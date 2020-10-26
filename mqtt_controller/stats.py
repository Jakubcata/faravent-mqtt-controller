import enum
from datetime import datetime
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
