# all functions intercting with db tables are defined here
# all db tables are represented as classes in db/models.py, so we will import those classes here and use them to interact with the db tables
from db.models import Conversation, Message, DB_FILE, ConversationSummary
#create function insert_message and list_message

from sqlalchemy import create_engine
engine = create_engine(DB_FILE)
from sqlalchemy.orm import sessionmaker
Session = sessionmaker(bind=engine)
session = Session()

def insert_message(conversation_id: int, role: str, content: str, tokens: int = 0):
    message = Message(conversation_id=conversation_id, role=role, content=content, tokens=tokens)
    session.add(message)
    session.commit()
    session.close()

def list_message(conversation_id: int):
    messages = session.query(Message).filter_by(conversation_id=conversation_id).order_by(Message.id).all()
    session.close()
    return messages

def list_messaages_after_summary(conversation_id: int, lastmessage_id: int):
    messages = session.query(Message).filter_by(conversation_id=conversation_id).filter(Message.id > lastmessage_id).order_by(Message.id).all()
    session.close()
    return messages

def create_conversation(title: str):
    conversation = Conversation(title=title)
    session.add(conversation)
    session.commit()
    session.refresh(conversation)  # reload id/created_at so they are readable after the session is closed
    session.close()
    return conversation

def update_conversation_tokens(conversation_id: str, tokens: int):
    conversation = session.query(Conversation).get(conversation_id)
    if conversation is None:
        raise ValueError(f"Conversation with id {conversation_id} not found")
    conversation.tokens = int((conversation.tokens or 0)) + tokens
    session.commit()
    session.refresh(conversation)

def insert_or_update_conversation_summary(conversation_id: int, summary: str, lastmessage_id: int):
    conversation_summary = session.query(ConversationSummary).filter_by(conversation_id=conversation_id).first()
    if conversation_summary:
        conversation_summary.summary = summary
        conversation_summary.lastmessage_id = lastmessage_id
    else:
        conversation_summary = ConversationSummary(conversation_id=conversation_id, summary=summary, lastmessage_id=lastmessage_id)
        session.add(conversation_summary)
    session.commit()
    session.refresh(conversation_summary)  # reload id/created_at so they are readable after the session is closed
    session.close()
    return conversation_summary

def get_conversation_summary(conversation_id: int):
    conversation_summary = session.query(ConversationSummary).filter_by(conversation_id=conversation_id).order_by(ConversationSummary.id.desc()).first()
    session.close()
    return conversation_summary
    
