.PHONY: install uninstall

install:
	chmod +x ./install.sh
	./install.sh

uninstall:
	systemctl disable --now vantageservice.service || true
	rm -f /usr/share/icons/hicolor/scalable/apps/vantage.png
	rm -f /usr/share/applications/vantage.desktop
	rm -f /usr/bin/vantage
	rm -f /usr/bin/vantage-cli
	rm -f /usr/bin/vantage-gui
	rm -rf /usr/lib/vantage
	rm -rf /etc/lenovo-vantage
	rm -f /etc/dbus-1/system.d/org.lenovo.Vantage.conf
	rm -f /etc/systemd/system/vantageservice.service
	systemctl daemon-reload
