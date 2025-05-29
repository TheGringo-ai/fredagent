# File: web/models.py
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    prompts = relationship("PromptLog", back_populates="user", cascade="all, delete-orphan")
    memory_events = relationship("MemoryEvent", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, name={self.name})>"

class PromptLog(Base):
    __tablename__ = "prompt_logs"
    id = Column(Integer, primary_key=True, index=True)
    prompt = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="prompts")

    def __repr__(self):
        return f"<PromptLog(id={self.id}, user_id={self.user_id}, timestamp={self.timestamp})>"

class MemoryEvent(Base):
    __tablename__ = "memory_events"
    id = Column(Integer, primary_key=True, index=True)
    event = Column(Text, nullable=False)
    timestamp = Column(DateTime, server_default=func.now())
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="memory_events")

    def __repr__(self):
        return f"<MemoryEvent(id={self.id}, user_id={self.user_id}, timestamp={self.timestamp})>"
