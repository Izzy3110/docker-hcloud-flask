import os
import time

from services.web.app.notifications.wyl.hcloud import HetznerCloud
from services.web.app.notifications.wyl.notifications import notify
from services.web.app.notifications.wyl.server_manager import clear_servers
from services.web.app.wyl.logging import logger
from services.web.app.wyl.server_manager import create_and_install_server
from services.web.app.wyl.ssh_manager import connect_to_server

NETSTAT_CHECK_VNC_COMMAND = "netstat -anpt | grep -i listen | grep 5901"


def netstat_vnc_command(vnc_port: int = 5901):
    return f"netstat -anpt | grep -i listen | grep {vnc_port}"


def edit_line_in_file(filename, search_text, append_text):
    with open(filename, 'r') as file:
        lines = file.readlines()

    with open(filename, 'w') as file:
        for line in lines:
            if search_text in line:
                line = line.strip() + append_text + "\n"
            file.write(line)


def handle_check(instance_config, excluded_ips):
    notification_messages = []
    ips_ok = []

    servers_checked_lst = []
    for instance, details in instance_config.items():
        logger.debug(f"Instance: {instance}")
        logger.debug(f"  Description: {details['description']}")
        logger.debug(f"  Location: {details['location_name']}")
        logger.debug(f"  Create Range: {details['create_range']}")
        cloud_instance = HetznerCloud(token=os.getenv('HCLOUD_API_TOKEN'))

        print("  excluded_ips", end='')
        """Handles the 'check' command."""
        servers = [
            server.public_net.ipv4.ip
            for server in cloud_instance.list_servers()
            if server.public_net.ipv4.ip not in excluded_ips
        ]
        print("...done")

        count_servers = len(servers)
        notification_messages.append(f"{instance} ({details['description']}: {count_servers} servers\n")
        print("IF servers...", end="")
        if servers:
            logger.debug("Populating servers list...")

            for server_ip in servers:
                if server_ip not in servers_checked_lst:
                    logger.debug(f"  Appending: {server_ip}")
                    servers_checked_lst.append(server_ip)

                    with open("servers.lst") as servers_lst_r:
                        content_lines = servers_lst_r.readlines()
                        found_ip = False
                        for line in content_lines:
                            if server_ip in line:
                                found_ip = True
                        if not found_ip:
                            with open("servers.lst", "a") as servers_lst_w:  # Use 'a' mode to append
                                servers_lst_w.write(f"{instance}:{server_ip}\n")  # Append new entry safely

                    ip_ok = connect_to_server(server_ip, command=netstat_vnc_command())
                    if ip_ok:
                        ips_ok.append(server_ip)
                        with open("servers.lst") as servers_lst_r:
                            content_lines = servers_lst_r.readlines()
                            if len(content_lines) > 0:
                                for line in content_lines:
                                    if server_ip in line and ":ok" not in line:
                                        edit_line_in_file("servers.lst", server_ip, ":ok")

            server_ok = len(ips_ok) == len(servers)

            logger.debug(f"Servers OK ({len(ips_ok)}): {server_ok}")
        else:
            logger.debug(" - No servers")
        print("...done")
    print("notification", end='')
    notify(title="Action: Check", message="".join(notification_messages), app_name="Hetzner Manager")
    print("...done")


def can_create_server(cloud_instance, server_max_count, excluded_ips):
    servers = [
        server.public_net.ipv4.ip
        for server in cloud_instance.list_servers()
        if server.public_net.ipv4.ip not in excluded_ips
    ]

    if len(servers) < server_max_count:
        return True
    return False


def handle_start(instance_config, excluded_ips):
    """Handles the 'start' command."""
    """
    asyncio.run(
        set_redis_data(
            "main-messages",
            {
                    "action": "start",
                    "t": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                }
        )
    )
    """

    for instance_key, current_instance in instance_config.items():
        range_ = current_instance["create_range"]
        server_max_count = range_[1] - range_[0]

        lines = open("servers.lst").readlines()

        with open("servers.lst", "a") as servers_lst_f:
            if current_instance["token"] is not None:
                cloud_instance = HetznerCloud(
                    location_name=current_instance["location_name"],
                    token=os.getenv(current_instance["token"])
                )

                logger.debug(
                    f"Creating and installing servers on Instance: {instance_key} ({current_instance['description']})")
                for i in range(*current_instance["create_range"]):
                    can_create = can_create_server(cloud_instance, server_max_count, excluded_ips)
                    if can_create:
                        logger.debug(f"[{i}] Creating server")

                        server = create_and_install_server(cloud_instance)
                        server_ip = server.public_net.ipv4.ip
                        print("'"+server_ip+"'")

                        logger.debug(f"SERVER-IP: {server_ip}")
                        if len(lines) == 0:
                            servers_lst_f.write(f"{instance_key}:{server_ip}\n")
                        else:
                            found_ip = False
                            for line in lines:
                                if server_ip in line:
                                    found_ip = True
                            if not found_ip:
                                servers_lst_f.write(f"{instance_key}:{server_ip}\n")

                        time.sleep(3)
                    else:
                        logger.debug("CANNOT CREATE: LIMIT")


def handle_delete(instance_config, excluded_ips=None):
    """Handles the 'delete' command."""
    logger.debug("Deleting servers...")

    if excluded_ips is not None:
        print(excluded_ips)

    for instance_key, current_instance in instance_config.items():
        if current_instance["token"] is not None:
            cloud_instance = HetznerCloud(
                location_name=current_instance["location_name"],
                token=os.getenv(current_instance["token"])
            )
            clear_servers(
                cloud_instance=cloud_instance,
                del_location_name=current_instance["location_name"],
                no_delete_names=["debian-4gb-fsn1-4"]
            )
            logger.debug("Done - Deleting servers")
