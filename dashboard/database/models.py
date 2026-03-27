from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Decision(Base):
    __tablename__ = "decisions"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    session_id = Column(String)
    audio_file = Column(String)
    position = Column(Integer)
    original_word = Column(String)
    whisper_confidence = Column(Float)
    action = Column(String)
    replacement_word = Column(String, nullable=True)
    phonetic_similarity = Column(Float)
    lm_score_original = Column(Float)
    lm_score_replacement = Column(Float)
    combined_score_original = Column(Float)
    combined_score_replacement = Column(Float)
    improvement = Column(Float)
    context_before = Column(Text)
    context_after = Column(Text)
    domain = Column(String)
    speaker = Column(String)
    audio_quality = Column(String)
    user_approved = Column(Boolean, nullable=True)
    user_feedback = Column(Text, nullable=True)
    flagged = Column(Boolean, default=False)

class Parameter(Base):
    __tablename__ = "parameters"
    session_id = Column(String, primary_key=True)
    confidence_threshold = Column(Float)
    phonetic_threshold = Column(Float)
    lambda_ = Column(Float)  # 'lambda' is a reserved keyword
    min_improvement = Column(Float)
    hot_words = Column(Text)  # JSON array stored as text
    whisper_model = Column(String)
    lm_model = Column(String)

class Session(Base):
    __tablename__ = "sessions"
    session_id = Column(String, primary_key=True)
    timestamp = Column(DateTime)
    audio_file = Column(String)
    total_words = Column(Integer)
    low_confidence_words = Column(Integer)
    words_rescored = Column(Integer)
    wer_before = Column(Float)
    wer_after = Column(Float)
    processing_time = Column(Float)

class Incident(Base):
    __tablename__ = "incidents"
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime)
    decision_id = Column(Integer)
    incident_type = Column(String)
    severity = Column(String)
    description = Column(Text)
    resolved = Column(Boolean, default=False)
