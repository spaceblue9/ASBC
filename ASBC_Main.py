import pandas as pd
import configparser
import os
import sys
import csv

class ASBCConverter:
    def __init__(self, config_path='ASBC-Config.ini'):
        self.config_path = config_path
        self.config = configparser.ConfigParser()
        if not os.path.exists(config_path):
            # สร้างไฟล์ Config เปล่าถ้ายังไม่มี
            with open(config_path, 'w', encoding='utf-8') as f:
                pass
        self.config.read(config_path, encoding='utf-8')
        self.original_columns = []
        
    def format_value(self, val):
        if val == "" or pd.isna(val):
            return ""
        if isinstance(val, float):
            if val.is_integer():
                return str(int(val))
            return str(val)
        return str(val)

    def load_input_data(self, task_config):
        file_path = task_config.get('file_path')
        if not file_path or not os.path.exists(file_path):
            return None
            
        sheet_name_raw = task_config.get('sheet_name', '0')
        try:
            sheet_name = int(sheet_name_raw)
        except ValueError:
            sheet_name = sheet_name_raw
        header_row = int(task_config.get('header_row', '0'))
        
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.xlsx':
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
            elif ext == '.xls':
                df = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row, engine='xlrd')
            else:
                df = pd.read_csv(file_path, header=header_row)
            
            self.original_columns = df.columns.tolist()
            df = df.astype(object).applymap(self.format_value)
            return df
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return None

    def read_template_file(self, path):
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            except:
                return ""
        return ""

    def save_output(self, content, processed_df, task_config):
        output_name = task_config.get('output_name')
        if not output_name: return
        
        encoding = task_config.get('encoding', 'utf-8')
        ext = os.path.splitext(output_name)[1].lower()
        
        try:
            os.makedirs(os.path.dirname(output_name), exist_ok=True)
            
            # บันทึกตาม Template เสมอ (เพื่อความถูกต้องตามที่ User ออกแบบ)
            # ยกเว้น JSON ที่อาจจะต้องการรูปแบบโครงสร้างข้อมูลแท้ๆ
            if ext == '.json' and not content.strip().startswith(('{', '[')):
                processed_df.to_json(output_name, orient='records', force_ascii=False, indent=4)
            else:
                with open(output_name, 'w', encoding=encoding, newline='') as f:
                    f.write(content)
            print(f"Successfully saved to: {output_name}")
        except Exception as e:
            print(f"Error saving {output_name}: {e}")

    def process_task(self, task_name, task_config):
        print(f"\n>>> Processing Task: {task_name}")
        df = self.load_input_data(task_config)
        if df is None: return
        
        melt_id_vars = task_config.get('melt_id_vars', '')
        if melt_id_vars:
            id_cols = [c.strip() for c in melt_id_vars.split(',')]
            existing_id_cols = [c for c in id_cols if c in df.columns]
            if existing_id_cols:
                value_vars = [col for col in self.original_columns if col not in existing_id_cols]
                df = df.melt(id_vars=existing_id_cols, value_vars=value_vars, var_name='Key', value_name='Value')
                if len(existing_id_cols) == 1:
                    df = df.rename(columns={existing_id_cols[0]: 'ID'})
                try:
                    df['sort_id'] = pd.to_numeric(df['ID'])
                    df = df.sort_values(by=['sort_id', 'ID']).drop(columns=['sort_id'])
                except:
                    df = df.sort_values(by=['ID'])

        header_tmpl = self.read_template_file(task_config.get('header_file'))
        body_tmpl = self.read_template_file(task_config.get('body_file'))
        footer_tmpl = self.read_template_file(task_config.get('footer_file'))
        
        result_rows = []
        for _, row in df.iterrows():
            line = body_tmpl
            for col in df.columns:
                val = str(row[col])
                if col in ['Key', 'Value'] and (',' in val or '\n' in val or '"' in val):
                    processed_val = '"' + val.replace('"', '""') + '"'
                else: processed_val = val
                line = line.replace("{{" + str(col) + "}}", processed_val)
                line = line.replace("{{" + str(col).lower() + "}}", processed_val)
                line = line.replace("{{" + str(col).upper() + "}}", processed_val)
            result_rows.append(line)
            
        final_output = header_tmpl + ("\n" if header_tmpl else "") + "\n".join(result_rows) + ("\n" if footer_tmpl else "") + footer_tmpl
        self.save_output(final_output, df, task_config)

    def run_all_tasks(self):
        for section in self.config.sections():
            if section.startswith('Task:'):
                self.process_task(section[5:], dict(self.config[section]))

    def validate_tasks(self):
        errors = []
        for section in self.config.sections():
            if section.startswith('Task:'):
                task_name = section[5:]
                conf = self.config[section]
                f_path = conf.get('file_path', '')
                if not f_path: errors.append(f"Task [{task_name}]: ไม่ได้ระบุไฟล์ต้นทาง")
                elif not os.path.exists(f_path): errors.append(f"Task [{task_name}]: ไม่พบไฟล์ต้นทาง -> {f_path}")
                b_file = conf.get('body_file', '')
                if not b_file: errors.append(f"Task [{task_name}]: ไม่ได้ระบุไฟล์เนื้อหา (Body)")
                elif not os.path.exists(b_file): errors.append(f"Task [{task_name}]: ไม่พบไฟล์เนื้อหา -> {b_file}")
                if not conf.get('output_name', ''): errors.append(f"Task [{task_name}]: ไม่ได้ระบุชื่อไฟล์ผลลัพธ์")
        return errors

if __name__ == "__main__":
    bot = ASBCConverter()
    bot.run_all_tasks()
