from sqlalchemy import Boolean, Float, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Component(Base):
    __tablename__ = "components"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(60), nullable=False, index=True)
    voltage_min: Mapped[float | None] = mapped_column(Float)
    voltage_max: Mapped[float | None] = mapped_column(Float)
    typical_current_mA: Mapped[float] = mapped_column(Float, default=0)
    max_current_mA: Mapped[float | None] = mapped_column(Float)
    startup_current_mA: Mapped[float | None] = mapped_column(Float)
    stall_current_mA: Mapped[float | None] = mapped_column(Float)
    recommended_gpio_current_mA: Mapped[float | None] = mapped_column(Float)
    logic_voltage: Mapped[float | None] = mapped_column(Float)
    gpio_safe: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_driver: Mapped[bool] = mapped_column(Boolean, default=False)
    is_high_current: Mapped[bool] = mapped_column(Boolean, default=False)
    is_logic_sensitive: Mapped[bool] = mapped_column(Boolean, default=False)
    is_inductive: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str | None] = mapped_column(Text)
    common_warning: Mapped[str | None] = mapped_column(Text)
    beginner_tip: Mapped[str | None] = mapped_column(Text)


class PowerSource(Base):
    __tablename__ = "power_sources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    voltage: Mapped[float] = mapped_column(Float, nullable=False)
    max_current_mA: Mapped[float] = mapped_column(Float, nullable=False)
    capacity_mAh: Mapped[float | None] = mapped_column(Float)
    internal_resistance_ohm: Mapped[float] = mapped_column(Float, default=0.08)
    source_type: Mapped[str] = mapped_column(String(60), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text)
    beginner_tip: Mapped[str | None] = mapped_column(Text)


class Regulator(Base):
    __tablename__ = "regulators"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    regulator_type: Mapped[str] = mapped_column(String(40), nullable=False)
    input_voltage_min: Mapped[float | None] = mapped_column(Float)
    input_voltage_max: Mapped[float | None] = mapped_column(Float)
    output_voltage_options: Mapped[list[float]] = mapped_column(JSON, default=list)
    max_current_mA: Mapped[float] = mapped_column(Float, nullable=False)
    efficiency: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    beginner_tip: Mapped[str | None] = mapped_column(Text)


class ExampleProject(Base):
    __tablename__ = "example_projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False, unique=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    components: Mapped[list[dict]] = mapped_column(JSON, default=list)
    power_source: Mapped[str] = mapped_column(String(120), nullable=False)
    expected_notes: Mapped[list[str]] = mapped_column(JSON, default=list)
