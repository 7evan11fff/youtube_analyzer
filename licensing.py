"""
Offline algorithmic license key system with Free / Pro tiers.

Key format:  YTNA-XXXX-XXXX-XXXX-XX   (groups of 4-4-4-2 hex after prefix)
Breakdown:
  - 12 hex chars  = random payload
  - 2 chars       = tier code  (FR = Free, PR = Pro)
  - 6 hex chars   = truncated HMAC-SHA256(payload + tier, SECRET)

Keys are validated entirely offline — no server needed.
Only someone who knows _SECRET_SALT can generate valid keys.
"""

import hashlib
import hmac
import json
import logging
import os
import secrets
from pathlib import Path
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)

# ── secret salt (change this to your own value to make keys unique to you) ──
_SECRET_SALT = b"ytnA_2026_s3cr3t_k3y_salt_!@#xZ9"

# ── tier constants ──────────────────────────────────────────────────
TIER_NONE = "none"
TIER_FREE = "free"
TIER_PRO  = "pro"

_TIER_CODES = {"FR": TIER_FREE, "PR": TIER_PRO}
_CODE_FOR_TIER = {TIER_FREE: "FR", TIER_PRO: "PR"}

# ── feature limits per tier ─────────────────────────────────────────
TIER_LIMITS: Dict[str, Dict[str, Any]] = {
    TIER_NONE: {
        "max_videos": 50,
        "json_export": False,
        "csv_export": False,
        "dashboard": False,
        "trends": False,
        "auto_scrape": False,
        "correlations": False,
        "markdown_export": True,
    },
    TIER_FREE: {
        "max_videos": 100,
        "json_export": True,
        "csv_export": True,
        "dashboard": True,
        "trends": False,
        "auto_scrape": False,
        "correlations": True,
        "markdown_export": True,
    },
    TIER_PRO: {
        "max_videos": 300,
        "json_export": True,
        "csv_export": True,
        "dashboard": True,
        "trends": True,
        "auto_scrape": True,
        "correlations": True,
        "markdown_export": True,
    },
}

LICENSE_PATH = Path("data/license.json")


# ── key generation ──────────────────────────────────────────────────
def generate_key(tier: str) -> str:
    """Generate a valid license key for the given tier."""
    code = _CODE_FOR_TIER.get(tier)
    if not code:
        raise ValueError(f"Unknown tier: {tier}. Use 'free' or 'pro'.")

    payload = secrets.token_hex(6).upper()  # 12 hex chars
    sig = _sign(payload, code)
    raw = f"{payload}{code}{sig}"  # 20 chars total
    return f"YTNA-{raw[0:4]}-{raw[4:8]}-{raw[8:12]}-{raw[12:16]}-{raw[16:20]}"


def _sign(payload: str, tier_code: str) -> str:
    """Produce the 6-char HMAC signature for a payload + tier code."""
    msg = f"{payload}{tier_code}".encode()
    h = hmac.new(_SECRET_SALT, msg, hashlib.sha256).hexdigest().upper()
    return h[:6]


# ── key validation ──────────────────────────────────────────────────
def validate_key(key: str) -> Optional[str]:
    """
    Validate a license key and return the tier string, or None if invalid.
    Accepts keys with or without the YTNA- prefix and dashes.
    """
    clean = key.strip().upper().replace("-", "").replace(" ", "")

    if clean.startswith("YTNA"):
        clean = clean[4:]

    if len(clean) != 20:
        return None

    payload = clean[:12]
    tier_code = clean[12:14]
    provided_sig = clean[14:20]

    if tier_code not in _TIER_CODES:
        return None

    expected_sig = _sign(payload, tier_code)
    if not hmac.compare_digest(provided_sig, expected_sig):
        return None

    return _TIER_CODES[tier_code]


# ── license file persistence ────────────────────────────────────────
def _read_license_file() -> Dict[str, Any]:
    try:
        if LICENSE_PATH.exists():
            return json.loads(LICENSE_PATH.read_text())
    except Exception as e:
        logger.warning(f"Could not read license file: {e}")
    return {}


def _write_license_file(data: Dict[str, Any]):
    LICENSE_PATH.parent.mkdir(parents=True, exist_ok=True)
    LICENSE_PATH.write_text(json.dumps(data, indent=2))


def activate_key(key: str) -> Optional[str]:
    """Validate key, persist it, and return the tier (or None)."""
    tier = validate_key(key)
    if tier is None:
        return None
    data = _read_license_file()
    data["key"] = key.strip().upper()
    data["tier"] = tier
    _write_license_file(data)
    logger.info(f"License activated: {tier}")
    return tier


def deactivate_key():
    """Remove stored license."""
    data = _read_license_file()
    data.pop("key", None)
    data.pop("tier", None)
    _write_license_file(data)


def get_current_tier() -> str:
    """Return the currently active tier from the stored license."""
    data = _read_license_file()
    stored_key = data.get("key")
    if stored_key:
        tier = validate_key(stored_key)
        if tier:
            return tier
    return TIER_NONE


def get_stored_key() -> Optional[str]:
    """Return the raw stored key, or None."""
    data = _read_license_file()
    return data.get("key")


def get_limits(tier: str = None) -> Dict[str, Any]:
    """Return the feature limits for a tier (defaults to current)."""
    if tier is None:
        tier = get_current_tier()
    return TIER_LIMITS.get(tier, TIER_LIMITS[TIER_NONE])


def is_feature_unlocked(feature: str, tier: str = None) -> bool:
    """Check if a specific feature is unlocked for the given tier."""
    limits = get_limits(tier)
    return bool(limits.get(feature, False))


def get_max_videos(tier: str = None) -> int:
    """Return the max video count allowed for the tier."""
    return get_limits(tier).get("max_videos", 15)


# ── onboarding flag ─────────────────────────────────────────────────
def is_onboarding_complete() -> bool:
    return _read_license_file().get("onboarding_complete", False)


def set_onboarding_complete(done: bool = True):
    data = _read_license_file()
    data["onboarding_complete"] = done
    _write_license_file(data)
