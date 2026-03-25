def calculate_stage_score(word_diff, char_diff):
    average_diff = (word_diff + char_diff) / 2
    score = max(0, 100 - average_diff)

    return round(score, 2)


def calculate_final_score(stage_scores):
    if not stage_scores:
        return 0.0

    total = sum(stage_scores.values())
    count = len(stage_scores)

    return round(total / count, 2)


def classify_risk(final_score):
    if final_score == 100:
        return "No Dyslexia Detected"
    elif final_score >= 85:
        return "Low Risk - Reading Skills Appear Typical"

    elif 70 <= final_score < 85:
        return "Moderate Risk - Some Reading Difficulties Detected"
    else:
        return "High Risk - Likely Dyslexia, Consult a Specialist"


def generate_interpretation(final_score):
    if final_score >= 85:
        return "Performance indicates appropriate reading ability."
    elif final_score >= 85:
        return "Performance indicates emerging reading ability."

    elif 70 <= final_score < 85:
        return "Mild reading inconsistencies observed. Monitoring recommended."

    else:
        return "Significant reading difficulty indicators detected. Professional evaluation advised."