from hcloud import Client
from hcloud.servers.client import ServersClient
from hcloud.server_types.client import ServerTypesClient
from hcloud.locations.client import LocationsClient
from hcloud.images.client import ImagesClient


class HetznerCloudManager:
    def __init__(self, api_token: str):
        self.client = Client(token=api_token)
        self.servers = ServersClient(self.client)
        self.server_types = ServerTypesClient(self.client)
        self.locations = LocationsClient(self.client)
        self.images = ImagesClient(self.client)

    def get_existing_names(self):
        """Returns a list of all server names in the account."""

        servers = self.list_servers()
        return [server.name for server in servers]

    def generate_server_name(self, base_name: str, max_attempts=100):
        """
        Generates a unique server name by appending an incrementing number to a base name.

        :param base_name: The base name (e.g., "debian-2gb-nbg1")
        :param max_attempts: The maximum number of attempts to find a unique name
        :return: A unique server name
        """

        existing_names = self.get_existing_names()
        suffix = 1  # Start with number 1

        # Try to find an unused name by appending numbers
        while f"{base_name}-{suffix}" in existing_names and suffix <= max_attempts:
            suffix += 1

        # Return the generated name
        return f"{base_name}-{suffix}"

    def list_servers(self):
        """Lists all servers in the Hetzner Cloud account."""

        return self.servers.get_all()

    def get_by_id(self, server_id: int):
        """
        Retrieves a server by its ID.

        :param server_id: The ID of the server to fetch
        :return: Server object if found, else None
        """

        return self.servers.get_by_id(server_id)

    def create_server(self, name: str, server_type: str, image: str, location: str):
        """
        Creates a new server.

        :param name: Name of the server
        :param server_type: Hetzner server type (e.g., "cx11")
        :param image: OS image (e.g., "ubuntu-22.04")
        :param location: Hetzner datacenter location (e.g., "nbg1")
        :return: The created server object
        """

        server_type_obj = self.server_types.get_by_name(server_type)
        image_obj = self.images.get_by_name(image)
        location_obj = self.locations.get_by_name(location)

        # If no name is provided, generate one
        if not name:
            memory_gb = int(server_type_obj.memory)
            image_name = f"{image_obj.name.replace('-','').replace('.','')}"
            name = self.generate_server_name(f"{image_name}-{memory_gb}gb-{location}")

        server = self.servers.create(
            name=name,
            server_type=server_type_obj,
            image=image_obj,
            location=location_obj
        )
        return server.server

    def delete_server(self, server_id: int):
        """
        Deletes a server by its ID.

        :param server_id: The ID of the server to delete
        :return: None
        """

        server = self.get_by_id(server_id)
        if server:
            self.servers.delete(server)

    def get_image_list(self):
        """
        Retrieves a list of available images with their names and architecture.

        :return: List of tuples with image name and architecture (e.g., [("ubuntu-22.04", "x86_64"), ...])
        """

        image_list = self.images.get_all()
        return [(image.name, image.architecture) for image in image_list]
