import json

data = json.load(open("settings.json"))

DATABASE_URL = data["DATABASE_URL"]
FLASK_URL = data["FLASK_URL"]

MQTT_USER = data["MQTT_USER"]
MQTT_PASSWORD = data["MQTT_PASSWORD"]
MQTT_HOST = data["MQTT_HOST"]
MQTT_TOPICS = data["MQTT_TOPICS"]
