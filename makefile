#/usr/bin/make

# https://www.gnu.org/prep/standards/standards.html
prefix = /usr/local
exec_prefix = $(prefix)
bindir = $(exec_prefix)/bin

# Custom
builddir = build

sudoersdir = /etc/sudoers.d

odoouser = odoo

zbxuser = zabbix
zbxconfdir = /etc/zabbix
zbxagentconf = $(zbxconfdir)/zabbix_agentd.conf.d

all: build_%
	echo $(bindir)

clean:
	rm -rf build/*

install: install_pyclient install_sudoers install_zabbixconf

install_pyclient:
	install -m 755 python/odoohelperlite.py $(bindir)/odoohelperlite
uninstall_pyclient:
	rm $(bindir)/odoohelperlite

build_sudoer: zabbix_sudo
	@cp zabbix_sudo $(builddir)/zabbix_sudo
	@sed -i "s|ODOOUSER|$(odoouser)|g" $(builddir)/zabbix_sudo
	@sed -i "s|ZBXUSR|$(zbxuser)|g" $(builddir)/zabbix_sudo
	@sed -i "s|BINNAMEFULL|$(bindir)/odoohelperlite|g" $(builddir)/zabbix_sudo

install_sudoers: $(builddir)/zabbix_sudo
	install -o root -g root -m 440 $(builddir)/zabbix_sudo $(sudoersdir)/zabbix_sudo
uninstall_sudoers:
	rm $(sudoersdir)/zabbix_sudo

build_zabbixconf: zabbix-odoo.conf
	cp zabbix-odoo.conf $(builddir)/zabbix-odoo.conf
	@sed -i "s|BINNAME|odoohelperlite|g" $(builddir)/zabbix-odoo.conf

install_zabbixconf: $(builddir)/zabbix-odoo.conf
	install -m 644 $(builddir)/zabbix-odoo.conf $(zbxagentconf)/zabbix-odoo.conf
uninstall_zabbixconf:
	rm $(zbxagentconf)/zabbix-odoo.conf

.PHONY: all clean install install_% uninstall_% build_%
