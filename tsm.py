"""use click to create a command line interface for running TSP simulations with geocoded cities. and use geopy to geocode city names to lat/lon coordinates. implement a nearest neighbor heuristic for TSP and allow running simulations starting from each city. output results sorted by total distance. It should be possible to run the script and see the results in the terminal. Also include a test suite using pytest to validate the functionality of the haversine function, nearest neighbor TSP, route distance calculation, and the overall simulation process."""

try:
    from geopy.geocoders import Nominatim
    from geopy.exc import GeocoderTimedOut
except ModuleNotFoundError:
    Nominatim = None

    class GeocoderTimedOut(Exception):
        pass

try:
    import click
except ModuleNotFoundError:
    click = None

from math import radians, sin, cos, sqrt, atan2
import random
import time

if Nominatim is not None:
    geolocator = Nominatim(user_agent="tsp_example")
else:
    geolocator = None


def geocode_city(city_name, retries=3):
    if geolocator is None:
        raise RuntimeError("geopy is required for geocoding. install geopy or skip geocoding tests")

    for i in range(retries):
        try:
            return geolocator.geocode(city_name, timeout=10)
        except GeocoderTimedOut:
            time.sleep(1)
    return None


def haversine(coord1, coord2):
    lat1, lon1 = map(radians, coord1)
    lat2, lon2 = map(radians, coord2)
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    R = 6371.0
    return R * c


def build_locations(city_names, max_cities=None, randomize=True):
    names = city_names.copy()
    if randomize:
        random.shuffle(names)

    locations = []
    for city in names:
        loc = geocode_city(city)
        if not loc:
            print(f"Geocode failed: {city}")
            continue

        locations.append({
            "city": city,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
        })

        if max_cities and len(locations) >= max_cities:
            break

    return locations


def route_distance(route_indices, locations):
    total = 0.0
    for i in range(len(route_indices) - 1):
        a = locations[route_indices[i]]
        b = locations[route_indices[i + 1]]
        total += haversine(
            (a["latitude"], a["longitude"]),
            (b["latitude"], b["longitude"]),
        )
    return total


def nearest_neighbor_tsp(locations, start_index=0):
    n = len(locations)
    if n == 0:
        return []

    visited = {start_index}
    current = start_index
    route = [current]

    while len(visited) < n:
        next_city = min(
            (i for i in range(n) if i not in visited),
            key=lambda i: haversine(
                (locations[current]["latitude"], locations[current]["longitude"]),
                (locations[i]["latitude"], locations[i]["longitude"]),
            ),
        )
        route.append(next_city)
        visited.add(next_city)
        current = next_city

    route.append(start_index)  # close loop
    return route


def run_simulations_all_starts(locations):
    all_results = []
    for start in range(len(locations)):
        route = nearest_neighbor_tsp(locations, start_index=start)
        dist = route_distance(route, locations)
        all_results.append({
            "start_index": start,
            "start_city": locations[start]["city"],
            "route": route,
            "distance_km": dist,
            "route_cities": [locations[i]["city"] for i in route],
        })

    all_results.sort(key=lambda item: item["distance_km"])
    return all_results


def run_tsp_cities(city_names=None, max_cities=8, randomize=True):
    sample_cities = [
        "New York, USA",
        "Los Angeles, USA",
        "Chicago, USA",
        "Houston, USA",
        "Phoenix, USA",
        "Philadelphia, USA",
        "San Antonio, USA",
        "San Diego, USA",
        "Dallas, USA",
        "San Jose, USA",
        "Austin, USA",
        "Jacksonville, USA",
    ]

    if not city_names:
        city_names = sample_cities

    city_locations = build_locations(city_names, max_cities=max_cities, randomize=randomize)
    if not city_locations:
        raise RuntimeError("No cities were geocoded successfully")

    click_or_print = []
    print("\nLoaded cities:")
    for idx, loc in enumerate(city_locations):
        print(f"{idx:2d}. {loc['city']} ({loc['latitude']:.6f}, {loc['longitude']:.6f})")

    all_simulations = run_simulations_all_starts(city_locations)

    print("\nSimulation results (sorted by total distance):")
    for sim in all_simulations:
        print(f"\nStart {sim['start_index']} {sim['start_city']} - {sim['distance_km']:.2f} km")
        print("Route:")
        print(" -> ".join(sim["route_cities"]))

    saved_routes = all_simulations
    print(f"\nSaved {len(saved_routes)} simulation outputs in variable 'saved_routes'")
    return saved_routes


if click is not None:
    @click.command(name="tsp-sim")
    @click.option("--max-cities", default=8, show_default=True, type=int,
                  help="Maximum number of cities to include")
    @click.option("--randomize/--no-randomize", default=True,
                  help="Randomize city order before building locations")
    @click.option("--city", "city_names", multiple=True,
                  help="City names to geocode (repeat option to add more)")
    def cli(max_cities, randomize, city_names):
        """Run TSP nearest neighbor simulation on geocoded city names."""
        names = list(city_names) if city_names else None
        run_tsp_cities(city_names=names, max_cities=max_cities, randomize=randomize)

    if __name__ == "__main__":
        cli()
else:
    if __name__ == "__main__":
        print("Click is not installed. Run with python tsm.py after installing click: pip install click")
        run_tsp_cities()

