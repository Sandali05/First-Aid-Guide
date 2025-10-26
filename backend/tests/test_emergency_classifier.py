from app.agents.emergency_classifier import classify


def test_classify_marks_cannot_breathe_as_high_severity():
    triage = classify("cannot breathe feel faint")

    assert triage["category"] == "fainting"
    assert triage["severity"] == "high"


def test_heavy_bleeding_escalates_to_high_severity():
    triage = classify("bleeding heavy from arm wound")

    assert triage["category"] == "bleeding"
    assert triage["severity"] == "high"
