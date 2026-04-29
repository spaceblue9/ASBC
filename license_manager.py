"""
ASBC Converter Pro — License Manager
Core license validation logic (embedded in compiled .exe)
"""

import hashlib
import hmac as _hmac
import os
import platform
import uuid

# ──────────────────────────────────────────────────────────────────────────────
# Secret key — obfuscated, embedded in compiled binary
# ⚠️  Must match _SK in keygen.py EXACTLY
# ──────────────────────────────────────────────────────────────────────────────
_P = ["ASBC", "P40x", "2025", "rK9n", "Wq7v", "mJ3z"]
_SK = "-".join(_P)


def get_machine_id() -> str:
    """Return a stable XXXX-XXXX-XXXX-XXXX fingerprint for this machine."""
    mac = uuid.getnode()
    host = platform.node().lower().strip()
    raw = f"{mac:012x}|{host}"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16].upper()
    return "-".join(digest[i : i + 4] for i in range(0, 16, 4))


def _expected_key(machine_id: str) -> str:
    """Compute the correct license key for a given machine ID."""
    mid = machine_id.replace("-", "").upper().encode("utf-8")
    h = _hmac.new(_SK.encode("utf-8"), mid, hashlib.sha256).hexdigest()[:20].upper()
    return "-".join(h[i : i + 5] for i in range(0, 20, 5))


def validate(machine_id: str, license_key: str) -> bool:
    """Constant-time key comparison (prevents timing attacks)."""
    a = license_key.replace("-", "").upper()
    b = _expected_key(machine_id).replace("-", "")
    return _hmac.compare_digest(a, b)


# ── License file storage ──────────────────────────────────────────────────────


def _dat_path() -> str:
    base = os.environ.get("APPDATA", os.path.expanduser("~"))
    folder = os.path.join(base, "ASBC_Pro")
    os.makedirs(folder, exist_ok=True)
    return os.path.join(folder, "license.dat")


def is_activated() -> bool:
    """Return True if a valid license for this machine is already saved."""
    try:
        with open(_dat_path(), "r", encoding="utf-8") as f:
            stored = f.read().strip()
        return validate(get_machine_id(), stored)
    except Exception:
        return False


def activate(license_key: str) -> bool:
    """Validate key against this machine. If valid, save and return True."""
    if not validate(get_machine_id(), license_key):
        return False
    try:
        with open(_dat_path(), "w", encoding="utf-8") as f:
            f.write(license_key.strip().upper())
        return True
    except Exception:
        return False
