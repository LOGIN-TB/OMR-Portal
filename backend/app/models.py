from datetime import datetime
from uuid import uuid4

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class PortalUser(Base):
    __tablename__ = "portal_users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    language = Column(String(2), default="de")
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)

    accounts = relationship("ServerAccount", back_populates="portal_user")
    preferences = relationship("NotificationPreference", back_populates="portal_user")


class ServerAccount(Base):
    __tablename__ = "server_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portal_user_id = Column(String(36), ForeignKey("portal_users.id"), nullable=False)
    server_id = Column(String(50), nullable=False)
    server_name = Column(String(100), nullable=False)
    smtp_user_id = Column(Integer, nullable=False)
    username = Column(String(100), nullable=False)
    company = Column(String(200), nullable=True)
    mail_domain = Column(String(200), nullable=True)
    is_active = Column(Boolean, default=True)
    last_synced = Column(DateTime, default=datetime.utcnow)

    portal_user = relationship("PortalUser", back_populates="accounts")

    __table_args__ = (
        UniqueConstraint("server_id", "smtp_user_id", name="uq_server_smtp_user"),
    )


class MagicToken(Base):
    __tablename__ = "magic_tokens"

    token = Column(String(36), primary_key=True, default=lambda: str(uuid4()))
    email = Column(String, nullable=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    used = Column(Boolean, default=False)


class WarningLog(Base):
    __tablename__ = "warning_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portal_user_id = Column(String(36), ForeignKey("portal_users.id"), nullable=False)
    warning_type = Column(String(50), nullable=False)
    sent_at = Column(DateTime, default=datetime.utcnow)
    details = Column(Text, nullable=True)


class NotificationPreference(Base):
    __tablename__ = "notification_preferences"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portal_user_id = Column(String(36), ForeignKey("portal_users.id"), nullable=False)
    warning_type = Column(String(50), nullable=False)
    enabled = Column(Boolean, default=True)

    portal_user = relationship("PortalUser", back_populates="preferences")

    __table_args__ = (
        UniqueConstraint("portal_user_id", "warning_type", name="uq_user_warning"),
    )


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)


class RelayServer(Base):
    __tablename__ = "relay_servers"

    id = Column(String(50), primary_key=True)
    name = Column(String(200), nullable=False)
    admin_url = Column(String(500), nullable=False)
    api_key = Column(String(500), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class PortalSetting(Base):
    __tablename__ = "portal_settings"

    key = Column(String(100), primary_key=True)
    value = Column(Text, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
