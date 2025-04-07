def rgb_to_hex(r, g, b):
    """
    Converts RGB values to a HEX color string.

    Args:
        r (int): Red value (0-255).
        g (int): Green value (0-255).
        b (int): Blue value (0-255).

    Returns:
        str: HEX color string (e.g., "#FFFFFF").
    """
    if not (0 <= r <= 255 and 0 <= g <= 255 and 0 <= b <= 255):
        raise ValueError("RGB values must be in the range 0-255")
    return f"#{r:02x}{g:02x}{b:02x}".upper()


def hex_to_rgb(hex_color):
    """
    Converts a HEX color code to an RGB tuple.

    Args:
        hex_color (str): The HEX color string (e.g., "#FFFFFF" or "FFFFFF").

    Returns:
        tuple: A tuple representing the RGB color (e.g., (255, 255, 255)).
    """
    hex_color = hex_color.lstrip('#')  # Remove '#' if present
    if len(hex_color) != 6:
        raise ValueError("Input should be a 6-character HEX color code.")

    # Split into RGB components
    r = int(hex_color[0:2], 16)  # Red
    g = int(hex_color[2:4], 16)  # Green
    b = int(hex_color[4:6], 16)  # Blue

    return r, g, b
