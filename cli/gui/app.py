#!/usr/bin/env python3
"""Entry point for Vantage GUI."""

import sys
import os

from PyQt6.QtWidgets import QApplication, QMessageBox, QDialog
from PyQt6.QtGui import QIcon

from i18n import (
    tr, load_locale, save_locale, set_locale,
    load_theme, save_theme, is_first_run,
)
from gui.styles import detect_system_theme
from gui.service import VantageService
from gui.dialogs import LanguageDialog
from gui.main_window import VantageGUI


def main():
    os.environ.setdefault("QT_QPA_PLATFORM", "xcb")
    os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
    os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

    app = QApplication(sys.argv)
    app.setWindowIcon(
        QIcon("/usr/share/icons/hicolor/scalable/apps/vantage.png")
    )

    # ── First-run language selection ───────────────────────────────
    if is_first_run():
        detected = detect_system_theme()
        save_theme(detected)
        dlg = LanguageDialog()
        if dlg.exec() == QDialog.DialogCode.Accepted and dlg.chosen():
            save_locale(dlg.chosen())
            set_locale(dlg.chosen())
        else:
            save_locale("en")
            set_locale("en")
    else:
        set_locale(load_locale())

    # ── Connect to D-Bus service (limited mode if unavailable) ─────
    svc = VantageService()
    if svc.limited:
        QMessageBox.warning(None, tr("Service Error"), tr("Service Error"))

    gui = VantageGUI(svc)
    gui.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
