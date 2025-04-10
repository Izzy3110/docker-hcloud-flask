import os
import time
import paramiko
import qrcode
from services.web.app.notifications.wyl.notifications import notify
from services.web.app.wyl.logging import logger
from services.web.app.wyl.ssh_manager import SSHManager


username = 'root'


def generate_qr_code(data: str, folder: str = 'qrcodes_data', filename: str = "qrcode.png"):
    """
    Generates a QR code from the provided data and saves it as an image file in the specified folder.

    :param data: The string to encode in the QR code.
    :param folder: The folder where the QR code image will be saved.
    :param filename: The name of the QR code image file (default is 'qrcode.png').
    """
    # Ensure the folder exists
    os.makedirs(folder, exist_ok=True)

    # Create the QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=100,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create an image from the QR Code instance
    img = qr.make_image(fill='black', back_color='white')

    # Define the full file path
    file_path = os.path.join(folder, filename)

    # Save the image
    img.save(file_path)
    print(f"QR code saved at: {file_path}")


def clear_servers(cloud_instance, del_location_name):
    do_not_delete_server_names = [
        "debian-4gb-fsn1-4"
    ]

    list_servers = cloud_instance.list_servers()
    for server_ in list_servers:
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
        with open("last_servers.txt", "a") as last_server_f:
            last_server_f.write(server.public_net.ipv4.ip+"\n")
        notify("Event detected", f"installing: {server.public_net.primary_ipv4.ip}", app_name="Hetzner Manager")
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
                err_message = no_valid_conn.args[1]
                print(f"Error: {err_message}")
                no_valid_connections_error = True
                pass

        try:
            notify(
                "Event detected",
                f"installed: {server.public_net.primary_ipv4.ip}",
                app_name="Hetzner Manager"
            )
        except Exception:
            notify(
                "Event detected",
                f"installed: {server.public_net.primary_ipv4.ip}",
                app_name="Hetzner Manager"
            )
        return server
    return None
