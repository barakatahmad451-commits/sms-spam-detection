from __future__ import annotations

import pickle
import re
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

# Preserve the module environment expected by the serialized vectorizer.
if __name__ != "__main__":
    sys.modules["__main__"] = sys.modules[__name__]

app = Flask(__name__, static_folder="static", template_folder="templates")

def text_process(message: str) -> list[str]:
    """Tokenize SMS text in the same way the original training pipeline expected."""
    normalized = message.lower()
    normalized = re.sub(r"[^a-z0-9\s]", " ", normalized)
    tokens = [token for token in normalized.split() if token]
    return tokens

MODEL_PATH = Path(__file__).with_name("multinomial_naive_bayes_model.h5")
VECTORIZER_PATH = Path(__file__).with_name("tfidf_vectorizer.h5")


def load_object(path: Path):
    try:
        import joblib

        return joblib.load(path)
    except Exception:
        with open(path, "rb") as file:
            return pickle.load(file)


model = load_object(MODEL_PATH)
vectorizer = load_object(VECTORIZER_PATH)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    payload = request.get_json(force=True)
    message = payload.get("message", "").strip()

    if not message:
        return jsonify(error="Please enter the SMS message to classify."), 400

    vector = vectorizer.transform([message])
    probabilities = model.predict_proba(vector)[0]
    classes = list(model.classes_)

    if "spam" in classes:
        spam_index = classes.index("spam")
    else:
        spam_index = 1 if len(classes) > 1 else 0

    spam_prob = float(probabilities[spam_index])
    ham_prob = 1.0 - spam_prob
    prediction = "Spam" if spam_prob >= 0.5 else "Ham"

    tokens = [token for token in message.lower().split() if token in getattr(vectorizer, "vocabulary_", {})]
    token_snippet = tokens[:8] if tokens else ["no exact tokens matched"]

    explanation = (
        "This message is flagged as spam because the model detected phishing and unsolicited messaging patterns. "
        if prediction == "Spam"
        else "This message looks legitimate. The model found a low risk of spam based on its learned vocabulary patterns."
    )

    return jsonify(
        prediction=prediction,
        spamProbability=round(spam_prob * 100, 2),
        hamProbability=round(ham_prob * 100, 2),
        explanation=explanation,
        matchedTokens=token_snippet,
        vocabularySize=len(getattr(vectorizer, "vocabulary_", {})),
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
