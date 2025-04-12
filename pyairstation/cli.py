import argparse
import sys
from typing import List, Optional
from playwright.sync_api import sync_playwright
import getpass

from .hosts import HostConfig, Host
from .agent import Agent


def show_command(args):
    """Display the contents of a host file in a human-readable format."""
    try:
        config = HostConfig(args.host_file)
        print(f"Host configuration from {args.host_file}:")
        print("-" * 60)
        for host in config.hosts:
            print(f"Hostname: {host.hostname}")
            print(f"IP: {host.ip}")
            print(f"MAC: {host.mac}")
            print(f"Skip DHCP: {host.skip_dhcp}")
            print("-" * 60)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def dhcp_apply_command(args):
    """Apply DHCP configuration to a Buffalo AirStation router."""
    try:
        config = HostConfig(args.host_file)
        
        # Get password if not provided
        password = args.password
        if password is None:
            password = getpass.getpass(f"Password for {args.user}: ")
        
        # Confirm changes if not using --yes flag
        if not args.yes:
            print(f"The following DHCP reservations will be applied to the router:")
            for host in config.hosts:
                if not host.skip_dhcp:
                    print(f"  {host.hostname}: {host.ip} ({host.mac})")
            
            confirm = input("Do you want to continue? [y/N] ")
            if confirm.lower() not in ["y", "yes"]:
                print("Operation cancelled.")
                return
        
        # Apply DHCP configuration
        with sync_playwright() as playwright:
            agent = Agent(playwright, args.user, password)
            try:
                agent.login()
                
                # Apply DHCP configuration using the new method
                agent.apply_dhcp_config([host for host in config.hosts if not host.skip_dhcp])
                
                print("DHCP configuration applied successfully.")
            finally:
                agent.close()
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
def hosts_show_command(args):
    """Generate /etc/hosts-style entries from the XML host configuration."""
    try:
        config = HostConfig(args.host_file)
        for host in config.hosts:
            print(f"{host.ip} {host.hostname}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def dhcp_get_ip_command(args):
    """Retrieve the IP address associated with a given MAC address."""
    try:
        # Get password if not provided
        password = args.password
        if password is None:
            password = getpass.getpass(f"Password for {args.user}: ")
        
        with sync_playwright() as playwright:
            agent = Agent(playwright, args.user, password)
            try:
                agent.login()
                ip_address = agent.ip_from_mac(args.mac)
                if ip_address:
                    print(ip_address)
                else:
                    print(f"No IP address found for MAC: {args.mac}", file=sys.stderr)
                    sys.exit(1)
            finally:
                agent.close()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def dhcp_get_mac_command(args):
    """Retrieve the MAC address associated with a given IP address."""
    try:
        # Get password if not provided
        password = args.password
        if password is None:
            password = getpass.getpass(f"Password for {args.user}: ")
        
        with sync_playwright() as playwright:
            agent = Agent(playwright, args.user, password)
            try:
                agent.login()
                mac_address = agent.mac_from_ip(args.ip)
                if mac_address:
                    print(mac_address)
                else:
                    print(f"No MAC address found for IP: {args.ip}", file=sys.stderr)
                    sys.exit(1)
            finally:
                agent.close()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

        sys.exit(1)


def main(argv: Optional[List[str]] = None):
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description="Python tool for managing Buffalo AirStation routers"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # 'show' command
    show_parser = subparsers.add_parser(
        "show", help="Display the contents of a host file"
    )
    show_parser.add_argument("host_file", help="Path to the host XML file")
    show_parser.set_defaults(func=show_command)
    
    # 'dhcp' command group
    dhcp_parser = subparsers.add_parser(
        "dhcp", help="DHCP-related commands"
    )
    dhcp_subparsers = dhcp_parser.add_subparsers(dest="subcommand")
    
    # 'dhcp apply' command
    dhcp_apply_parser = dhcp_subparsers.add_parser(
        "apply", help="Apply DHCP configuration to a router"
    )
    dhcp_apply_parser.add_argument("host_file", help="Path to the host XML file")
    dhcp_apply_parser.add_argument(
        "-u", "--user", default="admin", help="Username for router login"
    )
    dhcp_apply_parser.add_argument(
        "-p", "--password", help="Password for router login"
    )
    dhcp_apply_parser.add_argument(
        "-y", "--yes", action="store_true", help="Automatically confirm changes"
    )
    dhcp_apply_parser.set_defaults(func=dhcp_apply_command)
    
    # 'dhcp get-ip' command
    dhcp_get_ip_parser = dhcp_subparsers.add_parser(
        "get-ip", help="Retrieve the IP address for a given MAC address"
    )
    dhcp_get_ip_parser.add_argument("mac", metavar="MAC", help="MAC address to look up")
    dhcp_get_ip_parser.add_argument(
        "-u", "--user", default="admin", help="Username for router login"
    )
    dhcp_get_ip_parser.add_argument(
        "-p", "--password", help="Password for router login"
    )
    dhcp_get_ip_parser.set_defaults(func=dhcp_get_ip_command)
    
    # 'dhcp get-mac' command
    dhcp_get_mac_parser = dhcp_subparsers.add_parser(
        "get-mac", help="Retrieve the MAC address for a given IP address"
    )
    dhcp_get_mac_parser.add_argument("ip", metavar="IP", help="IP address to look up")
    dhcp_get_mac_parser.add_argument(
        "-u", "--user", default="admin", help="Username for router login"
    )
    dhcp_get_mac_parser.add_argument(
        "-p", "--password", help="Password for router login"
    )
    dhcp_get_mac_parser.set_defaults(func=dhcp_get_mac_command)
    
    # 'hosts' command group
    hosts_parser = subparsers.add_parser(
        "hosts", help="Hosts-related commands"
    )
    hosts_subparsers = hosts_parser.add_subparsers(dest="subcommand")
    
    # 'hosts show' command
    hosts_show_parser = hosts_subparsers.add_parser(
        "show", help="Generate /etc/hosts-style entries"
    )
    hosts_show_parser.add_argument("host_file", help="Path to the host XML file")
    hosts_show_parser.set_defaults(func=hosts_show_command)
    
    # Parse arguments
    args = parser.parse_args(argv)
    
    # Execute the appropriate command
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()