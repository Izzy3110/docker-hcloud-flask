import os
import pickle
from typing import Any


def check_first_last_char(string, char):
    if not string:  # Check if the string is empty
        return False
    return string[0] == char or string[-1] == char


def has_double_char(string, char):
    double_char = char * 2
    return double_char in string


class CookieHandler:
    def __init__(self, cookie_file):
        self.cookie_file = cookie_file

    def save_cookie(self, cookies_: Any):
        """Save the cookies to a file."""
        with open(self.cookie_file, "wb") as f_:  # Explicit binary write mode
            pickle.dump(cookies_, f_)

    def load_cookie(self):
        """Load the cookies from a file."""
        if os.path.exists(self.cookie_file):
            with open(self.cookie_file, "rb") as f:
                return pickle.load(f)
        return None
