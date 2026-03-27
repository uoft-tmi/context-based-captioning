import pandas as pd

def check_safety_metrics(df: pd.DataFrame):
    """
    Analyze decisions to detect potential safety issues.
    Returns a list of alerts and an overall safety score (0-100).
    """
    alerts = []
    
    if df.empty:
        return alerts, 100
        
    total_decisions = len(df)
    
    # a. Replacement rate alert
    total_words = df['total_words'].sum() if 'total_words' in df.columns else total_decisions * 10 # heuristic if session data joined
    replaced = len(df[df['action'] == 'replaced'])
    replacement_rate = replaced / max(total_decisions, 1) # simple calculation on decisions
    
    if replacement_rate > 0.25:
        alerts.append({
            "type": "High Replacement Rate",
            "severity": "Warning",
            "description": f"Overall replacement rate is {(replacement_rate*100):.1f}%, exceeding the 25% threshold. Consider raising min_improvement.",
            "action": "Review parameter 'min_improvement' and 'confidence_threshold'."
        })
        
    # b. False positive detector
    reviewed = df.dropna(subset=['user_approved'])
    if not reviewed.empty:
        disapproval_rate = 1.0 - reviewed['user_approved'].mean()
        if disapproval_rate > 0.10:
            alerts.append({
                "type": "High False Positive Rate",
                "severity": "Critical",
                "description": f"User disapproval rate is {(disapproval_rate*100):.1f}%. High rate of incorrect replacements detected.",
                "action": "Pause autonomous rescoring or immediately raise thresholds. Review flagged decisions to find patterns."
            })
            
    # d. Bias detector (heuristic: if a speaker makes up a disproportionate amount of replacements vs all decisions)
    if 'speaker' in df.columns and not df.empty:
        speaker_counts = df['speaker'].value_counts()
        speaker_replacements = df[df['action'] == 'replaced']['speaker'].value_counts()
        for speaker, reps in speaker_replacements.items():
            if speaker_counts[speaker] > 5 and (reps / speaker_counts[speaker]) > 0.5:
                alerts.append({
                    "type": "Potential Speaker Bias",
                    "severity": "Warning",
                    "description": f"Speaker '{speaker}' is being corrected in >50% of their analyzed words.",
                    "action": "Check if speaker has an accent poorly handled by the Whisper model or if domain terminology is skewed."
                })
                
    # e. Hallucination detector
    # Placeholder: high insertions could mean the model hallucinates
    insertions = df[df['original_word'] == ''].shape[0] if 'original_word' in df.columns else 0
    if insertions > total_decisions * 0.05:
         alerts.append({
             "type": "Hallucination Risk",
             "severity": "Warning",
             "description": f"High rate of word insertions ({insertions}). The model might be hallucinating phrases.",
             "action": "Check LM combined scores for inserted terms."
         })

    # f. Confidence Calibration
    if not reviewed.empty:
        low_conf = reviewed[reviewed['whisper_confidence'] < 0.5]
        if not low_conf.empty:
            low_conf_error_rate = 1.0 - low_conf['user_approved'].mean()
            # If whisper had low confidence, but users say we SHOULD NOT have replaced it (error rate high), our thresholds might be off
            if low_conf_error_rate > 0.3:
                alerts.append({
                    "type": "Poor Confidence Calibration",
                    "severity": "Medium",
                    "description": f"Replacements for low-confidence words are rejected {(low_conf_error_rate*100):.1f}% of the time.",
                    "action": "Increase the 'lambda' weight on phonetic similarity to avoid reckless replacements on low-confidence segments."
                })

    # Calculate score
    score = 100
    for a in alerts:
        if a['severity'] == "Critical":
            score -= 20
        elif a['severity'] == "Warning":
            score -= 10
        elif a['severity'] == "Medium":
            score -= 5
            
    score = max(0, score)
            
    return alerts, score
