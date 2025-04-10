import os
import requests
import pickle
import urllib3

from dotenv import load_dotenv

from services.web.app.notifications.wyl.helpers import CookieHandler

# Load environment variables
load_dotenv('.env')

# Configuration from environment variables
proxmox_api_base_url = os.getenv('API_BASE_URL')
username = os.getenv('PROXMOX_USER')
password = os.getenv('PROXMOX_PASS')

verify_ssl = False  # Change to True if you use valid SSL certificates
cookie_file = "proxmox_cookie.pkl"

if not verify_ssl:
    urllib3.disable_warnings()


class ProxmoxApi:
    def __init__(self, api_base_url=None):
        if api_base_url is not None:
            self.api_base_url = api_base_url
            self.auth_url = f"{self.api_base_url}/access/ticket"

    class RestartVM:
        def __init__(self, current_api, current_cookies, current_csrf_token):
            self.api = current_api
            self.cookies = current_cookies
            self.csrf_token = current_csrf_token
            self.node_name = None
            self.vmid = None

        def by_name(self, vm_name):
            """Find a VM by its name and set its VMID and node_name."""
            api_nodes = self.api.list_nodes(self.cookies)
            for node in api_nodes:
                current_vms = self.api.list_vms(self.cookies, current_node_name=node["node"])
                for current_vm in current_vms:
                    if current_vm["name"] == vm_name:
                        self.node_name = node["node"]
                        self.vmid = current_vm["vmid"]
                        return self
            raise ValueError(f"VM with name '{vm_name}' not found.")

        def by_id(self, current_vm_id: int):
            """Find a VM by its name and set its VMID and node_name."""
            current_nodes = self.api.list_nodes(self.cookies)
            for node in current_nodes:
                node_vms = self.api.list_vms(self.cookies, current_node_name=node["node"])
                for current_vm in node_vms:
                    if current_vm["vmid"] == current_vm_id:
                        self.node_name = node["node"]
                        self.vmid = current_vm["vmid"]
                        return self
            raise ValueError(f"VM with id '{current_vm_id}' not found.")

        def exec(self):
            """Restart the selected VM."""
            if not self.node_name or not self.vmid:
                raise ValueError("Node name and VMID must be set before executing.")
            url = f"{self.api.api_base_url}/nodes/{self.node_name}/qemu/{self.vmid}/status/reboot"
            headers = {"CSRFPreventionToken": self.csrf_token}
            current_response = requests.post(url, cookies=self.cookies, headers=headers, verify=verify_ssl)
            current_response.raise_for_status()
            return current_response.json()

    def get_auth_token(self):
        """Authenticate and retrieve the ticket and CSRF token."""
        auth_token_response = requests.post(self.auth_url, data={
            "username": username,
            "password": password
        }, verify=verify_ssl
                                            )

        auth_token_response.raise_for_status()

        data = auth_token_response.json()["data"]

        # Return the ticket and CSRF token
        return data["ticket"], data["CSRFPreventionToken"]

    def list_nodes(self, cookies_obj):
        """Retrieve the list of nodes."""
        url = f"{self.api_base_url}/nodes/"
        current_response = requests.get(url, cookies=cookies_obj, verify=verify_ssl)
        current_response.raise_for_status()
        return current_response.json()["data"]

    def list_vms(self, cookies_obj, current_node_name='antares'):
        """Retrieve the list of VMs for a specific node."""
        url = f"{self.api_base_url}/nodes/{current_node_name}/qemu"
        current_response = requests.get(url, cookies=cookies_obj, verify=verify_ssl)
        current_response.raise_for_status()
        return current_response.json()["data"]

    def restart_vm(self, current_cookies, current_csrf_token):
        """Initialize the RestartVM helper class."""
        return self.RestartVM(self, current_cookies, current_csrf_token)


if __name__ == "__main__":
    api = ProxmoxApi(api_base_url=proxmox_api_base_url)
    cookie_handler = CookieHandler(cookie_file)
    try:
        # Load cookie from file if available
        cookies = cookie_handler.load_cookie()

        if not cookies:
            # Authenticate and retrieve ticket if no saved cookie
            print("Authenticating...")
            ticket, csrf_token = api.get_auth_token()
            cookies = {"PVEAuthCookie": ticket}

            # Save the cookie for later use
            cookie_handler.save_cookie(cookies)
            print("Cookie saved.")
        else:
            """ Re-authenticate to get the CSRF token (if needed) """
            ticket, csrf_token = api.get_auth_token()

        # List nodes
        nodes = api.list_nodes(cookies)

        # List VMs for a specific node
        vms = api.list_vms(cookies)

        print("\nVMs:")
        for vm in vms:
            print(f"VMID: {vm['vmid']}, Name: {vm['name']}, Status: {vm['status']}")

        # Restart a specific VM (replace 'node_name' and 'vmid' with actual values)
        node_name = nodes[0]['node']  # Replace with the actual node name
        vm_id = 101  # Replace with the actual VMID
        for vm in vms:
            if vm['name'] == "docker-host":
                vm_id = vm['vmid']

        # Restart a VM by name
        print("\nRestarting VM 'docker-host'...")

        response = api.restart_vm(cookies, csrf_token).by_id(101).exec()
        print("Restart response:", response)

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    except pickle.UnpicklingError:
        print("Failed to load cookies. Please authenticate again.")
