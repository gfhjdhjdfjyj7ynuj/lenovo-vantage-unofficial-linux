"""Main window for Vantage GUI — sidebar, page stack, changes bar, logic."""

import os

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QFrame, QStackedWidget, QButtonGroup, QMessageBox, QScrollArea,
)
from PyQt6.QtGui import QIcon, QShortcut, QKeySequence
from PyQt6.QtCore import QTimer, Qt

from i18n import tr, load_theme, save_theme
from gui.styles import DARK_STYLESHEET, LIGHT_STYLESHEET
from gui.widgets import set_row_state
from gui.pages.dashboard import create_dashboard_page, get_laptop_model
from gui.pages.power import create_power_page
from gui.pages.battery import create_battery_page
from gui.pages.actions import create_actions_page
from gui.pages.settings import create_settings_page
from gui.pages.about import create_about_page


def get_battery_info():
    info = {
        "percent": "N/A", "status": "N/A", "health": "N/A",
        "cycles": "N/A", "current": "N/A", "full": "N/A", "design": "N/A",
    }
    for bat in os.listdir("/sys/class/power_supply/"):
        if bat.startswith("BAT"):
            path = f"/sys/class/power_supply/{bat}"
            try:
                if os.path.exists(f"{path}/capacity"):
                    info["percent"] = open(f"{path}/capacity").read().strip()
                if os.path.exists(f"{path}/status"):
                    info["status"] = open(f"{path}/status").read().strip()

                en_now = "energy_now" if os.path.exists(f"{path}/energy_now") else "charge_now"
                en_full = "energy_full" if os.path.exists(f"{path}/energy_full") else "charge_full"
                en_des = "energy_full_design" if os.path.exists(f"{path}/energy_full_design") else "charge_full_design"

                if os.path.exists(f"{path}/{en_now}"):
                    info["current"] = open(f"{path}/{en_now}").read().strip()
                if os.path.exists(f"{path}/{en_full}"):
                    info["full"] = open(f"{path}/{en_full}").read().strip()
                if os.path.exists(f"{path}/{en_des}"):
                    info["design"] = open(f"{path}/{en_des}").read().strip()
                if os.path.exists(f"{path}/cycle_count"):
                    info["cycles"] = open(f"{path}/cycle_count").read().strip()

                if info["full"] != "N/A" and info["design"] != "N/A":
                    info["health"] = f"{(float(info['full']) / float(info['design'])) * 100:.1f}%"
            except Exception:
                pass
            break
    return info


class VantageGUI(QMainWindow):
    def __init__(self, svc):
        super().__init__()
        self.svc = svc
        self.setWindowTitle("Lenovo Vantage Linux Unofficial")
        self.resize(1000, 750)
        self.setMinimumSize(900, 600)

        # ── Theme ─────────────────────────────────────────────────────
        self.current_theme = load_theme()
        self.statusBar().showMessage(tr("Status ready"), 3000)

        # If service is in limited mode, show a warning
        if svc.limited:
            self.statusBar().showMessage(tr("Service Error"), 0)

        # ── UI tracking ───────────────────────────────────────────────
        self.pm_combos = []
        self.gpu_combos = []
        self.fan_combos = []
        self.bat_combos = []
        self.usb_combos = []
        self.ib_combos = []
        self.fs_combos = []
        self.fn_combos = []
        self.tdp_spins = []
        self.rows = {}
        self._pending = False
        self.tdp_enabled = False

        # ── Main layout ───────────────────────────────────────────────
        main_widget = QWidget()
        main_widget.setObjectName("MainWidget")
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        self.setCentralWidget(main_widget)

        # ── Sidebar ───────────────────────────────────────────────────
        self.sidebar = QWidget()
        self.sidebar.setObjectName("Sidebar")
        self.sidebar.setFixedWidth(220)
        side_layout = QVBoxLayout(self.sidebar)
        side_layout.setContentsMargins(0, 20, 0, 20)
        side_layout.setSpacing(5)

        title_lbl = QLabel(" Vantage")
        title_lbl.setStyleSheet(
            "font-size: 18px; font-weight: bold; color: white; "
            "margin-left: 15px; margin-bottom: 20px;"
        )
        side_layout.addWidget(title_lbl)

        self.nav_btns = []
        self.btn_group = QButtonGroup(self)
        self.btn_group.setExclusive(True)

        tabs = [
            tr("Dashboard"), tr("Power"), tr("Battery"),
            tr("Actions"), tr("Settings"), tr("About"),
        ]
        for idx, t in enumerate(tabs):
            if t == tr("About"):
                side_layout.addStretch()
                divider = QFrame()
                divider.setObjectName("SidebarDivider")
                divider.setFrameShape(QFrame.Shape.HLine)
                side_layout.addWidget(divider)

            btn = QPushButton(t)
            btn.setProperty("class", "SidebarBtn")
            btn.setCheckable(True)
            self.btn_group.addButton(btn, idx)
            btn.clicked.connect(lambda checked, i=idx: self.switch_tab(i))
            side_layout.addWidget(btn)
            self.nav_btns.append(btn)

        for i in range(len(tabs)):
            QShortcut(QKeySequence(f"Ctrl+{i+1}"), self).activated.connect(
                lambda idx=i: self.switch_tab(idx)
            )

        main_layout.addWidget(self.sidebar)

        # ── Right panel ───────────────────────────────────────────────
        right_widget = QWidget()
        right_widget.setObjectName("MainWidget")
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        # Changes bar
        self.changes_bar = QFrame()
        self.changes_bar.setObjectName("ChangesBar")
        self.changes_bar.setFixedHeight(50)
        self.changes_bar.setVisible(False)
        bar_h = QHBoxLayout(self.changes_bar)
        bar_h.setContentsMargins(24, 0, 24, 0)
        bar_h.setSpacing(12)

        lbl_pending = QLabel(tr("Unsaved changes"))
        lbl_pending.setObjectName("ChangesLabel")
        bar_h.addWidget(lbl_pending)
        bar_h.addStretch()

        btn_apply_all = QPushButton(tr("Apply Changes"))
        btn_apply_all.setObjectName("ApplyAllBtn")
        btn_apply_all.clicked.connect(self.apply_all)
        bar_h.addWidget(btn_apply_all)

        btn_revert = QPushButton(tr("Revert"))
        btn_revert.setObjectName("RevertBtn")
        btn_revert.clicked.connect(self.revert_all)
        bar_h.addWidget(btn_revert)

        right_layout.addWidget(self.changes_bar)

        # Theme toggle button
        self.theme_btn = QPushButton(tr("Light Theme"))
        self.theme_btn.setObjectName("ThemeBtn")
        self.theme_btn.setFixedHeight(36)
        self.theme_btn.clicked.connect(self.toggle_theme)
        right_layout.addWidget(
            self.theme_btn,
            alignment=Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop,
        )

        # Stacked pages
        self.stack = QStackedWidget()
        right_layout.addWidget(self.stack)
        main_layout.addWidget(right_widget)

        self.stack.addWidget(create_dashboard_page(self))
        self.stack.addWidget(create_power_page(self))
        self.stack.addWidget(create_battery_page(self))
        self.stack.addWidget(create_actions_page(self))
        self.stack.addWidget(create_settings_page(self))
        self.stack.addWidget(create_about_page(self))

        self.switch_tab(0)
        self._apply_theme(self.current_theme)
        self.load_state()

        # Sensor timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_sensors)
        self.timer.start(2000)
        self.update_sensors()

    # ── Navigation ────────────────────────────────────────────────────
    def switch_tab(self, idx):
        self.nav_btns[idx].setChecked(True)
        self.stack.setCurrentIndex(idx)

    # ── TDP ───────────────────────────────────────────────────────────
    def _on_tdp_toggle(self, checked):
        for spin in self.tdp_spins:
            spin.setEnabled(checked)
        self.btn_apply_tdp.setEnabled(checked)
        if checked:
            self._mark_pending()
        else:
            self._clear_pending()

    def _on_tdp_spin_change(self):
        if self.tdp_check.isChecked():
            self._mark_pending()

    # ── Pending changes bar ───────────────────────────────────────────
    def _mark_pending(self):
        self._pending = True
        self.changes_bar.setVisible(True)

    def _clear_pending(self):
        self._pending = False
        self.changes_bar.setVisible(False)

    def apply_all(self):
        if self.tdp_check.isChecked():
            self.apply_tdp()
        self._clear_pending()
        self.statusBar().showMessage(tr("Status all applied"), 3000)

    def revert_all(self):
        self.load_state()
        if hasattr(self, 'tdp_check'):
            self.tdp_check.setChecked(False)
        self._clear_pending()
        self.statusBar().showMessage(tr("Status reverted"), 2000)

    # ── Theme ─────────────────────────────────────────────────────────
    def _apply_theme(self, theme: str):
        if theme == "light":
            self.setStyleSheet(LIGHT_STYLESHEET)
            self.theme_btn.setText(tr("Dark Theme"))
        else:
            self.setStyleSheet(DARK_STYLESHEET)
            self.theme_btn.setText(tr("Light Theme"))

    def toggle_theme(self):
        if self.current_theme == "dark":
            self.current_theme = "light"
        else:
            self.current_theme = "dark"
        self._apply_theme(self.current_theme)
        save_theme(self.current_theme)

    # ── Hardware apply ─────────────────────────────────────────────────
    def auto_apply_change(self):
        sender = self.sender()
        if not sender or not sender.isEnabled():
            return
        if self.svc.limited:
            QMessageBox.warning(
                self, tr("Service Error"),
                tr("Service Error"),
            )
            return

        self.statusBar().showMessage(tr("Status syncing"), 1000)
        errors = []
        try:
            if sender in self.pm_combos:
                pm = "balanced" if sender.currentText() == "Balance" else sender.currentText().lower()
                self.svc.iface.SetPowerMode(pm)
            elif sender in self.bat_combos:
                self.svc.iface.SetConservation(sender.currentText() == "Conservation")
            elif sender in self.usb_combos:
                self.svc.iface.SetUsbCharging(sender.currentText() == "On")
            elif sender in self.ib_combos:
                self.svc.iface.SetInstantBoot(sender.currentText() == "On")
            elif sender in self.fs_combos:
                self.svc.iface.SetFlipToStart(sender.currentText() == "On")
            elif sender in self.gpu_combos:
                self.svc.iface.SetDgpuMode(sender.currentText().lower())
            elif sender in self.fan_combos:
                fm = sender.currentText().lower().replace(" ", "_")
                self.svc.iface.SetFanMode(fm)
            elif sender in self.fn_combos:
                self.svc.iface.SetFnLock(sender.currentText() == "On")
        except Exception as e:
            errors.append(str(e))
            self._mark_pending()

        if errors:
            QMessageBox.warning(self, tr("Change Failed"), "\n".join(errors))
        else:
            self.statusBar().showMessage(tr("Status applied"), 2000)
            self._clear_pending()

        self.load_state()

    def apply_tdp(self):
        if self.svc.limited:
            return
        try:
            self.svc.iface.SetRyzenTdp(
                self.tdp_spins[0].value(),
                self.tdp_spins[1].value(),
                self.tdp_spins[2].value(),
            )
            self.statusBar().showMessage(tr("Status tdp applied"), 2000)
            self._clear_pending()
        except Exception as e:
            QMessageBox.warning(self, tr("TDP Error"), str(e))

    # ── Capability engine ─────────────────────────────────────────────
    def apply_cap(self, widget, cap_dict, partial_warning=""):
        if not isinstance(cap_dict, dict) or not widget:
            return
        if not cap_dict:
            return

        supported = cap_dict.get("supported", False)
        partial = cap_dict.get("partial", False)
        reason = cap_dict.get("reason", "Not supported by hardware.")

        sub_lbl = None
        for child in widget.findChildren(QLabel):
            if child.objectName() == "RowSubtitle":
                sub_lbl = child

        if not supported:
            set_row_state(widget, False)
            if sub_lbl and reason:
                sub_lbl.setText(reason)
        elif partial:
            set_row_state(widget, True)
            if sub_lbl and partial_warning:
                sub_lbl.setText(sub_lbl.text() + f" ({partial_warning})")
        else:
            set_row_state(widget, True)

    # ── Load hardware state ───────────────────────────────────────────
    def load_state(self):
        current = self.stack.currentWidget()
        scroll = current.findChild(QScrollArea) if current else None
        scroll_val = scroll.verticalScrollBar().value() if scroll else 0

        if self.svc.limited:
            return

        try:
            raw_caps = self.svc.iface.GetAllCapabilities()
            caps = {}
            for k, v in raw_caps.items():
                try:
                    caps[str(k)] = {
                        str(ik): (bool(iv) if ik in ['supported', 'partial'] else str(iv))
                        for ik, iv in v.items()
                    }
                except Exception:
                    pass

            self.apply_cap(self.rows.get('power_dash'), caps.get("power", {}))
            self.apply_cap(self.rows.get('power_main'), caps.get("power", {}))
            self.apply_cap(self.rows.get('battery'), caps.get("battery", {}))

            sys_cap = caps.get("system", {})
            self.apply_cap(self.rows.get('fn'), sys_cap)
            self.apply_cap(self.rows.get('ib'), sys_cap)
            self.apply_cap(self.rows.get('fs'), sys_cap)
            self.apply_cap(self.rows.get('usb'), sys_cap)

            self.apply_cap(self.rows.get('gpu_dash'), caps.get("gpu", {}))
            self.apply_cap(self.rows.get('gpu_main'), caps.get("gpu", {}))

            self.apply_cap(self.rows.get('fan_dash'), caps.get("fan", {}))
            self.apply_cap(self.rows.get('fan_main'), caps.get("fan", {}))

            self.apply_cap(self.rows.get('tdp'), caps.get("ryzenadj", {}), "Missing ryzenadj binary.")
        except Exception:
            pass

        def _sync(combos, val):
            for c in combos:
                c.blockSignals(True)
                c.setCurrentText(val)
                c.blockSignals(False)

        try:
            pm = str(self.svc.iface.GetPowerMode()).lower()
            _sync(self.pm_combos, "Quiet" if "quiet" in pm else "Performance" if "performance" in pm else "Balance")
        except Exception:
            pass
        try:
            _sync(self.bat_combos, "Conservation" if bool(self.svc.iface.GetConservation()) else "Normal")
        except Exception:
            pass
        try:
            _sync(self.usb_combos, "On" if bool(self.svc.iface.GetUsbCharging()) else "Off")
        except Exception:
            pass
        try:
            _sync(self.fn_combos, "On" if bool(self.svc.iface.GetFnLock()) else "Off")
        except Exception:
            pass
        try:
            _sync(self.ib_combos, "On" if bool(self.svc.iface.GetInstantBoot()) else "Off")
        except Exception:
            pass
        try:
            _sync(self.fs_combos, "On" if bool(self.svc.iface.GetFlipToStart()) else "Off")
        except Exception:
            pass
        try:
            gpu_mode = str(self.svc.iface.GetDgpuMode()).lower()
            _sync(self.gpu_combos, "Integrated" if "integrated" in gpu_mode else "Dedicated" if "dedicated" in gpu_mode or "nvidia" in gpu_mode else "Hybrid")
        except Exception:
            pass
        try:
            fm = str(self.svc.iface.GetFanMode()).lower()
            _sync(self.fan_combos, "Super Silent" if "super" in fm else "Dust Cleaning" if "dust" in fm else "Performance" if "performance" in fm else "Standard")
        except Exception:
            pass
        try:
            tdp = self.svc.iface.GetRyzenTdp()
            if self.tdp_spins:
                for s in self.tdp_spins:
                    s.blockSignals(True)
                self.tdp_spins[0].setValue(int(tdp.get("stapm", 45000)))
                self.tdp_spins[1].setValue(int(tdp.get("fast", 45000)))
                self.tdp_spins[2].setValue(int(tdp.get("slow", 45000)))
                for s in self.tdp_spins:
                    s.blockSignals(False)
        except Exception:
            pass

        if scroll:
            scroll.verticalScrollBar().setValue(scroll_val)

    # ── Sensor updates ────────────────────────────────────────────────
    def update_sensors(self):
        def set_bar_color(pb, val):
            if val < 50:
                color = "#27ae60"
            elif val < 80:
                color = "#f39c12"
            else:
                color = "#e74c3c"
            pb.setStyleSheet(
                f"QProgressBar::chunk {{ background-color: {color}; border-radius: 4px; }}"
            )

        if not self.svc.limited:
            try:
                s = self.svc.iface.GetSensors()
                cpu = float(s.get('cpu_temp', 0))
                gpu = float(s.get('gpu_temp', 0))
                cpu_util = float(s.get('cpu_usage', 0))
                gpu_util = float(s.get('gpu_usage', 0))
                fan = int(s.get('fan_rpm', 0))

                self.pb_cpu.setValue(int(cpu_util))
                set_bar_color(self.pb_cpu, int(cpu_util))
                self.lbl_cpu_util.setText(f"{cpu_util:.1f}%")

                self.pb_cput.setValue(int(cpu))
                set_bar_color(self.pb_cput, int(cpu))
                self.lbl_cpu_temp.setText(f"{cpu:.1f} °C")

                fan_pct = int(fan / 50 if fan > 0 else 0)
                self.pb_cpuf.setValue(fan_pct)
                set_bar_color(self.pb_cpuf, fan_pct)
                self.lbl_cpu_fan.setText(f"{fan} RPM" if fan > 0 else "Idle")

                self.pb_gpu.setValue(int(gpu_util))
                set_bar_color(self.pb_gpu, int(gpu_util))
                self.lbl_gpu_util.setText(f"{gpu_util:.1f}%")

                self.pb_gput.setValue(int(gpu))
                set_bar_color(self.pb_gput, int(gpu))
                self.lbl_gpu_temp.setText(f"{gpu:.1f} °C")

                if hasattr(self, 'pb_gpuf'):
                    self.pb_gpuf.setValue(fan_pct)
                    set_bar_color(self.pb_gpuf, fan_pct)
                    self.lbl_gpu_fan.setText(f"{fan} RPM" if fan > 0 else "Idle")
            except Exception:
                pass

        if hasattr(self, 'bat_labels'):
            binfo = get_battery_info()
            for k, lbl in self.bat_labels.items():
                if k in binfo:
                    val = binfo[k]
                    if val != "N/A":
                        if k in ["current", "full", "design"]:
                            val = str(int(val) // 1000) + " mAh/mWh"
                        elif k == "percent":
                            val += "%"
                    lbl.setText(val)
