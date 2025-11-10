def combine_scores(a_label, a_conf, b_score, c_score):
    weights = {"a": 0.5, "b": 0.3, "c": 0.2}
    label_to_base = {"weak": 80, "medium": 50, "strong": 20}

    base = label_to_base[a_label]
    risk = base * weights["a"] + b_score * weights["b"] + c_score * weights["c"]

    if risk > 70:
        final_label = "weak"
    elif risk > 40:
        final_label = "medium"
    else:
        final_label = "strong"

    return {"final_label": final_label, "risk_score": round(risk, 2)}
