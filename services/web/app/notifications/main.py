from __future__ import annotations
import asyncio
import textwrap
import argparse
from dotenv import load_dotenv
from wyl.actions import handle_check, handle_start, handle_delete
from wyl.yaml_config import load_config

load_dotenv('.env')

# Load the configuration
config = load_config("config.yaml")

debug = config["system"]["debug"]

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

instance_config = config.get("instance_config", {})
excluded_ips = config.get("excluded_ips", [])


parser = argparse.ArgumentParser(
    prog='main',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent('''\
        Hetzner Cloud Server - Automated Installation
        --------------------------------
        '''),
    usage="main [-h] [--action [start|delete|check]] [--start | -s] [--delete | -d] [--check | -c]"
)

parser.add_argument(
    "--action", "-a",
    help="Action to execute in the %(prog)s program",
    choices=["start", "delete", "check"]
)

# Define boolean arguments
parser.add_argument(
    "--start", "-s",
    help="Start Servers on all instances",
    action="store_true"
)
parser.add_argument(
    "--delete", "-d",
    help="Delete all servers on all instances",
    action="store_true"
)
parser.add_argument(
    "--check", "-c",
    help="Check Servers on default instance",
    action="store_true"
)

args = parser.parse_args()


cmd = "check"

if __name__ == '__main__':
    # Dispatch table for commands
    commands = {
        "check": lambda: handle_check(instance_config, excluded_ips),
        "start": lambda: handle_start(instance_config, excluded_ips),
        "delete": lambda: handle_delete(instance_config, excluded_ips),
    }

    print(f"execute command: {cmd}")
    # Execute the appropriate command or default to an error message
    commands.get(cmd, lambda: print(f"Unknown command: {cmd}"))()
    print("...done|execute  ")
    # notify("test-title", "Test Message", app_name="Test-Script")
