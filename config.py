class VirtualSensorConfig():
    # Sensor name: [port, range, update interval, coordinates]
    SENSORS = {
        'temperature': {
            'Port': 5556,
            'Range': [-10, 40],
            'Interval': 5,
            'Coordinates': [0, 0]},
        'air_quality': {
            'Port': 5557,
            'Range': [0, 100],
            'Interval': 20,
            'Coordinates': [0, 1]},
        'humidity': {
            'Port': 5558,
            'Rnage': [0, 100],
            'Interval': 5,
            'Coordinates': [1, 1]}
    }
