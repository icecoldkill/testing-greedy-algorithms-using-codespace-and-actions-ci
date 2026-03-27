import math

from tsm import haversine, nearest_neighbor_tsp, route_distance, run_simulations_all_starts


def test_haversine_zero_distance():
    assert haversine((0, 0), (0, 0)) == 0.0


def test_haversine_known_distance():
    # approx distance London (51.5074,-0.1278) to Paris (48.8566,2.3522)
    dist = haversine((51.5074, -0.1278), (48.8566, 2.3522))
    assert 340 <= dist <= 350


def test_nearest_neighbor_tsp_triangle():
    locations = [
        {"city": "A", "latitude": 0.0, "longitude": 0.0},
        {"city": "B", "latitude": 0.0, "longitude": 1.0},
        {"city": "C", "latitude": 1.0, "longitude": 0.0},
    ]
    route = nearest_neighbor_tsp(locations, start_index=0)
    assert route[0] == 0
    assert route[-1] == 0
    assert set(route[:-1]) == {0, 1, 2}


def test_route_distance_is_symmetric():
    locations = [
        {"city": "A", "latitude": 0.0, "longitude": 0.0},
        {"city": "B", "latitude": 0.0, "longitude": 1.0},
    ]
    route = [0, 1, 0]
    d = route_distance(route, locations)
    assert math.isclose(d, 2 * haversine((0, 0), (0, 1)), rel_tol=1e-9)


def test_run_simulations_all_starts_returns_sorted():
    locations = [
        {"city": "A", "latitude": 0.0, "longitude": 0.0},
        {"city": "B", "latitude": 0.0, "longitude": 1.0},
        {"city": "C", "latitude": 0.0, "longitude": 2.0},
    ]
    results = run_simulations_all_starts(locations)
    assert len(results) == 3
    distances = [r["distance_km"] for r in results]
    assert distances == sorted(distances)
