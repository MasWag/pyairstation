from playwright.sync_api._generated import Playwright, Locator
from typing import Optional, List
from time import sleep
from .hosts import Host
import re


class Agent:
    DEFAULT_ROOT = "http://192.168.11.1"

    # Constructor takes Playwright
    def __init__(self, playwright: Playwright, user, password, root_uri=DEFAULT_ROOT):
        self.playwright = playwright
        self.browser = playwright.chromium.launch()
        self.page = self.browser.new_page()
        self.user = user
        self.password = password
        self.root_uri = root_uri
        self.login_uri = f"{root_uri}/login.html"
        self.panel_uri = f"{root_uri}/index_adv.html"

    def login(self):
        self.page.goto(self.login_uri)
        self.page.get_by_role("textbox", name="ユーザー名を入力してください。").fill(
            self.user
        )
        self.page.get_by_role("textbox", name="パスワードを入力してください。").fill(
            self.password
        )
        self.page.get_by_role("button", name="ログイン").click()
        self.page.goto(self.panel_uri)

    def need_login(self) -> bool:
        self.page.reload()
        return self.page.url == self.login_uri

    def ensure_logined(self):
        if self.need_login():
            self.login()
        else:
            self.page.goto(self.panel_uri)

    def ensure_dhcp(self):
        self.ensure_logined()
        self.page.goto(self.panel_uri)
        self.page.locator("#AT_LAN").click()
        self.page.get_by_text("DHCPリース").click()
        while self.page.locator('iframe[name="content_frame"]').count() == 0:
            sleep(1)
        content_frame = self.page.locator('iframe[name="content_frame"]').content_frame
        while content_frame.get_by_text("リース情報").count() == 0:
            sleep(1)

    def mac_from_ip(self, ip_address: str) -> Optional[str]:
        self.ensure_dhcp()
        content_frame = self.page.locator('iframe[name="content_frame"]').content_frame
        escaped_ip = re.escape(ip_address)
        ip_pattern = f"^\\\\(\\\\*\\\\)\\s*{escaped_ip}$|^{escaped_ip}$"
        row: Locator = content_frame.locator(
            f'tr:has(td:has(div:text-matches("{ip_pattern}")))'
        )
        if row.count() == 0:
            return None
        else:
            raw_text = row.locator('td:has-text(":")').first.inner_text()
            return re.search(
                r"([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})", raw_text
            ).group(0)

    def ip_from_mac(self, mac_address: str) -> Optional[str]:
        self.ensure_dhcp()
        content_frame = self.page.locator('iframe[name="content_frame"]').content_frame
        row = content_frame.locator(f'tr:has-text("{mac_address}")')
        if row.count() == 0:
            return None
        else:
            raw_text = row.locator("td").first.inner_text()
            return re.search(r"([0-9]{1,3}\.){3}[0-9]{1,3}", raw_text).group(0)

    def apply_dhcp_config(self, hosts: List[Host]):
        """Apply DHCP configuration for the given hosts.

        Args:
            hosts: List of Host objects to configure
        """
        for host in hosts:
            if host.skip_dhcp:
                continue
            current_ip: Optional[str] = self.ip_from_mac(host.mac)
            if current_ip is None:
                raise NotImplementedError(f'The MAC address {host.mac} is not yet used, which is not implemented')
            elif current_ip != host.ip:
                if self.mac_from_ip(host.ip) is None:
                    print(f'Change the IP address of {host.mac}: {current_ip} -> {host.ip}')
                    content_frame = self.page.locator('iframe[name="content_frame"]').content_frame
                    row = content_frame.locator(f'tr:has-text("{host.mac}")')
                    if row.get_by_text('自動割当').count() > 0:
                        row.get_by_text('手動割当に変更').click()
                    while row.get_by_text('修正').count() == 0:
                        sleep(1)
                    row.get_by_text('修正').click()
                    self.page.locator('input#id_IP').fill(host.ip)
                    self.page.get_by_text('修正保存').click()
                else:
                    # This case is not yet implemented
                    raise NotImplementedError(f'The IP address {host.ip} is already used, which is not implemented')

    def close(self):
        """Close the browser."""
        self.browser.close()
