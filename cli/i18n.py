#!/usr/bin/env python3
"""Lightweight i18n infrastructure for Vantage GUI.

Supports English (en) and Russian (ru). The active locale is persisted
in ~/.config/vantage/settings.json and loaded at startup.

Usage:
    from i18n import tr, load_locale, save_locale, get_locale, set_locale
    load_locale()          # read saved language (or "en" fallback)
    label.setText(tr("Power Mode"))
"""

import json
import os
from pathlib import Path

_STRINGS_EN = {
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
    "Language subtitle": "Choose interface language.",
    "Theme": "Theme",
    "Theme subtitle": "Switch between dark and light appearance.",
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
    "Service Error": "Service Error",
    "Change Failed": "Change Failed",
    "TDP Error": "TDP Error",

    # ── Language dialog ────────────────────────────────────────────
    "Language dialog title": "Select Language",
    "Language dialog text": "Choose your preferred language for Vantage.",
    "English": "English",
    "Russian": "Русский",

    # ── Theme ──────────────────────────────────────────────────────
    "Dark Theme": "Dark Theme",
    "Light Theme": "Light Theme",
    "System Default": "System Default",
}

_STRINGS_RU = {
    # ── Sidebar / tabs ──────────────────────────────────────────────
    "Vantage": "Vantage",
    "Dashboard": "Обзор",
    "Power": "Питание",
    "Battery": "Батарея",
    "Actions": "Действия",
    "Settings": "Настройки",
    "About": "О программе",

    # ── Dashboard ──────────────────────────────────────────────────
    "Device subtitle fallback": "Неизвестное устройство Lenovo",
    "CPU": "ЦП",
    "GPU": "ГП",
    "Utilization": "Загрузка",
    "Temperature": "Температура",
    "Fan": "Вентилятор",
    "Quick Controls": "Быстрые настройки",
    "Power Mode": "Режим питания",
    "Power Mode subtitle": "Профиль производительности для ЦП и ГП.",
    "GPU Working Mode": "Режим работы ГП",
    "GPU Working Mode subtitle": "Выбор режима ГП (требует перезагрузки).",
    "Active Cooling Policy": "Политика охлаждения",
    "Active Cooling Policy subtitle": "Настройка кривой вентилятора.",

    # ── Power & System ─────────────────────────────────────────────
    "Power & System": "Питание и система",
    "Power Mode power subtitle": "Профиль производительности (также Fn+Q).",
    "Always on USB": "Постоянное USB",
    "Always on USB subtitle": "Зарядка USB при выключенном ноутбуке.",
    "Instant Boot": "Мгновенный запуск",
    "Instant Boot subtitle": "Включение при подключении зарядки.",
    "Flip To Start": "Запуск при открытии",
    "Flip To Start subtitle": "Включение при открытии крышки.",
    "Thermal / Fan Control": "Охлаждение и вентилятор",
    "Custom TDP (RyzenAdj)": "Пользовательский TDP (RyzenAdj)",
    "Custom TDP subtitle": "Переопределение лимитов мощности в мВт.",
    "Enable Override": "Включить переопределение",
    "Apply TDP": "Применить TDP",
    "Discrete GPU Toggle": "Дискретный ГП",
    "Discrete GPU Toggle subtitle": "Не поддерживается на этой архитектуре.",
    "GPU Overclock": "Разгон ГП",
    "GPU Overclock subtitle": "Отсутствует поддержка NVIDIA Coolbits.",
    "Resolution": "Разрешение",
    "Resolution subtitle": "Управляется ОС.",
    "Scaling (DPI)": "Масштаб (DPI)",
    "Scaling (DPI) subtitle": "Управляется ОС.",
    "Keyboard Backlight": "Подсветка клавиатуры",
    "Keyboard Backlight subtitle": "OpenRGB отсутствует или не поддерживается.",
    "Touchpad Toggle": "Тачпад",
    "Touchpad Toggle subtitle": "Управляется окружением рабочего стола ОС.",
    "Fn Lock": "Блокировка Fn",
    "Fn Lock subtitle": "Переключение медиа-клавиш и F1-F12.",
    "Windows Key Lock": "Блокировка клавиши Win",
    "Windows Key Lock subtitle": "Аппаратное сопоставление не найдено.",

    # ── Battery ────────────────────────────────────────────────────
    "Battery Details": "Сведения о батарее",
    "Battery Mode": "Режим батареи",
    "Conservation Mode": "Режим сохранения",
    "Conservation Mode subtitle": "Ограничивает заряд до 60-80% для продления срока службы.",
    "Statistics": "Статистика",
    "Battery %": "Заряд %",
    "Charging state": "Состояние зарядки",
    "Current capacity": "Текущая ёмкость",
    "Full capacity": "Полная ёмкость",
    "Design capacity": "Заводская ёмкость",
    "Health %": "Износ %",
    "Cycle count": "Циклов зарядки",

    # ── Actions ────────────────────────────────────────────────────
    "Actions & Automation": "Действия и автоматизация",
    "Actions info": "Движок автоматизации по событиям для профилей оборудования.\nПравила автоматизации планируются в будущем выпуске.",
    "Master Toggle": "Главный переключатель",
    "Master Toggle subtitle": "Правила автоматизации ещё не реализованы.",
    "Triggers & Actions": "Триггеры и действия",
    "Available Triggers": "Доступные триггеры",
    "Available Triggers subtitle": "Выбор условий срабатывания.",
    "Mapped Actions": "Назначенные действия",
    "Mapped Actions subtitle": "Определение поведения при срабатывании.",

    # ── Settings ───────────────────────────────────────────────────
    "General": "Общие",
    "Language": "Язык",
    "Language subtitle": "Выбор языка интерфейса.",
    "Theme": "Тема",
    "Theme subtitle": "Переключение между тёмной и светлой темой.",
    "Behavior": "Поведение",
    "Autorun": "Автозапуск",
    "Autorun subtitle": "Запуск вместе с системой.",
    "Boot Logo": "Логотип загрузки",
    "Boot Logo subtitle": "Логотип UEFI. Не реализовано.",

    # ── About ──────────────────────────────────────────────────────
    "About app title": "Lenovo Vantage Linux (неофициальный)",
    "About app desc": "Надёжный набор управления оборудованием для ноутбуков Lenovo на Linux.",
    "Version": "Версия",
    "Backend": "Бэкенд",
    "Dependencies": "Зависимости",

    # ── Changes bar ────────────────────────────────────────────────
    "Unsaved changes": "● Несохранённые изменения",
    "Apply Changes": "Применить",
    "Revert": "Отменить",

    # ── Status messages ────────────────────────────────────────────
    "Status ready": "Готово",
    "Status syncing": "Синхронизация...",
    "Status applied": "✓ Настройки применены к оборудованию.",
    "Status all applied": "✓ Все изменения применены.",
    "Status reverted": "Возврат к последнему сохранённому состоянию.",
    "Status tdp applied": "✓ Лимиты TDP применены.",

    # ── Dialogs ────────────────────────────────────────────────────
    "Service Error": "Ошибка службы",
    "Change Failed": "Ошибка изменения",
    "TDP Error": "Ошибка TDP",

    # ── Language dialog ────────────────────────────────────────────
    "Language dialog title": "Выберите язык",
    "Language dialog text": "Выберите предпочитаемый язык для Vantage.",
    "English": "English",
    "Russian": "Русский",

    # ── Theme ──────────────────────────────────────────────────────
    "Dark Theme": "Тёмная тема",
    "Light Theme": "Светлая тема",
    "System Default": "Системная",
}

_CONFIG_DIR = Path.home() / ".config" / "vantage"
_CONFIG_FILE = _CONFIG_DIR / "settings.json"

_locale = "en"


def set_locale(code: str) -> None:
    global _locale
    _locale = code


def get_locale() -> str:
    return _locale


def load_locale() -> str:
    """Read the saved language from the config file. Returns 'en' on fallback."""
    global _locale
    try:
        if _CONFIG_FILE.exists():
            data = json.loads(_CONFIG_FILE.read_text())
            lang = data.get("language", "en")
            if lang in ("en", "ru"):
                _locale = lang
                return lang
    except Exception:
        pass
    _locale = "en"
    return "en"


def save_locale(code: str) -> None:
    """Persist the chosen language code to the config file."""
    global _locale
    _locale = code
    try:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {}
        if _CONFIG_FILE.exists():
            data = json.loads(_CONFIG_FILE.read_text())
        data["language"] = code
        _CONFIG_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def load_theme() -> str:
    """Read the saved theme ('dark' or 'light') from config. Returns 'dark' on fallback."""
    try:
        if _CONFIG_FILE.exists():
            data = json.loads(_CONFIG_FILE.read_text())
            return data.get("theme", "dark")
    except Exception:
        pass
    return "dark"


def save_theme(theme: str) -> None:
    """Persist the chosen theme to the config file."""
    try:
        _CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        data = {}
        if _CONFIG_FILE.exists():
            data = json.loads(_CONFIG_FILE.read_text())
        data["theme"] = theme
        _CONFIG_FILE.write_text(json.dumps(data, indent=2))
    except Exception:
        pass


def is_first_run() -> bool:
    """Return True if no config file exists yet (language not chosen)."""
    return not _CONFIG_FILE.exists()


def tr(key: str) -> str:
    """Return the translated string for *key* in the current locale.

    Falls back to the English string, then to the key itself, so the UI
    never shows an empty label.
    """
    if _locale == "ru":
        return _STRINGS_RU.get(key, _STRINGS_EN.get(key, key))
    return _STRINGS_EN.get(key, key)
