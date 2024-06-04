import urllib.parse

def generate_google_maps_search_link(place):
    base_url = "https://www.google.com/maps/search/"
    encoded_place = urllib.parse.quote(place)
    search_url = f"{base_url}{encoded_place}"
    return search_url

# Example usage
place = "Banque Cotonou"
search_link = generate_google_maps_search_link(place)
print("Google Maps Search Link:", search_link)
