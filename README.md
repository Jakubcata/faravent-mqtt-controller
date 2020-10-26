# FaraVent MQTT Server

Appka napísaná vo [Flasku](https://github.com/pallets/flask) využívajúca [Paho-Mqqt](https://github.com/eclipse/paho.mqtt.python) knižnicu.
Prijíma/posiela správy z daných topic-ov a ukladá ich do (mysql) databazy.

## Features

- A received message is handled (you can do whatever you want with the message) and then saved to a DB
- You can subscribe/unsubscribe to topics by simple API calls and without restart of the app.
- The list of subscribed topics is saved to a DB, so it persists also after a restart of the app.
- You can send a message to a topic via an endpoint

## Installation

### Install system libraries

```
sudo apt install libmysqlclient-dev mosquitto mosquitto-clients
pip install pipenv
```

### Create virtualenv and install packages

```
pipenv install
```

### Setup secrets in `settings.py`

```
cp settings.example.py settings.py
vim settings.py
```

### Run

```
pipenv run python app.py
```

### Setup systemd service (Optional)

```
sudo cp mqtt_controller.service /etc/systemd/system/

# and update the paths of the run scripts
sudo vim /etc/systemd/system/mqtt_controller.service
vim run.sh
sudo systemctl enable mqtt_controller
sudo systemctl start mqtt_controller
```

## Usage

### Endpoints

- GET ``/topics/list/`` - returns list of actually listening topics
- GET ``/topics/subscribe/?topic=`` - subscribe to a topic
- GET ``/topics/unsubscribe/?topic=`` - unsubscribe from a topic
- GET ``/publish/?topic=&message=`` - publish a message to a topic
