import configparser
import csv
import os
import re
import sys
import warnings

import pandas as pd


class ASBCConverter:
    def __init__(self, config_path="ASBC-Config.ini"):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_path):
            # สร้างไฟล์ Config เปล่าถ้ายังไม่มี
            with open(config_path, "w", encoding="utf-8") as f:
                pass
        self.config.read(config_path, encoding="utf-8")
        self.original_columns = []

    def format_value(self, val):
        if val == "" or pd.isna(val):
            return ""
        if isinstance(val, float):
            if val.is_integer():
                return str(int(val))
            return str(val)
        return str(val)

    def apply_filters(self, df, filter_rules_str):
        if not filter_rules_str or not filter_rules_str.strip():
            return df

        rules = [r.strip() for r in filter_rules_str.split(";") if r.strip()]
        if not rules:
            return df

        mask = pd.Series([True] * len(df), index=df.index)

        for rule in rules:
            parts = rule.split(":", 2)
            if len(parts) != 3:
                print(f"Warning: Invalid filter rule -> {rule}")
                continue

            field, op, value = parts[0].strip(), parts[1].strip().lower(), parts[2].strip()

            if field not in df.columns:
                print(f"Warning: Filter field '{field}' not found in data")
                continue

            col = df[field].astype(str).str.strip()

            if op in ("equals", "eq"):
                rule_mask = col.str.lower() == value.lower()
            elif op in ("not_equals", "neq"):
                rule_mask = col.str.lower() != value.lower()
            elif op == "contains":
                rule_mask = col.str.contains(value, case=False, na=False)
            elif op == "not_contains":
                rule_mask = ~col.str.contains(value, case=False, na=False)
            elif op in ("starts_with", "sw"):
                rule_mask = col.str.lower().str.startswith(value.lower())
            elif op in ("ends_with", "ew"):
                rule_mask = col.str.lower().str.endswith(value.lower())
            elif op in ("greater", "gt"):
                try:
                    rule_mask = pd.to_numeric(col, errors="coerce") > float(value)
                except:
                    rule_mask = col > value
            elif op in ("less", "lt"):
                try:
                    rule_mask = pd.to_numeric(col, errors="coerce") < float(value)
                except:
                    rule_mask = col < value
            elif op == "in":
                values = [v.strip().lower() for v in value.split(",")]
                rule_mask = col.str.lower().isin(values)
            else:
                print(f"Warning: Unknown filter operator -> {op}")
                continue

            mask = mask & rule_mask

        filtered_count = mask.sum()
        total_count = len(df)
        if filtered_count < total_count:
            print(f"  Filter: {total_count} rows -> {filtered_count} rows ({total_count - filtered_count} filtered out)")
        else:
            print(f"  Filter: {total_count} rows (no change)")

        return df[mask].reset_index(drop=True)

    def load_input_data(self, task_config):
        file_path = task_config.get("file_path")
        if not file_path or not os.path.exists(file_path):
            return None

        sheet_name_raw = task_config.get("sheet_name", "0")
        try:
            sheet_name = int(sheet_name_raw)
        except ValueError:
            sheet_name = sheet_name_raw
        header_row = int(task_config.get("header_row", "0"))

        try:
            ext = os.path.splitext(file_path)[1].lower()
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")  # suppress openpyxl warnings
                if ext == ".xlsx":
                    df = pd.read_excel(
                        file_path, sheet_name=sheet_name, header=header_row
                    )
                elif ext == ".xls":
                    df = pd.read_excel(
                        file_path,
                        sheet_name=sheet_name,
                        header=header_row,
                        engine="xlrd",
                    )
                else:
                    df = pd.read_csv(file_path, header=header_row)

            self.original_columns = df.columns.tolist()
            df = df.astype(object).map(self.format_value)
            return df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def read_template_file(self, path):
        if path and os.path.exists(path):
            try:
                with open(path, "r", encoding="utf-8") as f:
                    return f.read().strip()
            except:
                return ""
        return ""

    def save_output(self, content, processed_df, task_config):
        output_name = task_config.get("output_name")
        if not output_name:
            return

        encoding = task_config.get("encoding", "utf-8")
        ext = os.path.splitext(output_name)[1].lower()

        try:
            os.makedirs(os.path.dirname(output_name), exist_ok=True)

            # บันทึกตาม Template เสมอ (เพื่อความถูกต้องตามที่ User ออกแบบ)
            # ยกเว้น JSON ที่อาจจะต้องการรูปแบบโครงสร้างข้อมูลแท้ๆ
            if ext == ".json" and not content.strip().startswith(("{", "[")):
                processed_df.to_json(
                    output_name, orient="records", force_ascii=False, indent=4
                )
            else:
                with open(output_name, "w", encoding=encoding, newline="") as f:
                    f.write(content)
            print(f"Successfully saved to: {output_name}")
        except Exception as e:
            print(f"Error saving {output_name}: {e}")

    def process_task(self, task_name, task_config):
        print(f"\n>>> Processing Task: {task_name}")
        df = self.load_input_data(task_config)
        if df is None:
            return

        filter_rules = task_config.get("filter_rules", "")
        df = self.apply_filters(df, filter_rules)

        if df.empty:
            print(f"  No data after filtering. Skipping task.")
            return

        melt_id_vars = task_config.get("melt_id_vars", "")
        if melt_id_vars:
            id_cols = [c.strip() for c in melt_id_vars.split(",")]
            existing_id_cols = [c for c in id_cols if c in df.columns]
            if existing_id_cols:
                value_vars = [
                    col for col in self.original_columns if col not in existing_id_cols
                ]
                df = df.melt(
                    id_vars=existing_id_cols,
                    value_vars=value_vars,
                    var_name="Key",
                    value_name="Value",
                )
                if len(existing_id_cols) == 1:
                    df = df.rename(columns={existing_id_cols[0]: "ID"})
                try:
                    df["sort_id"] = pd.to_numeric(df["ID"])
                    df = df.sort_values(by=["sort_id", "ID"]).drop(columns=["sort_id"])
                except:
                    df = df.sort_values(by=["ID"])

        un_melt_cols = task_config.get("un_melt_columns", "")
        if un_melt_cols:
            cols = [c.strip() for c in un_melt_cols.split(",")]
            if len(cols) == 3:
                id_col, key_col, value_col = cols
                if id_col in df.columns and key_col in df.columns and value_col in df.columns:
                    df = df.pivot(index=id_col, columns=key_col, values=value_col)
                    df = df.reset_index()
                    df.columns.name = None
                    df = df.astype(object).map(self.format_value)
                else:
                    print(f"Warning: Un-Transpose columns not found -> {un_melt_cols}")

        header_tmpl = self.read_template_file(task_config.get("header_file"))
        body_tmpl = self.read_template_file(task_config.get("body_file"))
        footer_tmpl = self.read_template_file(task_config.get("footer_file"))

        result_rows = []
        for _, row in df.iterrows():
            line = body_tmpl
            for col in df.columns:
                val = str(row[col])
                if col in ["Key", "Value"] and (
                    "," in val or "\n" in val or '"' in val
                ):
                    processed_val = '"' + val.replace('"', '""') + '"'
                else:
                    processed_val = val
                col_norm = str(col).strip()
                # Support {{CI Name}}, {{ CI Name }}, {{ci name}}, {{CI NAME}}
                pattern = r"\{\{\s*" + re.escape(col_norm) + r"\s*\}\}"
                line = re.sub(pattern, processed_val, line, flags=re.IGNORECASE)
            result_rows.append(line)

        final_output = (
            header_tmpl
            + ("\n" if header_tmpl else "")
            + "\n".join(result_rows)
            + ("\n" if footer_tmpl else "")
            + footer_tmpl
        )
        self.save_output(final_output, df, task_config)

    def run_all_tasks(self):
        for section in self.config.sections():
            if section.startswith("Task:"):
                self.process_task(section[5:], dict(self.config[section]))

    def validate_tasks(self):
        errors = []
        for section in self.config.sections():
            if section.startswith("Task:"):
                task_name = section[5:]
                conf = self.config[section]
                f_path = conf.get("file_path", "")
                if not f_path:
                    errors.append(f"Task [{task_name}]: ไม่ได้ระบุไฟล์ต้นทาง")
                elif not os.path.exists(f_path):
                    errors.append(f"Task [{task_name}]: ไม่พบไฟล์ต้นทาง -> {f_path}")
                b_file = conf.get("body_file", "")
                if not b_file:
                    errors.append(f"Task [{task_name}]: ไม่ได้ระบุไฟล์เนื้อหา (Body)")
                elif not os.path.exists(b_file):
                    errors.append(f"Task [{task_name}]: ไม่พบไฟล์เนื้อหา -> {b_file}")
                if not conf.get("output_name", ""):
                    errors.append(f"Task [{task_name}]: ไม่ได้ระบุชื่อไฟล์ผลลัพธ์")
        return errors


if __name__ == "__main__":
    bot = ASBCConverter()
    bot.run_all_tasks()
