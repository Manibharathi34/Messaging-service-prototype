from sqlalchemy import Table, Column, String, Integer, Text, ForeignKey, DateTime, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import registry

mapper_registry = registry()
metadata = mapper_registry.metadata

users = Table(
    "users",
    metadata,
    Column("id", String, primary_key=True),  # UUID string
    Column("username", String(50), unique=True, nullable=False, index=True),
    Column("email", String(100), unique=True, nullable=False, index=True),
    Column("created_at", DateTime(timezone=True), server_default=func.now()),
)

chats = Table(
    "chats",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("sender", String, ForeignKey("users.id"), nullable=False, index=True),
    Column("receiver", String, ForeignKey("users.id"), nullable=False, index=True),
    Index("ix_chat_sender_receiver", "sender", "receiver", unique=True),
)

messages = Table(
    "messages",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("chat_id", Integer, ForeignKey("chats.id"), nullable=False, index=True),
    Column("text", Text, nullable=False),
    Column("time", DateTime(timezone=True), server_default=func.now(), index=True),
)
