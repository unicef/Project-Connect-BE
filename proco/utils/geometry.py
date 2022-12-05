import math


def cartesian(latitude, longitude):
    # Convert to radians
    latitude = latitude * (math.pi / 180)
    longitude = longitude * (math.pi / 180)

    earth_radius = 6371  # 6378137.0 + elevation  # relative to centre of the earth
    x_coord = earth_radius * math.cos(latitude) * math.cos(longitude)
    y_coord = earth_radius * math.cos(latitude) * math.sin(longitude)
    z_coord = earth_radius * math.sin(latitude)
    return x_coord, y_coord, z_coord
