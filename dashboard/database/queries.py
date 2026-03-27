from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd
from .models import Decision, Base

# Initialize engine (SQLite for local dev)
engine = create_engine('sqlite:///decisions.db', echo=False)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)

def get_decisions(start_date=None, end_date=None, audio_file=None, action=None,
                  domain=None, flagged=None, search=None, sort_by='timestamp'):
    """Fetch decisions applying optional filters and sorting.
    Returns a pandas DataFrame for easy consumption by Streamlit.
    """
    session = Session()
    query = session.query(Decision)
    if start_date:
        query = query.filter(Decision.timestamp >= start_date)
    if end_date:
        query = query.filter(Decision.timestamp <= end_date)
    if audio_file:
        query = query.filter(Decision.audio_file.contains(audio_file))
    if action:
        query = query.filter(Decision.action == action)
    if domain:
        query = query.filter(Decision.domain.contains(domain))
    if flagged is not None:
        query = query.filter(Decision.flagged == flagged)
    if search:
        # simple search in original_word, replacement_word, context fields
        pattern = f"%{search}%"
        query = query.filter(
            (Decision.original_word.like(pattern)) |
            (Decision.replacement_word.like(pattern)) |
            (Decision.context_before.like(pattern)) |
            (Decision.context_after.like(pattern))
        )
    # Sorting
    if hasattr(Decision, sort_by):
        query = query.order_by(getattr(Decision, sort_by))
    else:
        query = query.order_by(Decision.timestamp)
    df = pd.read_sql(query.statement, engine)
    session.close()
    return df

def get_pending_decisions(limit=100):
    """Fetch decisions that have not been reviewed yet."""
    session = Session()
    query = session.query(Decision).filter(
        Decision.user_approved.is_(None),
        Decision.flagged == False
    ).order_by(Decision.timestamp).limit(limit)
    df = pd.read_sql(query.statement, engine)
    session.close()
    return df

def update_decision_feedback(decision_id, user_approved, flagged, feedback_text=None):
    """Update a decision with user feedback."""
    session = Session()
    decision = session.query(Decision).filter(Decision.id == decision_id).first()
    if decision:
        if user_approved is not None:
            decision.user_approved = user_approved
        if flagged is not None:
            decision.flagged = flagged
        if feedback_text is not None:
            decision.user_feedback = feedback_text
        session.commit()
    session.close()
