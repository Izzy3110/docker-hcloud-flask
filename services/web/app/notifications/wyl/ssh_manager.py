
import socket
import time
from datetime import datetime

import paramiko
from paramiko.rsakey import RSAKey
from services.web.app.notifications.wyl.logging import logger
from queue import Queue


q = Queue()


class SSHManager:
    key = None
    privatekey_filepath = None

    hostname = None
    username = None
    password = None

    connected = False
    lines = []
    closed_message_sent = False

    def __init__(self, **kwargs):
        self.client: paramiko.client.SSHClient = paramiko.client.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        if "privatekey_filepath" in kwargs.keys():
            self.privatekey_filepath = kwargs.get('privatekey_filepath', None)
        if "hostname" in kwargs.keys():
            self.hostname = kwargs.get('hostname')
        if "username" in kwargs.keys():
            self.username = kwargs.get('username')
        if "password" in kwargs.keys():
            self.password = kwargs.get('password')

        self.load_private_key()

    def execute_command(self, command):
        while not self.connected:
            try:
                self.client.connect(hostname=self.hostname, username=self.username, pkey=self.key)
                self.connected = True
                self.lines = []
            except socket.gaierror as se:
                num, error_message = se.args
                print(f"[{num}] {error_message}")
                time.sleep(2)
            except TimeoutError as te:
                print(f"[error] {str(te)}")
                time.sleep(2)
                pass

        if self.connected:
            _stdin, _stdout, _stderr = self.client.exec_command(command)
            for line in iter(lambda: _stdout.readline(256), ""):
                current_line_l = line.rstrip()
                print(f"l0: {current_line_l}")
                if current_line_l != "0":
                    self.lines.append(current_line_l)
                    q.put((datetime.now().timestamp(), current_line_l))

                    """
                    asyncio.run(
                        set_redis_data(
                            "main-messages",
                            {
                                "event": "ssh:execute_command:line_output",
                                "result_message": current_line_l,
                                "t": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                            }
                        )
                    )
                    """

            """
            current_line_lb = _stdout.readline().rstrip()
            print(f"l1: {current_line_lb}")
            asyncio.run(
                set_redis_data(
                    "main-messages",
                    {
                        "event": "ssh:execute_command:line_output",
                        "result_message": current_line_lb,
                        "t": datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    }
                )
            )
            self.lines.append(_stdout.readline().rstrip())
            # print(_stdout.read().decode())

            current_line_lc = _stderr.read().decode().rstrip()
            print(f"l2: {current_line_lc}")
            self.lines.append(current_line_lc)
            """

        self.client.close()
        self.connected = False

    def load_private_key(self, filename=None):
        if self.privatekey_filepath is not None:
            filename = self.privatekey_filepath
            print(" - loaded from filepath")
        try:
            self.key = RSAKey.from_private_key_file(filename=filename)
        except FileNotFoundError:
            print(f"Key-File does not exist: {filename}")


def connect_to_server(ip, command):
    """Connects to a server using Paramiko SSH and executes a command."""

    ip_ok = False

    # Initialize the SSH client
    client: paramiko.client.SSHClient = paramiko.SSHClient()

    # Automatically add host keys from the known hosts file
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    # Load the private key
    private_key: RSAKey = paramiko.RSAKey.from_private_key_file("privatekey-1271v3-open.openSSH")

    try:
        logger.info(f"Connecting to {ip}...")

        # Connect to the server
        client.connect(hostname=ip, username="root", pkey=private_key)

        # Execute the command
        stdin, stdout, stderr = client.exec_command(f"bash -c \"{command}\"")

        # Read the output and errors
        output = stdout.read().decode()
        error = stderr.read().decode()

        if len(output) > 0:
            ip_ok = True

        # Log the output and errors
        if output:
            logger.info(f"Output from {ip}: {output.strip()}")

        if error:
            logger.error(f"Error from {ip}: {error.strip()}")

    except Exception as e:
        logger.error(f"Failed to connect to {ip}: {e}")
        return ip_ok

    finally:
        logger.debug("closing the connection")

        # Close the connection
        client.close()
        return ip_ok
