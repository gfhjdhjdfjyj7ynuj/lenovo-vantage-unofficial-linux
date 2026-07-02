#!/usr/bin/env python3
"""Lightweight i18n infrastructure for Vantage GUI.

Centralizes all user-facing strings so they can later be swapped for a
real translation backend (gettext / Qt linguist) without touching UI code.

Usage:
    from i18n import tr
    label.setText(tr("Power Mode"))
"""

_STRINGS = {
    # ── Sidebar / tabs ──────────────────────────────────────────────
    "Vantage": "Vantage",
    "Dashboard": "Dashboard",
    "Power": "Power",
    "Battery": "Battery",
    "Actions": "Actions",
    "Settings": "Settings",
    "About": "About",

    # ── Dashboard ──────────────────────────────────────────────────
    "Device subtitle fallback": "Unknown Lenovo Device",
    "CPU": "CPU",
    "GPU": "GPU",
    "Utilization": "Utilization",
    "Temperature": "Temperature",
    "Fan": "Fan",
    "Quick Controls": "Quick Controls",
    "Power Mode": "Power Mode",
    "Power Mode subtitle": "Performance profile for CPU & GPU.",
    "GPU Working Mode": "GPU Working Mode",
    "GPU Working Mode subtitle": "Select GPU mode (requires restart).",
    "Active Cooling Policy": "Active Cooling Policy",
    "Active Cooling Policy subtitle": "Set EC fan curve behavior.",

    # ── Power & System ─────────────────────────────────────────────
    "Power & System": "Power & System",
    "Power Mode power subtitle": "Performance profile (also Fn+Q).",
    "Always on USB": "Always on USB",
    "Always on USB subtitle": "Charge USB when laptop is off.",
    "Instant Boot": "Instant Boot",
    "Instant Boot subtitle": "Power on when charger connects.",
    "Flip To Start": "Flip To Start",
    "Flip To Start subtitle": "Power on when lid is opened.",
    "Thermal / Fan Control": "Thermal / Fan Control",
    "Custom TDP (RyzenAdj)": "Custom TDP (RyzenAdj)",
    "Custom TDP subtitle": "Override hardware power limits in mW.",
    "Enable Override": "Enable Override",
    "Apply TDP": "Apply TDP",
    "Discrete GPU Toggle": "Discrete GPU Toggle",
    "Discrete GPU Toggle subtitle": "Unsupported on this architecture.",
    "GPU Overclock": "GPU Overclock",
    "GPU Overclock subtitle": "Missing NVIDIA Coolbits support.",
    "Resolution": "Resolution",
    "Resolution subtitle": "Managed by OS.",
    "Scaling (DPI)": "Scaling (DPI)",
    "Scaling (DPI) subtitle": "Managed by OS.",
    "Keyboard Backlight": "Keyboard Backlight",
    "Keyboard Backlight subtitle": "OpenRGB missing or unsupported.",
    "Touchpad Toggle": "Touchpad Toggle",
    "Touchpad Toggle subtitle": "Managed by OS desktop environment.",
    "Fn Lock": "Fn Lock",
    "Fn Lock subtitle": "Toggle media keys vs F1-F12.",
    "Windows Key Lock": "Windows Key Lock",
    "Windows Key Lock subtitle": "Hardware mapping not found.",

    # ── Battery ────────────────────────────────────────────────────
    "Battery Details": "Battery Details",
    "Battery Mode": "Battery Mode",
    "Conservation Mode": "Conservation Mode",
    "Conservation Mode subtitle": "Limits charge to 60-80% to extend battery lifespan.",
    "Statistics": "Statistics",
    "Battery %": "Battery %",
    "Charging state": "Charging state",
    "Current capacity": "Current capacity",
    "Full capacity": "Full capacity",
    "Design capacity": "Design capacity",
    "Health %": "Health %",
    "Cycle count": "Cycle count",

    # ── Actions ────────────────────────────────────────────────────
    "Actions & Automation": "Actions & Automation",
    "Actions info": "Event-driven automation engine for hardware profiles.\nAutomation rules are planned for a future release. Stay tuned.",
    "Master Toggle": "Master Toggle",
    "Master Toggle subtitle": "Automation rules not yet implemented.",
    "Triggers & Actions": "Triggers & Actions",
    "Available Triggers": "Available Triggers",
    "Available Triggers subtitle": "Select trigger conditions.",
    "Mapped Actions": "Mapped Actions",
    "Mapped Actions subtitle": "Define behavior upon trigger.",

    # ── Settings ───────────────────────────────────────────────────
    "General": "General",
    "Language": "Language",
    "Language subtitle": "Not yet implemented.",
    "Theme": "Theme",
    "Theme subtitle": "Not yet implemented.",
    "Behavior": "Behavior",
    "Autorun": "Autorun",
    "Autorun subtitle": "Start with system.",
    "Boot Logo": "Boot Logo",
    "Boot Logo subtitle": "UEFI boot logo. Not implemented.",

    # ── About ──────────────────────────────────────────────────────
    "About app title": "Lenovo Vantage Linux Unofficial",
    "About app desc": "A robust, native hardware control suite built for Lenovo laptops running on Linux.",
    "Version": "Version",
    "Backend": "Backend",
    "Dependencies": "Dependencies",

    # ── Changes bar ────────────────────────────────────────────────
    "Unsaved changes": "● Unsaved changes",
    "Apply Changes": "Apply Changes",
    "Revert": "Revert",

    # ── Status messages ────────────────────────────────────────────
    "Status ready": "Ready",
    "Status syncing": "Syncing...",
    "Status applied": "✓ Settings applied to hardware.",
    "Status all applied": "✓ All changes applied.",
    "Status reverted": "Reverted to last saved state.",
    "Status tdp applied": "✓ TDP limits applied.",

    # ── Dialogs ────────────────────────────────────────────────────
    "Daemon Error": "Daemon Error",
    "Change Failed": "Change Failed",
    "TDP Error": "TDP Error",
}

_locale = "en"


def set_locale(code: str) -> None:
    global _locale
    _locale = code


def get_locale() -> str:
    return _locale


def tr(key: str) -> str:
    """Return the translated string for *key*.

    Falls back to the key itself (which doubles as the English string)
    so the UI never shows an empty label.
    """
    return _STRINGS.get(key, key)
