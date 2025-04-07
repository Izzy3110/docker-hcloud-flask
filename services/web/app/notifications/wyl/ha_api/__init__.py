import os

import requests
from dotenv import load_dotenv

load_dotenv('.env')

API_TOKEN = os.getenv('HA_API')
HOME_ASSISTANT_URL = "https://izzyshome.duckdns.org:8123"  # Update with your HA URL

ha_api_headers = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json",
}


def get_light_state(entity_id):
    """
    Retrieve the current color and brightness of a light entity from Home Assistant.

    Args:
        entity_id (str): The entity ID of the light (e.g., "light.living_room").

    Returns:
        dict: A dictionary with the current state, including RGB color and brightness, or None if the request fails.
    """
    url = f"{HOME_ASSISTANT_URL}/api/states/{entity_id}"

    try:
        response = requests.get(url, headers=ha_api_headers, verify=False)
        if response.status_code == 200:
            data = response.json()
            state = data.get("state", "unknown")
            attributes = data.get("attributes", {})

            friendly_name = attributes.get("friendly_name", None)
            rgb_color = attributes.get("rgb_color", None)
            brightness = attributes.get("brightness", None)

            return {
                "state": state,
                "rgb_color": rgb_color,
                "brightness": brightness,
                "friendly_name": friendly_name
            }
        else:
            print(f"Error retrieving light state: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


def send_assist_command(command):
    url = f"{HOME_ASSISTANT_URL}/api/conversation/process"
    data = {
        "text": command,
    }
    response = requests.post(url, headers=ha_api_headers, json=data, verify=False)
    if response.status_code == 200:
        print("Command processed successfully!")
        print("Response:", response.json())
    else:
        print(f"Failed to process command: {response.status_code}")
        print(response.text)


def set_light_brightness(entity_id, brightness_percent):
    """
    Set the brightness of a light entity in Home Assistant.

    Args:
        entity_id (str): The entity ID of the light (e.g., "light.living_room").
        brightness_percent (float): Brightness as a percentage (0-100).
    """
    url = f"{HOME_ASSISTANT_URL}/api/services/light/turn_on"

    # Convert brightness percentage to a value between 0 and 255
    brightness = int((brightness_percent / 100) * 255)

    data = {
        "entity_id": entity_id,
        "brightness": brightness,  # Brightness level (0-255)
    }

    try:
        response = requests.post(url, headers=ha_api_headers, json=data, verify=False)
        if response.status_code == 200:
            print(f"Brightness for {entity_id} successfully set to {brightness_percent}%!")
        else:
            print(f"Error setting brightness: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"An error occurred: {e}")


def set_light_color(entity_id, r, g, b):
    url = f"{HOME_ASSISTANT_URL}/api/services/light/turn_on"
    data = {
        "entity_id": entity_id,
        "rgb_color": [r, g, b],  # RGB-Werte für die Farbe
    }
    response = requests.post(url, headers=ha_api_headers, json=data, verify=False)
    if response.status_code == 200:
        print(f"Farbe für {entity_id} erfolgreich geändert!")
    else:
        print(f"Fehler beim Ändern der Farbe: {response.status_code}")
        print(response.text)
