from sqlalchemy import String, UUID, Float, DateTime, Text, ForeignKey, JSON, INT
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
    user_configuration: Mapped["UserConfiguration"] = relationship("UserConfiguration", back_populates="user", uselist=False)
    fear_greed_bot: Mapped["Fear_greed_bot"] = relationship("Fear_greed_bot", back_populates="user")

class Subscription(Base): 
    __tablename__ = "subscriptions"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    services: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    configuration: Mapped[dict] = mapped_column(JSON, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="subscriptions")

class Alert(Base):
    __tablename__ = "alerts"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    execution_alert_datetime: Mapped[DateTime] = mapped_column(DateTime)
    type: Mapped[str] = mapped_column(String(40), nullable=False)
    headline: Mapped[str] = mapped_column(Text, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="alerts")

class FearGreedSubscription(Base):
    __tablename__ = "feargreedsubscription"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('user.id'), nullable=False)
    notification_level: Mapped[str] = mapped_column(String(256), default="1")

    user: Mapped["User"] = relationship("User", back_populates="feargreedsubscription")

class ErrorsLogs(Base):
    __tablename__ = "errors_logs"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subject: Mapped[str] = mapped_column(String(55), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=True)

class UserConfiguration(Base):
    __tablename__ = "user_configuration"

    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('user.id'), primary_key=True, default=uuid.uuid4)
    cvi: Mapped[dict] = mapped_column(JSON)

    user: Mapped["User"] = relationship("User", back_populates="user_configuration", uselist=False)

class Fear_greed_bot(Base):
    __tablename__ = "fear_greed_bot"

    id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[UUID] = mapped_column(pgUUID(as_uuid=True), ForeignKey('user.id'), nullable=False, unique=True)
    level: Mapped[int] = mapped_column(INT, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="fear_greed_bot", uselist=False)



