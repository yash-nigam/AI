# tables messages and conversations which represent the conversation between user and assistant
# one conversation can have multiple messages, so we need to have a foreign key relationship between messages and conversations
# messages - fields(id, conversation_id, role, content, created_at)
# conversations - fields(id, title, created_at)
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, create_engine
from dotenv import load_dotenv
import os
from datetime import datetime, timezone
# Declarative base means every class that inherits from it will be a table in the database
from sqlalchemy.orm import declarative_base, relationship

load_dotenv()  # reads .env into environment variables
DB_FILE = os.environ["DB_FILE_PATH"]
Base = declarative_base()

def _now():
    return datetime.now(timezone.utc)

class Conversation(Base):
    __tablename__ = "conversations"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True)
    created_at = Column(DateTime, default=_now)
    tokens = Column(String, index=True)
    messages = relationship("Message", back_populates="conversation")
    summaries = relationship("ConversationSummary", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    role = Column(String, index=True)
    content = Column(String, index=True)
    tokens = Column(String, index=True)
    created_at = Column(DateTime, default=_now)
    conversation = relationship("Conversation", back_populates="messages")

class ConversationSummary(Base):
    __tablename__ = "conversation_summaries"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"))
    summary = Column(String, index=True)
    created_at = Column(DateTime, default=_now)
    lastmessage_id = Column(Integer, ForeignKey("messages.id"))
    conversation = relationship("Conversation", back_populates="summaries")

def autocreate_tables():
    engine = create_engine(DB_FILE, echo=True)
    Base.metadata.create_all(bind=engine)   

