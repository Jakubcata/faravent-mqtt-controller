import json
from datetime import datetime

import structlog
from envparse import Env
from flask import Flask, jsonify, request
from flask_cors import CORS
from kw.structlog_config.config import configure_stdlib_logging, configure_structlog

from mqtt_controller.client import MQTTClient
from mqtt_controller.models import Message, SensorValues, Topic, db
from mqtt_controller.qr_code import cz_code, eur_code
from settings import DATABASE_URL, MQTT_HOST

# Debug and Logging
env = Env(DEBUG=bool)

DEBUG = env("DEBUG", default=True)

configure_structlog(DEBUG, timestamp_format="iso")
configure_stdlib_logging(DEBUG, timestamp_format="iso")

app = Flask(__name__)
CORS(app)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
db.init_app(app)


log = structlog.get_logger()


def parse_message(topic: str, message: str) -> None:
    try:
        json_message = json.loads(message)
        result = db.session.execute(
            "select id from devices where out_topic= :out_topic", {"out_topic": topic}
        )
        device_id = next(result)[0]
        db.session.add(
            SensorValues(
                device_id=device_id,
                temperature=json_message.get("temp"),
                humidity=json_message.get("hum"),
                movement=json_message.get("movmnt"),
                signal=json_message.get("signl"),
                version=json_message.get("version"),
                created=datetime.now(),
            )
        )
    except Exception:
        log.exception("api.mqtt_callback.parse_message")


def on_message_callback(topic: str, message: str) -> None:
    log.info("api.mqtt_callback.parse_message", topic=topic, message=message)
    with app.app_context():
        db.session.add(
            Message(
                type="received", topic=topic, message=message, created=datetime.now()
            )
        )
        parse_message(topic, message)
        db.session.commit()
    log.info("api.mqtt_callback.parse_message.saved")


with app.app_context():
    # db.create_all()
    db_topics = [topic.name for topic in db.session.query(Topic).all()]
    mqtt_client = MQTTClient(MQTT_HOST, db_topics, on_message_callback)
    mqtt_client.start()


@app.route("/topics/list")
def topics() -> str:
    return jsonify({"topics": sorted(list(mqtt_client.topics))})


@app.route("/topics/subscribe")
def subscribe_topic() -> str:
    topic = request.args["topic"]
    mqtt_client.subscribe_topic(topic)
    db.session.add(Topic(name=topic, created=datetime.now()))
    db.session.commit()
    return jsonify({"topics": sorted(list(mqtt_client.topics))})


@app.route("/topics/unsubscribe")
def unsubscribe_topic() -> str:
    topic = request.args["topic"]
    mqtt_client.unsubscribe_topic(topic)
    db.session.delete(db.session.query(Topic).filter_by(name=topic).first())
    db.session.commit()
    return jsonify({"topics": sorted(list(mqtt_client.topics))})


@app.route("/publish")
def send_message() -> str:
    topic = request.args["topic"]
    message = request.args["message"]

    mqtt_client.send_message(topic, message)
    db.session.add(
        Message(type="sent", topic=topic, message=message, created=datetime.now())
    )
    db.session.commit()
    return jsonify({"topic": topic, "message": message, "status": "sent"})


@app.route("/qrcode")
def qr_code() -> str:
    currency = request.args["currency"]
    amount = request.args["amount"]
    message = request.args.get("message", "")
    if currency == "czk":
        return jsonify({"message": cz_code(amount, message)})
    return jsonify({"message": eur_code(amount, message)})


@app.route("/ping")
def ping() -> str:
    return jsonify({"message": "Pong."})


if __name__ == "__main__":
    app.run()
