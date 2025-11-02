"""
Navigation Manager - Directions, location, nearby places, distance calculations
"""

import os
import logging
import requests
import math

logger = logging.getLogger(__name__)


class NavigationManager:
    """Manage navigation and location features"""

    def __init__(self):
        """Initialize navigation manager"""

        # Google Maps API key (optional but recommended)
        self.google_maps_api_key = os.getenv('GOOGLE_MAPS_API_KEY')

        # OpenStreetMap Nominatim for geocoding (free, no key needed)
        self.nominatim_url = "https://nominatim.openstreetmap.org"

        # User agent for Nominatim (required)
        self.user_agent = "SmartGlasses/1.0"

        logger.info("Navigation Manager initialized")

    def get_current_location(self):
        """Get current location using IP geolocation (approximate)"""
        try:
            # Using ip-api.com (free, no key needed)
            response = requests.get("http://ip-api.com/json/", timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('status') == 'success':
                city = data.get('city', 'Unknown')
                region = data.get('regionName', '')
                country = data.get('country', '')
                lat = data.get('lat', 0)
                lon = data.get('lon', 0)

                location_text = f"You appear to be in {city}"
                if region:
                    location_text += f", {region}"
                if country:
                    location_text += f", {country}"

                logger.info(f"Current location: {city}, {region}, {country}")
                return location_text

            return "Couldn't determine current location"

        except requests.exceptions.RequestException as e:
            logger.error(f"Location error: {e}")
            return "Couldn't determine current location"

    def geocode_address(self, address):
        """Convert address to coordinates using Nominatim"""
        try:
            url = f"{self.nominatim_url}/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1
            }
            headers = {'User-Agent': self.user_agent}

            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data and len(data) > 0:
                result = data[0]
                lat = float(result['lat'])
                lon = float(result['lon'])
                display_name = result.get('display_name', address)

                return {
                    'lat': lat,
                    'lon': lon,
                    'name': display_name
                }

            return None

        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None

    def reverse_geocode(self, lat, lon):
        """Convert coordinates to address"""
        try:
            url = f"{self.nominatim_url}/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json'
            }
            headers = {'User-Agent': self.user_agent}

            response = requests.get(url, params=params, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()

            if 'display_name' in data:
                return data['display_name']

            return None

        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None

    def get_directions(self, origin, destination):
        """Get directions between two locations"""
        if self.google_maps_api_key:
            return self._get_directions_google(origin, destination)
        else:
            return self._get_directions_basic(origin, destination)

    def _get_directions_google(self, origin, destination):
        """Get directions using Google Maps API"""
        try:
            url = "https://maps.googleapis.com/maps/api/directions/json"
            params = {
                'origin': origin,
                'destination': destination,
                'key': self.google_maps_api_key,
                'mode': 'driving'
            }

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'OK' or 'routes' not in data or len(data['routes']) == 0:
                return f"Couldn't get directions from {origin} to {destination}"

            route = data['routes'][0]
            leg = route['legs'][0]

            distance = leg['distance']['text']
            duration = leg['duration']['text']
            start = leg['start_address']
            end = leg['end_address']

            # Get first few steps
            steps = leg.get('steps', [])[:3]
            directions_text = f"Directions from {start} to {end}. "
            directions_text += f"Total distance: {distance}, estimated time: {duration}. "

            if steps:
                directions_text += "First steps: "
                for i, step in enumerate(steps, 1):
                    instruction = step['html_instructions']
                    # Remove HTML tags
                    import re
                    instruction = re.sub('<[^<]+?>', '', instruction)
                    directions_text += f"{i}. {instruction}. "

            logger.info(f"Directions: {origin} to {destination}")
            return directions_text.strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Directions API error: {e}")
            return "Couldn't get directions"

    def _get_directions_basic(self, origin, destination):
        """Get basic directions without Google Maps (just distance/bearing)"""
        origin_coords = self.geocode_address(origin)
        dest_coords = self.geocode_address(destination)

        if not origin_coords or not dest_coords:
            return f"Couldn't find locations for directions. Set GOOGLE_MAPS_API_KEY for full directions."

        distance_km = self.calculate_distance(
            origin_coords['lat'], origin_coords['lon'],
            dest_coords['lat'], dest_coords['lon']
        )

        distance_mi = distance_km * 0.621371

        bearing = self.calculate_bearing(
            origin_coords['lat'], origin_coords['lon'],
            dest_coords['lat'], dest_coords['lon']
        )

        direction_text = f"From {origin} to {destination}: "
        direction_text += f"approximately {distance_mi:.1f} miles ({distance_km:.1f} km) "
        direction_text += f"heading {bearing}. "
        direction_text += "For turn-by-turn directions, set GOOGLE_MAPS_API_KEY."

        return direction_text

    def find_nearby_places(self, location, place_type=None):
        """Find nearby places (requires Google Maps API)"""
        if not self.google_maps_api_key:
            return "Nearby places search requires GOOGLE_MAPS_API_KEY environment variable."

        # Get coordinates for location
        coords = self.geocode_address(location)
        if not coords:
            return f"Couldn't find location: {location}"

        try:
            url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            params = {
                'location': f"{coords['lat']},{coords['lon']}",
                'radius': 1000,  # 1km radius
                'key': self.google_maps_api_key
            }

            if place_type:
                params['type'] = place_type

            response = requests.get(url, params=params, timeout=5)
            response.raise_for_status()
            data = response.json()

            if data.get('status') != 'OK' or 'results' not in data:
                return f"No nearby places found"

            results = data['results'][:5]

            result_text = f"Found {len(results)} nearby places"
            if place_type:
                result_text += f" (type: {place_type})"
            result_text += ": "

            for i, place in enumerate(results, 1):
                name = place.get('name', 'Unknown')
                vicinity = place.get('vicinity', '')
                rating = place.get('rating', '')

                result_text += f"{i}. {name}"
                if vicinity:
                    result_text += f" at {vicinity}"
                if rating:
                    result_text += f", rated {rating} stars"
                result_text += ". "

            logger.info(f"Nearby places: {location}, type: {place_type}")
            return result_text.strip()

        except requests.exceptions.RequestException as e:
            logger.error(f"Nearby places error: {e}")
            return "Couldn't search for nearby places"

    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates in kilometers (Haversine formula)"""
        # Earth radius in kilometers
        R = 6371.0

        # Convert to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)

        # Haversine formula
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad

        a = math.sin(dlat / 2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon / 2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        distance = R * c

        return distance

    def calculate_bearing(self, lat1, lon1, lat2, lon2):
        """Calculate compass bearing between two points"""
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        dlon_rad = math.radians(lon2 - lon1)

        y = math.sin(dlon_rad) * math.cos(lat2_rad)
        x = math.cos(lat1_rad) * math.sin(lat2_rad) - math.sin(lat1_rad) * math.cos(lat2_rad) * math.cos(dlon_rad)

        bearing_rad = math.atan2(y, x)
        bearing_deg = math.degrees(bearing_rad)
        bearing_deg = (bearing_deg + 360) % 360

        # Convert to compass direction
        directions = ['north', 'northeast', 'east', 'southeast', 'south', 'southwest', 'west', 'northwest']
        index = round(bearing_deg / 45) % 8

        return directions[index]

    def get_distance_between(self, location1, location2):
        """Get distance between two locations"""
        coords1 = self.geocode_address(location1)
        coords2 = self.geocode_address(location2)

        if not coords1:
            return f"Couldn't find location: {location1}"
        if not coords2:
            return f"Couldn't find location: {location2}"

        distance_km = self.calculate_distance(
            coords1['lat'], coords1['lon'],
            coords2['lat'], coords2['lon']
        )

        distance_mi = distance_km * 0.621371

        result = f"Distance from {location1} to {location2}: "
        result += f"{distance_mi:.1f} miles ({distance_km:.1f} kilometers)"

        logger.info(f"Distance: {location1} to {location2} = {distance_km:.1f} km")
        return result

    def search_place(self, query):
        """Search for a place by name"""
        coords = self.geocode_address(query)

        if not coords:
            return f"Couldn't find location: {query}"

        name = coords.get('name', query)
        lat = coords.get('lat')
        lon = coords.get('lon')

        result = f"Found: {name}. "
        result += f"Coordinates: {lat:.4f}, {lon:.4f}"

        logger.info(f"Place search: {query}")
        return result
