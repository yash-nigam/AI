# all functions intercting with db tables are defined here
# all db tables are represented as classes in db/models.py, so we will import those classes here and use them to interact with the db tables
from db.models import Conversation, Message, DB_FILE
#create function insert_message and list_message

from sqlalchemy import create_engine
engine = create_engine(DB_FILE)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

def insert_message(conversation_id: int, role: str, content: str):
    message = Message(conversation_id=conversation_id, role=role, content=content)
    session.add(message)
    session.commit()
    session.close()

def list_message(conversation_id: int):
    messages = session.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.id)
    session.close()
    return messages

def create_conversation(title: str):
    conversation = Conversation(title=title)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)  # reload id/created_at so they are readable after the session is closed
    session.close()
    return conversation