import xml.etree.ElementTree as ET
from typing import Optional, List


class Host:
    def __init__(self, hostname: str, ip: str, mac: str, skip_dhcp: bool = False):
        self.hostname = hostname
        self.ip = ip
        self.mac = mac
        self.skip_dhcp = skip_dhcp

    def __repr__(self):
        return f"Host(hostname={self.hostname!r}, ip={self.ip!r}, mac={self.mac!r}, skip_dhcp={self.skip_dhcp})"


class HostConfig:
    def __init__(self, xml_path: str):
        self.hosts: List[Host] = []
        self._load(xml_path)

    def _load(self, xml_path: str):
        tree = ET.parse(xml_path)
        root = tree.getroot()

        if root.tag != "hosts":
            raise ValueError("Root element must be <hosts>")

        for elem in root.findall("host"):
            hostname = elem.attrib["hostname"]
            skip_dhcp = elem.attrib.get("skip_dhcp") == "true"
            ip_elem = elem.find("ip")
            mac_elem = elem.find("mac")

            if ip_elem is None or mac_elem is None:
                raise ValueError(f"Missing <ip> or <mac> in host {hostname}")

            host = Host(
                hostname=hostname,
                ip=ip_elem.text.strip(),
                mac=mac_elem.text.strip(),
                skip_dhcp=skip_dhcp
            )
            self.hosts.append(host)


# Example usage:
if __name__ == "__main__":
    config = HostConfig("examples/hosts.xml")
    for host in config.hosts:
        print(host)
