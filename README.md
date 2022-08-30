# Odoo Zabbix Plugin

Display Odoo metrics in Zabbix.

## Usage

The program is not intended to be used manually and is instead intended to be
used by the zabbix agent daemon.

The python client, assuming it has been installed as described below, has the
name `odoohelperlite` when installed and the options can be explored using
the flag `--help` . For the subcommands the help-flag for the time being need
the flag `--no-sanity` to run.

**Example 1 - Basic:**
```
myuser@demo:~$ odoohelperlite --help
Usage: odoohelperlite [OPTIONS] COMMAND [ARGS]...



Options:
  -u, --user TEXT         Dev. Option: Set odoo user.
  -f, --filestore TEXT    Dev. Option: Set filestore.
  --sanity / --no-sanity  Dev. Option: Ignore sanity checks.
  --help                  Show this message and exit.

Commands:
  database   Display database information.
  discovery  Run Zabbix Discovery
myuser@demo:~$
```

**Example 2 - Help of subcommand database:**

Note the no-sanity flag. Otherwise a safety-check prevents program from
continuing. It is currently safe to run the program with the sanity check off
and it will remain safe when calling the `--help` flags.
```
myuser@demo:~$ odoohelperlite --no-sanity database --help
Usage: odoohelperlite database [OPTIONS]

  Display database information.

Options:
  -l, --list           List all Odoo databases.
  -n, --nbr, --count   Count all Odoo databases.
  -d, --database TEXT  Perform operations on the given database.
  --db-size            Size of db in bytes.
  --fs-size            Size of filestore in bytes.
  --size               Size of db and filestore in bytes.
  --get-param          Get database parameter.
  --url                Get database web.base.url.
  --url-freeze         Get web.base.url.freeze parameter.
  --help               Show this message and exit.

```



## Prerequisites

  * Ubuntu 20.04 or later (likely works on older too)
  * `zabbix-agent` installed.
  * Python 3.7 or later (can run on at least 3.6 with minor modifications)

## Installation

Three main steps:
  1. Configure and install the agent plugin.
  2. Import the template.
  3. Apply template to the host in Zabbix.

The default configuration should work under the assumption the prerequisites are
met.

To configure the host:
```
$: make
$: sudo make install
$: sudo service zabbix-agent restart
```

The template should just need to be imported into Zabbix. There are two
templates: One intended for normal use and nearly identical test one who gathers
the same data at a much higher frequency.

## Caveats

  * As of this commit it is very much an experimental project.
    Use at your own risk!

  * The default template gather data quite slowly. It might take a long time
    before items are discovered, data trickles through etc.

  * Regarding Zabbix being slow: If running the host behind a proxy it might
    take a long time for the proxy to catch up. In the mean time Zabbix might
    behave strangely, like displaying the host connection as being in an unknown
    state while collecting data.


## Dev notes:

Requires: Python 3.7 or later
