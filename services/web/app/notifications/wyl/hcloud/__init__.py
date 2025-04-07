import os
import random
import hcloud._exceptions
from dotenv import load_dotenv
from hcloud import Client
from hcloud.images import Image
from hcloud.server_types import ServerType

load_dotenv('.env')

HCLOUD_API_TOKEN = os.getenv('HCLOUD_API_TOKEN_3')


class HetznerCloud:
    servers = []
    default_location = None
    ssh_keyname = 'rsa-key-20180508-E2-1271v3'
    server_type = 'cpx11'
    image_name = 'debian-12'

    char_list = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', '-']
    generating = False

    def __init__(self, location_name=None, token=None):
        if token is not None:
            self.client = Client(token=token)  # Please paste your API token here
        else:
            self.client = Client(token=f"{HCLOUD_API_TOKEN}")  # Please paste your API token here

        try:
            for loc in self.client.locations.get_all():
                if location_name is not None:
                    if loc.name == location_name:
                        self.default_location = loc
                else:
                    if loc.name == "nbg1":
                        self.default_location = loc
        except hcloud._exceptions.APIException as api_exceception:
            print(api_exceception.code)
            print(api_exceception.message)

    def list_servers(self):
        try:
            self.servers = self.client.servers.get_all()
            return self.servers
        except hcloud._exceptions.APIException as api_exceception:
            print("'"+ api_exceception.code + "'")
            print("'"+api_exceception.message+"'")
            return []

    def delete_server(self, delete_server):
        self.client.servers.delete(server=delete_server)

    def generate_random_string(self, length=10):
        return ''.join(random.choice(self.char_list) for _ in range(length))

    @staticmethod
    def count_char_occurrences(string, char):
        return string.count(char)

    def generate_new_servername(self):
        self.generating = False
        generated = False
        server_name = ""
        while not generated:
            if not self.generating:
                self.generating = True
            server_name = self.generate_random_string(20)
            count = self.count_char_occurrences(server_name, '-')

            if count > 1:
                first_char = True if server_name[0] == "-" else False
                last_char = True if server_name[-1] == "-" else False
                if first_char:
                    pass
                else:
                    if last_char:
                        pass
                    else:
                        generated = True
                        print("ok")
        self.generating = False
        return server_name

    def create_server(self, server_name=None, server_type=None, image_name=None):
        if server_type is None:
            server_type = self.server_type
        if image_name is None:
            image_name = self.image_name

        if server_name is None:
            server_name = self.generate_new_servername()

        response = self.client.servers.create(
            name=server_name,
            server_type=ServerType(name=server_type),
            location=self.default_location,
            image=Image(name=image_name),
            ssh_keys=[self.client.ssh_keys.get_by_name(self.ssh_keyname)]
        )
        print(response.server.public_net)
        print(response.server.public_net.ipv4)
        print(response.server.public_net.ipv6)
        print(response.server.public_net.primary_ipv4)
        print(response.server.public_net.primary_ipv6)
        print(response.server.public_net.ipv4.ip)
        print(response.server.public_net.ipv6.ip)
        print(response)

        server = response.server

        print(f"{server.id=} {server.name=} {server.status=}")
        print(f"root password: {response.root_password}")
        return server, response.root_password
