pyairstation
============

[![License: Apache-2.0](https://img.shields.io/github/license/maswag/pyairstation)](./LICENSE)


`pyairstation` is a Python library and CLI tool for managing DHCP lease and DNS configurations on Buffalo AirStation routers. It provides a simple interface to inspect, convert, and apply network configurations based on structured host files.

This implementation is tested on Buffalo AirStation WSR-1166DHPL2.

Requirements
------------

- Python 3.9+
- [Playwright](https://playwright.dev/python/) for web automation

Installation
------------

Clone this repository and install the package using `pip`:

```sh
pip install .
playwright install
```

`playwright install` is necessary to download the required browser engines.

CLI Usage
---------

All commands follow the structure:

```sh
pyairstation [COMMAND] [SUBCOMMAND] [OPTIONS]
```

You can view all available commands and flags using:

```sh
pyairstation --help
```


### Command: `show`

Display the contents of a given host file in a human-readable format. Useful for verifying the loaded configuration before applying changes.

```sh
pyairstation show [HOST_FILE]
```

#### Arguments

- `HOST_FILE`: Path to an XML file describing host information (see [Host File Format](#host-file-format)).


#### Example

```sh
pyairstation show ./examples/hosts.xml
```



DHCP Commands
-------------

### Command: `dhcp get-ip`

Retrieve the IP address associated with the given MAC address from the router's DHCP table.

```sh
pyairstation dhcp get-ip [OPTIONS] <MAC>
```

#### Arguments

- `<MAC>`: MAC address of the device to look up (e.g., `00:1A:2B:3C:4D:5E`).

#### Options

- `-u`, `--user`: Router username (default: `admin`)
- `-p`, `--pass`: Router password

#### Example

```sh
pyairstation dhcp get-ip -u admin -p secret 00:1A:2B:3C:4D:5E
```



### Command: `dhcp get-mac`

Retrieve the MAC address associated with the given IP address from the router's DHCP table.

```sh
pyairstation dhcp get-mac [OPTIONS] <IP>
```

#### Arguments

- `<IP>`: IP address to look up (e.g., `192.168.11.2`).

#### Options

- `-u`, `--user`: Router username (default: `admin`)
- `-p`, `--pass`: Router password

#### Example

```sh
pyairstation dhcp get-mac -u admin -p secret 192.168.11.2
```



### Command: `dhcp apply`

Apply static DHCP lease settings from the XML host file to the router. This operation uses browser automation to configure the router and will overwrite existing DHCP reservations.

```sh
pyairstation dhcp apply [OPTIONS] [HOST_FILE]
```

#### Arguments

- `HOST_FILE`: Path to an XML file describing host information.

#### Options

- `-u`, `--user`: Router username (default: `admin`)
- `-p`, `--pass`: Router password
- `-y`, `--yes`: Automatically confirm all prompts (non-interactive)

#### Example

```sh
pyairstation dhcp apply -u admin -p secret ./examples/hosts.xml
```

Hosts Commands
--------------

### Command: `hosts show`

Convert an XML host file into `/etc/hosts` format for name resolution.

```sh
pyairstation hosts show [HOST_FILE]
```

#### Arguments

- `HOST_FILE`: Path to the host configuration XML file.

#### Example

```sh
pyairstation hosts show ./examples/hosts.xml
```

Output:

```
192.168.11.1 router
192.168.11.2 http
```


Host File Format
----------------

The host file must be an XML document with the following structure:

```xml
<hosts>
  <host hostname="router" skip_dhcp="true">
    <ip>192.168.11.1</ip>
    <mac>00:1A:2B:3C:4D:5E</mac>
  </host>
  <host hostname="http">
    <ip>192.168.11.2</ip>
    <mac>1A:2B:3C:4D:5E:6F</mac>
  </host>
</hosts>
```

### Elements and Attributes

- `hostname` (attribute): Name to assign to the host.
- `skip_dhcp` (optional): If `"true"`, DHCP reservation is skipped for that host.
- `<ip>`: The IP address to associate.
- `<mac>`: The MAC address of the device.


License
-------

This project is open-source and distributed under the Apache 2.0 License.
