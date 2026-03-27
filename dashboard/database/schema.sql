-- decisions table (as specified in user request)
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    session_id TEXT,
    audio_file TEXT,
    position INTEGER,
    original_word TEXT,
    whisper_confidence REAL,
    action TEXT,
    replacement_word TEXT,
    phonetic_similarity REAL,
    lm_score_original REAL,
    lm_score_replacement REAL,
    combined_score_original REAL,
    combined_score_replacement REAL,
    improvement REAL,
    context_before TEXT,
    context_after TEXT,
    domain TEXT,
    speaker TEXT,
    audio_quality TEXT,
    user_approved BOOLEAN,
    user_feedback TEXT,
    flagged BOOLEAN DEFAULT FALSE
);

CREATE TABLE parameters (
    session_id TEXT PRIMARY KEY,
    confidence_threshold REAL,
    phonetic_threshold REAL,
    lambda REAL,
    min_improvement REAL,
    hot_words TEXT,
    whisper_model TEXT,
    lm_model TEXT
);

CREATE TABLE sessions (
    session_id TEXT PRIMARY KEY,
    timestamp DATETIME,
    audio_file TEXT,
    total_words INTEGER,
    low_confidence_words INTEGER,
    words_rescored INTEGER,
    wer_before REAL,
    wer_after REAL,
    processing_time REAL
);

CREATE TABLE incidents (
    id INTEGER PRIMARY KEY,
    timestamp DATETIME,
    decision_id INTEGER,
    incident_type TEXT,
    severity TEXT,
    description TEXT,
    resolved BOOLEAN DEFAULT FALSE
);
