import enum
from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import and_

from mqtt_controller.models import SensorValues


class StatsResampleFunc(enum.Enum):
    Mean = "mean"
    Max = "max"


class Stats:
    def __init__(self, db: SQLAlchemy):
        self.db = db

    def load_data(
        self,
        device_id: int,
        value: str,
        start_date: datetime,
        end_date: datetime,
        resample: Optional[str] = None,
        resample_func: StatsResampleFunc = StatsResampleFunc.Mean,
    ) -> pd.DataFrame:
        query = (
            self.db.query(getattr(SensorValues, value), SensorValues.created)
            .filter(
                and_(
                    SensorValues.device_id == device_id,
                    SensorValues.created >= start_date,
                    SensorValues.created <= end_date,
                )
            )
            .statement
        )
        frame = pd.read_sql(query, self.db.bind)

        # set the time index
        frame.index = pd.to_datetime(frame["created"])

        if resample:
            frame = getattr(frame.resample(resample), resample_func.value)()

        return frame

    def is_movement(
        self,
        device_id: int,
        interval: Optional[timedelta] = None,
        threshold: float = 0.05,
    ) -> bool:
        interval = interval or timedelta(minutes=5)
        frame = self.load_data(
            device_id,
            "movement",
            datetime.now() - interval,
            datetime.now(),
            "2S",
            StatsResampleFunc.Max,
        )
        return frame.mean(axis=0)["movement"] >= threshold

    def get_humidity(
        self, device_id: int, interval: Optional[timedelta] = None
    ) -> float:
        interval = interval or timedelta(minutes=5)
        frame = self.load_data(
            device_id,
            "humidity",
            datetime.now() - interval,
            datetime.now(),
            "2S",
            StatsResampleFunc.Mean,
        )
        return frame.mean(axis=0)["humidity"]

    def get_temperature(
        self, device_id: int, interval: Optional[timedelta] = None
    ) -> float:
        interval = interval or timedelta(minutes=5)
        frame = self.load_data(
            device_id,
            "temperature",
            datetime.now() - interval,
            datetime.now(),
            "2S",
            StatsResampleFunc.Mean,
        )
        return frame.mean(axis=0)["temperature"]
