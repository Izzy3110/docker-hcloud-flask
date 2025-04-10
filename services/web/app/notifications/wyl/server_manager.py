import os
import time
import paramiko
from services.web.app.notifications.wyl.logging import logger
from services.web.app.notifications.wyl.ssh_manager import SSHManager
from hcloud.servers import Server

username = 'root'


def clear_servers(cloud_instance, del_location_name, no_delete_names=None):
    do_not_delete_server_names = [
            "debian-4gb-fsn1-4"
        ] if no_delete_names is None else no_delete_names

    list_servers = cloud_instance.list_servers()
    for server_ in list_servers:
        server_: Server
        # print(server_.public_net.ipv4.ip)
        if server_.datacenter.location.name == del_location_name:

            if server_.name not in do_not_delete_server_names:
                print(f"deleting: {server_.id} {server_.name}")
                cloud_instance.delete_server(server_)
            else:
                print(f"not deleting: {server_.name}")
                print(server_.datacenter.location.name)


def create_and_install_server(hcloud_instance):
    curl_apt = "apt-get update && \
    curl -sSL https://raw.githubusercontent.com/Izzy3110/cloudserver-install/refs/heads/main/download.sh | bash && \
    cd cloudserver-install && bash install.sh"

    private_key_path = os.path.join(os.getcwd(), "privatekey-1271v3-open.openSSH")
    modify_last = False

    if modify_last:
        target_server = open("last_server").read().strip()
        servers = hcloud_instance.list_servers()
        for server in servers:
            if target_server == server.public_net.ipv4.ip:
                logger.debug(f"server-ip: {server.public_net.ipv4.ip}")
                ssh_man = SSHManager(
                    hostname=server.public_net.ipv4.ip,
                    username=username,
                    privatekey_filepath=private_key_path
                )
                ssh_man.execute_command(curl_apt)
    else:
        server, root_password = hcloud_instance.create_server()
        current_server_id = server.id
        current_server_public_ipv4 = server.public_net.ipv4.ip

        logger.debug(f"Server-ID: {current_server_id}")
        logger.debug(f"Server-IPv4: {current_server_public_ipv4}")

        i = 15
        while i >= 0:
            print(f"sleeping {i} seconds")
            time.sleep(1)
            i -= 1

        with open("last_server", "w") as last_server_f:
            last_server_f.write(server.public_net.ipv4.ip)

        ssh_man = SSHManager(
            hostname=server.public_net.ipv4.ip,
            username=username,
            privatekey_filepath=private_key_path
        )

        no_valid_connections_error = True
        while no_valid_connections_error:
            try:
                ssh_man.execute_command(curl_apt)
                break
            except paramiko.ssh_exception.NoValidConnectionsError as no_valid_conn:
                print(no_valid_conn.args)
                no_valid_connections_error = True
                pass
        return server
    return None
