
from datetime import datetime, timezone
from pathlib import Path
import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field, model_validator

app = FastAPI(title="SALT-LINE API", version="0.2.0")

# Always use the database beside this Python file.
DB_NAME = Path(__file__).resolve().parent / "saltline.db"


def initialize_database():
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS sensor_readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                uptime_ms INTEGER NOT NULL DEFAULT 0,
                tds_raw_avg INTEGER NOT NULL,
                water_level_raw_avg INTEGER NOT NULL,
                tds_voltage_est_v REAL NOT NULL,
                water_voltage_est_v REAL NOT NULL,
                temperature_c REAL,
                temperature_valid BOOLEAN NOT NULL DEFAULT 0,
                input_warning BOOLEAN NOT NULL,
                source TEXT NOT NULL,
                received_at TEXT NOT NULL
            )
        """)

        # Migrate existing databases without deleting old records.
        existing_columns = {
            row[1]
            for row in conn.execute(
                "PRAGMA table_info(sensor_readings)"
            ).fetchall()
        }

        migrations = {
            "uptime_ms": "INTEGER NOT NULL DEFAULT 0",
            "temperature_c": "REAL",
            "temperature_valid": "BOOLEAN NOT NULL DEFAULT 0"
        }

        for column, definition in migrations.items():
            if column not in existing_columns:
                conn.execute(
                    f"ALTER TABLE sensor_readings "
                    f"ADD COLUMN {column} {definition}"
                )


initialize_database()


class SensorReading(BaseModel):
    model_config = ConfigDict(extra="forbid")

    device_id: str = Field(min_length=1)
    uptime_ms: int = Field(ge=0)

    tds_raw_avg: int = Field(ge=0, le=4095)
    water_level_raw_avg: int = Field(ge=0, le=4095)

    tds_voltage_est_v: float = Field(ge=0, le=3.3)
    water_voltage_est_v: float = Field(ge=0, le=3.3)

    temperature_c: float | None = Field(
        default=None, ge=-55, le=125
    )
    temperature_valid: bool = False

    input_warning: bool
    source: str = Field(min_length=1)

    @model_validator(mode="after")
    def validate_temperature(self):
        if self.temperature_valid and self.temperature_c is None:
            raise ValueError(
                "temperature_c is required when temperature_valid is true"
            )
        return self


@app.get("/")
def home():
    return {
        "project": "SALT-LINE",
        "status": "Backend running",
        "version": "0.2.0"
    }


@app.post("/api/v1/sensor-readings")
def receive_sensor_data(data: SensorReading):

    received_at = datetime.now(timezone.utc).isoformat()

    with sqlite3.connect(DB_NAME) as conn:
        cursor = conn.execute("""
            INSERT INTO sensor_readings (
                device_id,
                uptime_ms,
                tds_raw_avg,
                water_level_raw_avg,
                tds_voltage_est_v,
                water_voltage_est_v,
                temperature_c,
                temperature_valid,
                input_warning,
                source,
                received_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            data.device_id,
            data.uptime_ms,
            data.tds_raw_avg,
            data.water_level_raw_avg,
            data.tds_voltage_est_v,
            data.water_voltage_est_v,
            data.temperature_c,
            data.temperature_valid,
            data.input_warning,
            data.source,
            received_at
        ))

        reading_id = cursor.lastrowid

    return {
        "success": True,
        "message": "Sensor reading stored",
        "reading_id": reading_id,
        "device_id": data.device_id,
        "received_at": received_at
    }


@app.get("/api/v1/sensor-readings")
def get_sensor_readings():

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT * FROM sensor_readings
            ORDER BY id DESC
            LIMIT 50
        """).fetchall()

    readings = []

    for row in rows:
        reading = dict(row)
        reading["input_warning"] = bool(reading["input_warning"])
        reading["temperature_valid"] = bool(
            reading["temperature_valid"]
        )
        readings.append(reading)

    return {
        "count": len(readings),
        "readings": readings
    }


@app.get("/api/v1/sensor-readings/{reading_id}")
def get_sensor_reading(reading_id: int):

    with sqlite3.connect(DB_NAME) as conn:
        conn.row_factory = sqlite3.Row

        row = conn.execute("""
            SELECT * FROM sensor_readings
            WHERE id = ?
        """, (reading_id,)).fetchone()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Sensor reading not found"
        )

    reading = dict(row)
    reading["input_warning"] = bool(reading["input_warning"])
    reading["temperature_valid"] = bool(
        reading["temperature_valid"]
    )

    return reading
