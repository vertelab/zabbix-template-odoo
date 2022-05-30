# Odoo Zabbix Plugin

Display Odoo metrics in Zabbix.

## Usage

TODO: Fill out this segment.

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
