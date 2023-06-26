from virtual_sensor import VirtualSensor
from multiprocessing import Process


def humidity_sensor():
    virtual_sensor2 = VirtualSensor(5555, "humidity")
    virtual_sensor2.start_sensor(100, (0, 100), 5)

def temperature_sensor():
    virtual_sensor1 = VirtualSensor(5556, "temperature")
    virtual_sensor1.start_sensor(100, (-20, 38), 1)

def air_quality_sensor():
    virtual_sensor3 = VirtualSensor(5557, "air quality")
    virtual_sensor3.start_sensor(100, (0, 100), 1)

def magnitude_sensor():
    virtual_sensor4 = VirtualSensor(5558, "magnitude")
    virtual_sensor4.start_sensor(100, (0, 10), 2)


def message_broker():
    pass


if __name__ == '__main__':
    p1 = Process(target=temperature_sensor)
    p2 = Process(target=humidity_sensor)
    p3 = Process(target=air_quality_sensor)
    p4 = Process(target=magnitude_sensor)
    p5 = Process(target=message_broker)

    p5.start()
    p1.start()
    p2.start()
    p3.start()
    p4.start()


