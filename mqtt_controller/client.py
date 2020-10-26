from typing import Any, Callable, List, Optional

import paho.mqtt.client as mqtt
import structlog

from settings import MQTT_PASSWORD, MQTT_USER

log = structlog.get_logger()


class MQTTClient:
    def __init__(
        self,
        host: str,
        topics: List[str],
        on_message_callback: Callable[[str, str], None],
    ):
        self.host = host
        self.topics = set(topics)
        self.client: Optional[mqtt.Client] = None
        self.on_message_callback = on_message_callback

    def subscribe_topic(self, topic: str) -> None:
        if not self.client:
            raise Exception("MQTT client is not running!")

        if topic not in self.topics:
            self.topics.add(topic)
            self.client.subscribe(topic)
            log.info("mqtt_client.topic.subscribed", topic=topic)
            return
        else:
            log.warning("mqtt_client.topic.already_subscribed", topic=topic)
            return

    def unsubscribe_topic(self, topic: str) -> None:
        if not self.client:
            raise Exception("MQTT client is not running!")

        if topic in self.topics:
            self.topics.remove(topic)
            self.client.unsubscribe(topic)
            log.info("mqtt_client.topic.unsubscribed", topic=topic)
            return
        else:
            log.warning("mqtt_client.topic.not_subscribed", topic=topic)

    def on_connect(self, client: Any, _: Any, __: Any, rc: int) -> None:
        """The callback for when the client receives a CONNACK response from the server."""
        log.info("mqtt_client.network.connected", result_code=rc)

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        for topic in self.topics:
            client.subscribe(topic)
            log.info("mqtt_client.topic.subscribed", topic=topic)

    def on_message(self, _: Any, __: Any, msg: mqtt.MQTTMessage) -> None:
        """The callback for when a PUBLISH message is received from the server."""

        try:
            log.info(
                "mqtt_client.network.received",
                topic=msg.topic,
                payload=msg.payload.decode(),
            )
            self.on_message_callback(msg.topic, msg.payload)
        except Exception:
            log.exception("mqtt_client.network.error")

    def send_message(self, topic: str, message: str) -> None:
        self.client.publish(topic, message)
        log.info("mqtt_client.network.sent", topic=topic, message=message)

    def start(self) -> None:

        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.username_pw_set(username=MQTT_USER, password=MQTT_PASSWORD)
        self.client.connect(self.host, 1883, 60)

        self.client.loop_start()

    def stop(self) -> None:
        self.client.loop_stop()
        self.client = None
