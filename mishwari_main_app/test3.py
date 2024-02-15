import googlemaps
from geopy.distance import geodesic
from shapely.geometry import Point, LineString

def get_routes(api_key, start, end):
    gmaps = googlemaps.Client(key=api_key)
    directions_result = gmaps.directions(start, end, mode='driving', alternatives=True)
    return directions_result

def calculate_perpendicular_distance(point, line_start, line_end):
    line = LineString([line_start, line_end])
    point_shapely = Point(point)
    perpendicular_point = line.interpolate(line.project(point_shapely))

    if line.project(point_shapely) <= line.length:
        # Use the coordinates of the perpendicular point
        return geodesic((perpendicular_point.x, perpendicular_point.y), point).kilometers
    else:
        # Use the nearest endpoint
        return min(geodesic(line_start, point).kilometers, geodesic(line_end, point).kilometers)


def is_close_to_route(point, route, threshold=1.2):
    for leg in route['legs']:
        for step in leg['steps']:
            start_step = (step['start_location']['lat'], step['start_location']['lng'])
            end_step = (step['end_location']['lat'], step['end_location']['lng'])
            dist = calculate_perpendicular_distance(point, start_step, end_step)
            if dist <= threshold:
                return True
    return False

# Replace with your actual API key
api_key = 'AIzaSyBd16Y-gzEJpKbzYRvTlElqeB2qmd2Jz0A'
start = '14.540446, 49.127974' 
end = '15.949157, 48.810048'  
all_routes = get_routes(api_key, start, end)

# User selects a route
route_number = int(input("Enter the number of the route you want to select: "))
selected_route = all_routes[route_number - 1]

# Example waypoints (replace with actual waypoints)
waypoints = [(15.707222, 48.781184)]  # Replace with real coordinates

# Check which waypoints are close to the selected route
close_waypoints = [wp for wp in waypoints if is_close_to_route(wp, selected_route)]
print("Waypoints close to the route:", close_waypoints)
