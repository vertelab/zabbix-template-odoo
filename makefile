#/usr/bin/make

# TODO: Fix target all !

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

all: build_sudoer build_zabbixconf
	@echo "Building:" $^

clean:
	rm -rf build/*

install: install_pyclient install_sudoers install_zabbixconf

install_pyclient:
	install -D -m 755 python/odoohelperlite.py $(DESTDIR)$(bindir)/odoohelperlite
uninstall_pyclient:
	rm $(DESTDIR)$(bindir)/odoohelperlite

$(builddir)/zabbix_sudo: zabbix_sudo
	@cp zabbix_sudo $(builddir)/zabbix_sudo
	@sed -i "s|ODOOUSER|$(odoouser)|g" $(builddir)/zabbix_sudo
	@sed -i "s|ZBXUSR|$(zbxuser)|g" $(builddir)/zabbix_sudo
	@sed -i "s|BINNAMEFULL|$(bindir)/odoohelperlite|g" $(builddir)/zabbix_sudo

.PHONY: build_sudoer
build_sudoer: $(builddir)/zabbix_sudo
install_sudoers: $(builddir)/zabbix_sudo
	install -D -o root -g root -m 440 $(builddir)/zabbix_sudo $(DESTDIR)$(sudoersdir)/zabbix_sudo
uninstall_sudoers:
	rm $(DESTDIR)$(sudoersdir)/zabbix_sudo

$(builddir)/zabbix-odoo.conf: zabbix-odoo.conf
	cp zabbix-odoo.conf $(builddir)/zabbix-odoo.conf
	@sed -i "s|BINNAME|odoohelperlite|g" $(builddir)/zabbix-odoo.conf
.PHONY: build_zabbixconf
build_zabbixconf: $(builddir)/zabbix-odoo.conf
install_zabbixconf: $(builddir)/zabbix-odoo.conf
	install -D -m 644 $(builddir)/zabbix-odoo.conf $(DESTDIR)$(zbxagentconf)/zabbix-odoo.conf
uninstall_zabbixconf:
	rm $(DESTDIR)$(zbxagentconf)/zabbix-odoo.conf

.PHONY: all clean install
