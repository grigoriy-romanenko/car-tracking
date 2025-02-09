import math
import config
import random
import folium
from math import atan2, degrees, radians
from geographiclib.geodesic import Geodesic

def get_azimuth(x, y, a, w=config.original_image_width, h=config.original_image_height):
    dist = min(w, h) / 2
    a0 = -1 if a < 0 else 1
    x0 = w/2 + dist * math.cos(math.atan2(-dist, 0) - a0 * abs(radians(a)))
    y0 = h/2 + dist * math.sin(math.atan2(-dist, 0) - a0 * abs(radians(a)))
    deg1 = (360 + degrees(atan2(x0 - w/2, y0 - h/2))) % 360
    deg2 = (360 + degrees(atan2(x - w/2, y - h/2))) % 360
    return abs(360 - deg2 + deg1) if deg1 <= deg2 else abs(deg2 - deg1)

def get_distance(x, y, flight_height,
                 sensor_width=config.sensor_width, sensor_height=config.sensor_height, focal_length=config.focal_length,
                 image_width=config.original_image_width, image_height=config.original_image_height):
    gsd_w = flight_height * sensor_width / (focal_length * image_width)
    gsd_h = flight_height * sensor_height / (focal_length * image_height)
    return math.sqrt(((max(x, image_width / 2) - min(x, image_width / 2)) * gsd_w) ** 2
                     + ((max(y, image_height / 2) - min(y, image_height / 2)) * gsd_h) ** 2)

def get_location(detection, metrics):
    distance = get_distance(detection.x, detection.y, metrics.altitude)
    azimuth = get_azimuth(detection.x, detection.y, metrics.azimuth)
    location = Geodesic.WGS84.Direct(metrics.latitude, metrics.longitude, azimuth, distance)
    return location['lat2'], location['lon2']

def make_map(metrics, tracks):
    m = folium.Map(location=(metrics[0].latitude, metrics[0].longitude), zoom_start=15)
    track_coordinates = list(map(lambda x: (x.latitude, x.longitude), metrics))
    folium.PolyLine(track_coordinates, tooltip="drone").add_to(m)
    rand = lambda: random.randint(0,255)
    for track_id, track in tracks.items():
        track_coordinates = list(map(lambda detection: get_location(detection, metrics[detection.frame_num]), track))
        color = "#%02x%02x%02x" % (rand(), rand(), rand())
        folium.PolyLine(track_coordinates, tooltip=f"car-{track_id}", color=color).add_to(m)
    m.save(config.map_file_path)
