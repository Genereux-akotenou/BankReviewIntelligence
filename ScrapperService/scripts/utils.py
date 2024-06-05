import re
import json


class Utils:

    @staticmethod
    def is_phone_number(text):
        phone_pattern = re.compile(r"^\+?\d[\d\s-]{8,}\d$")
        return bool(phone_pattern.match(text))

    @staticmethod
    def is_website_url(text):
        url_pattern = re.compile(
            r'^(https?:\/\/)?'
            r'([\da-z\.-]+)\.'
            r'([a-z\.]{2,6})'
            r'([\/\w \.-]*)*\/?$'
        )
        return bool(url_pattern.match(text))

    @staticmethod
    def throw_error(e):
        print(f"Error: {e}")

    @staticmethod
    def load_cities(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
        
    @staticmethod
    def generate_google_maps_link(address):
        import urllib.parse
        base_url = "https://www.google.com/maps/search/?api=1&query="
        url_safe_address = urllib.parse.quote(address)
        return base_url + url_safe_address
