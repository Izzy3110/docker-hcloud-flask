import os
from datetime import datetime
import hcloud
import humanize
import pytz
from flask import Blueprint, redirect, url_for, current_app, render_template, request, jsonify
from flask_login import current_user

from services.web.app.extensions.csrf import csrf
from services.web.app.wyl import HetznerCloudManager
from dotenv import load_dotenv

load_dotenv('.env')

EXCLUDED_SERVER_NAMES = os.getenv('EXCLUDED_SERVER_NAMES_CS')
exclude_name_list = EXCLUDED_SERVER_NAMES.split(",") if "," in EXCLUDED_SERVER_NAMES else [EXCLUDED_SERVER_NAMES]

servers_bp = Blueprint('servers', __name__)

hcloud_keys = {key: value for key, value in os.environ.items() if key.startswith("HCLOUD_API_")}
hcloud_managers = {}
hcloud_accounts = []
for k, v in hcloud_keys.items():
    account_api_token = v
    hcloud_account_name = k.lstrip('HCLOUD_API_')
    hcloud_accounts.append(hcloud_account_name)
    hcloud_managers[hcloud_account_name] = HetznerCloudManager(account_api_token)


@csrf.exempt
@servers_bp.route('/server_types')
def get_server_types():
    type_names = []
    for account, manager in  hcloud_managers.items():
        for server_type in manager.server_types.get_all():
            if server_type.name not in type_names:
                type_names.append(server_type.name)
        break

    return jsonify({
        "success": True,
        "server_types": type_names
    })


@csrf.exempt
@servers_bp.route("/servers")
def list_servers():
    global exclude_name_list
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))
    local_tz_name = current_app.config["TIMEZONE_NAME"]

    filtered_servers = {}

    for account_no, hcloud_manager in hcloud_managers.items():
        servers_list = hcloud_manager.list_servers()

        filtered_servers[account_no] = [server for server in servers_list if server.name not in exclude_name_list]

        for server in filtered_servers[account_no]:
            # Convert the UTC time to a datetime object (assuming it's a string)
            utc_time_str = server.created.isoformat()  # Assuming server.created is a datetime object
            utc_time = datetime.fromisoformat(utc_time_str)

            # Convert UTC time to local time (e.g., "Europe/Berlin")
            local_tz = pytz.timezone(local_tz_name)
            local_time = utc_time.astimezone(local_tz)

            # Add the converted local time to the server object as created_tz
            server.created_tz = local_time  # Add this new field to the server object

            # Calculate the time difference and convert it to a human-readable string
            delta = datetime.now(local_tz) - local_time
            hours = delta.total_seconds() / 60 / 60
            server.created_delta = humanize.naturaltime(delta)+" "+f"({hours:.2f} h)"

    # Pass the filtered servers to the template
    return render_template("servers.html", servers_list=filtered_servers)


@csrf.exempt
@servers_bp.route("/delete_server/<account_no>/<int:server_id>", methods=["POST"])
def delete_server(account_no, server_id):
    """Delete a server by account and server ID."""
    if account_no in hcloud_managers:
        server = hcloud_managers[account_no].get_by_id(server_id)
        if server:
            hcloud_managers[account_no].delete_server(server_id)

    return redirect(url_for("servers.list_servers"))


@csrf.exempt
@servers_bp.route("/create_server/<account_no>", methods=["POST"])
def create_server(account_no):
    """Create a new server for a specific account."""
    server_name = request.form.get("server_name")
    # print(server_name)

    server_type = request.form.get("server_type")
    image = request.form.get("image")
    location = request.form.get("location")

    if account_no in hcloud_managers:
        try:
            new_server = hcloud_managers[account_no].create_server(
                name=server_name,
                server_type=server_type,
                image=image,
                location=location
            )
            if new_server:
                print(f"Server {server_name} created successfully for account {account_no}.")
        except hcloud.APIException as api_ex:
            print(server_name)
            print(api_ex)

    return redirect(url_for("servers.list_servers"))
