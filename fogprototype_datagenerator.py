# 1st virtual sensor: temperature
# 2nd virtual sensor: air quality
# 3rd virtual sensor: magnitude

import random
import decimal

import datetime
import jwt
#import paho.mqtt.client as mqtt

# 1. Use MQTT client library for connection to Google Cloud

# JWT configuration function: https://cloud.google.com/iot/docs/how-tos/credentials/jwts?hl=de#iot-core-jwt-nodejs

def create_jwt(project_id, private_key_file, algorithm):
    """Creates a JWT (https://jwt.io) to establish an MQTT connection.
    Args:
     project_id: The cloud project ID this device belongs to
     private_key_file: A path to a file containing either an RSA256 or
             ES256 private key.
     algorithm: The encryption algorithm to use. Either 'RS256' or 'ES256'
    Returns:
        A JWT generated from the given project_id and private key, which
        expires in 20 minutes. After 20 minutes, your client will be
        disconnected, and a new JWT will have to be generated.
    Raises:
        ValueError: If the private_key_file does not contain a known key.
    """

    token = {
        # The time that the token was issued at
        "iat": datetime.datetime.now(tz=datetime.timezone.utc),
        # The time the token expires.
        "exp": datetime.datetime.now(tz=datetime.timezone.utc) + datetime.timedelta(minutes=20),
        # The audience field should always be set to the GCP project id.
        "aud": project_id,
    }

    # Read the private key file.
    with open(private_key_file) as f:
        private_key = f.read()

    print(
        "Creating JWT using {} from private key file {}".format(
            algorithm, private_key_file
        )
    )

    return jwt.encode(token, private_key, algorithm=algorithm)

# 2. Publish data to cloud (Publishing function publishAsync)
# 3. Subscribe to topic (Subscribing (no function))

# generating random data 
# random values 
random_values_virtual_sensor1 = random.randint(-20, 40)
random_values_virtual_sensor2 = random.randint(0, 500)
random_values_virtual_sensor3 = round(decimal.Decimal(random.randrange(100, 900))/100, 1)

virtual_sensors = {
    'temperature': random_values_virtual_sensor1,
    'air quality': random_values_virtual_sensor2,
    'magnitude': random_values_virtual_sensor3
}

print(virtual_sensors)
