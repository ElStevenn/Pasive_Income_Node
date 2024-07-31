from sqlalchemy import String, UUID, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID as pgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase
import uuid

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "user"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(256), nullable=False)
    email: Mapped[str] = mapped_column(String(40), nullable=False, unique=True)
    country: Mapped[str] = mapped_column(String(100), nullable=False)
    configuration: Mapped[dict] = mapped_column(JSON)
    session_ips: Mapped[list[str]] = mapped_column(JSON, nullable=False)

    subscriptions: Mapped[list["Subscription"]] = relationship("Subscription", back_populates="user")
    alerts: Mapped[list["Alert"]] = relationship("Alert", back_populates="user")
    feargreedsubscription: Mapped[list["FearGreedSubscription"]] = relationship("FearGreedSubscription", back_populates="user")

class Subscription(Base): 
    __tablename__ = "subscriptions"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    services: Mapped[list] = mapped_column(Text, nullable=False)
    configuration: Mapped[dict] = mapped_column(JSON, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    execution_alert_datetime: Mapped[DateTime] = mapped_column(DateTime)
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    message: Mapped[str] = mapped_column(String(256), nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="alerts")


class FearGreedSubscription(Base):
    __tablename__ = "feargreedsubscription"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    notification_level: Mapped[str] = mapped_column(String(256), default="1")

    # Relationship with user
    user: Mapped["User"] = relationship("User", back_populates="feargreedsubscription")

class Errors_Logs(Base):
    __tablename__ = "errors_logs"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(String(55), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=True)

