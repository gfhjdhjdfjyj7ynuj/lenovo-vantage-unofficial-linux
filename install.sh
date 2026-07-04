#!/bin/bash
#
# Universal installer for Lenovo Vantage Linux.
# Does NOT guess the distribution — installs everything into fixed
# system paths and reloads systemd + D-Bus.
#
# Usage:
#   sudo ./install.sh            # install
#   sudo ./install.sh --uninstall # remove
#

set -e

INSTALL_DIR="/usr/lib/vantage"
SYSTEMD_DIR="/etc/systemd/system"
DBUS_DIR="/etc/dbus-1/system.d"
APP_DIR="/usr/share/applications"
ICON_DIR="/usr/share/icons/hicolor/scalable/apps"
BIN_DIR="/usr/bin"

require_root() {
    if [ "$EUID" -ne 0 ]; then
        echo "This script must be run as root. Try: sudo $0"
        exit 1
    fi
}

check_python_deps() {
    local missing=()
    python3 -c "import dbus"    2>/dev/null || missing+=("python3-dbus")
    python3 -c "import PyQt6"   2>/dev/null || missing+=("python3-pyqt6")
    python3 -c "import gi"      2>/dev/null || missing+=("python3-gi (PyGObject)")

    if [ ${#missing[@]} -gt 0 ]; then
        echo "WARNING: Missing Python dependencies: ${missing[*]}"
        echo "Install them with your package manager before running the GUI/CLI."
        echo "  Debian/Ubuntu: sudo apt install ${missing[*]}"
        echo "  Fedora:        sudo dnf install ${missing[*]}"
        echo "  Arch:          sudo pacman -S ${missing[*]}"
        echo ""
    fi
}

do_install() {
    echo "=== Installing Lenovo Vantage Linux ==="

    check_python_deps

    echo "Copying program files to $INSTALL_DIR ..."
    mkdir -p "$INSTALL_DIR/service/features" "$INSTALL_DIR/service/ipc" "$INSTALL_DIR/cli"
    cp -r service/* "$INSTALL_DIR/service/"
    cp -r cli/*   "$INSTALL_DIR/cli/"
    chmod +x "$INSTALL_DIR/service/vantageservice.py"
    chmod +x "$INSTALL_DIR/cli/vantage-gui.py"
    chmod +x "$INSTALL_DIR/cli/vantage-cli.py"

    echo "Installing systemd service ..."
    cp systemd/vantageservice.service "$SYSTEMD_DIR/"
    chmod 644 "$SYSTEMD_DIR/vantageservice.service"

    echo "Installing D-Bus policy ..."
    mkdir -p "$DBUS_DIR"
    cp dbus/org.lenovo.Vantage.conf "$DBUS_DIR/"
    chmod 644 "$DBUS_DIR/org.lenovo.Vantage.conf"

    echo "Installing desktop entry and icon ..."
    mkdir -p "$APP_DIR" "$ICON_DIR"
    cp vantage.desktop "$APP_DIR/"
    if [ -f "vantage.png" ]; then
        cp vantage.png "$ICON_DIR/"
    fi

    echo "Creating CLI / GUI launchers ..."
    cat > "$BIN_DIR/vantage-gui" <<'EOF'
#!/bin/bash
cd /usr/lib/vantage/cli && exec python3 vantage-gui.py "$@"
EOF
    cat > "$BIN_DIR/vantage-cli" <<'EOF'
#!/bin/bash
cd /usr/lib/vantage/cli && exec python3 vantage-cli.py "$@"
EOF
    chmod +x "$BIN_DIR/vantage-gui" "$BIN_DIR/vantage-cli"

    echo "Reloading systemd and D-Bus ..."
    systemctl daemon-reload
    systemctl reload dbus 2>/dev/null || true

    echo "Enabling service ..."
    systemctl enable --now vantageservice.service

    echo ""
    echo "=== Installation complete ==="
    echo "Service:  systemctl status vantageservice"
    echo "GUI:      vantage-gui"
    echo "CLI:      vantage-cli --help"
}

do_uninstall() {
    echo "=== Uninstalling Lenovo Vantage Linux ==="

    systemctl disable --now vantageservice.service 2>/dev/null || true

    rm -f  "$SYSTEMD_DIR/vantageservice.service"
    rm -f  "$DBUS_DIR/org.lenovo.Vantage.conf"
    rm -f  "$APP_DIR/vantage.desktop"
    rm -f  "$ICON_DIR/vantage.png"
    rm -f  "$BIN_DIR/vantage-gui" "$BIN_DIR/vantage-cli" "$BIN_DIR/vantage"
    rm -rf "$INSTALL_DIR"
    rm -rf /etc/lenovo-vantage

    systemctl daemon-reload
    systemctl reload dbus 2>/dev/null || true

    echo "=== Uninstall complete ==="
}

require_root

if [ "$1" = "--uninstall" ]; then
    do_uninstall
else
    do_install
fi
