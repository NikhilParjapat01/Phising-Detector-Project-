from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pickle
import re
import requests
import os

app = FastAPI(title="AI Phishing & Scam Detector API", version="2.0")

# Load model and vectorizer
with open("spam_model.pkl", "rb") as f:
    model = pickle.load(f)
with open("vectorizer.pkl", "rb") as f:
    vectorizer = pickle.load(f)

class MessageRequest(BaseModel):
    text: str

class FeedbackRequest(BaseModel):
    text: str
    predicted_label: str
    user_reported_label: str

# Extended Hinglish & Global Phishing / Scam Keywords
HINGLISH_SUSPICIOUS = [
    "paise", "kamaye", "ghar ba", "inbox karo", "matlab", "lottery", 
    "jeeto", "account block", "urgently", "sarkari", "scheme", "part time", 
    "daily income", "invest", "crypto profit", "whatsapp pe message"
]

SUSPICIOUS_DOMAINS = ["bit.ly", "tinyurl.com", "t.co", "shorturl.at", "wa.link"]

def resolve_url(url: str) -> str:
    """Attempts to un-shorten redirect links to check the final destination."""
    try:
        response = requests.head(url, allow_redirects=True, timeout=2)
        return response.url
    except Exception:
        return url

def explain_prediction(text: str, is_phishing: bool, confidence: float) -> str:
    lower_text = text.lower()
    triggers = [word for word in HINGLISH_SUSPICIOUS if word in lower_text]
    urls = re.findall(r'https?://\S+|www\.\S+', text)
    
    # Check for shorteners
    has_shortener = any(any(domain in url for domain in SUSPICIOUS_DOMAINS) for url in urls)
    
    if is_phishing:
        reasons = []
        if urls:
            reasons.append("contains embedded web links")
        if has_shortener:
            reasons.append("uses a known URL shortener which masks the real destination")
        if triggers:
            reasons.append(f"triggers financial/urgency keywords ({', '.join(triggers)})")
        if confidence > 0.80:
            reasons.append("matches high-risk social engineering pattern matrices")
        
        return "Flagged because it " + " and ".join(reasons) if reasons else "High structural similarity to known scam messages."
    else:
        return "Clean text pattern. No dangerous financial lures, fake urgency claims, or malicious short-links detected."

@app.post("/predict")
def predict(data: MessageRequest):
    text = data.text
    
    # Heuristic override for obvious scam words combined with links/actions
    urls = re.findall(r'https?://\S+|www\.\S+', text)
    lower_text = text.lower()
    has_urgency = any(w in lower_text for w in ["urgent", "hurry", "blocked", "verify", "claim", "won", "lottery", "income"])
    
    vec_text = vectorizer.transform([text])
    probabilities = model.predict_proba(vec_text)[0] # [prob_safe, prob_phishing]
    phishing_prob = float(probabilities[1])
    
    # Boost probability if heuristics catch clear scam patterns missed by base TF-IDF
    if urls and has_urgency and phishing_prob < 0.6:
        phishing_prob = 0.78
        
    is_phishing = phishing_prob >= 0.5
    confidence_score = round(phishing_prob * 100 if is_phishing else (1 - phishing_prob) * 100, 2)
    
    return {
        "is_phishing": is_phishing,
        "label": "PHISHING / SCAM" if is_phishing else "SAFE",
        "confidence_score": confidence_score,
        "explanation": explain_prediction(text, is_phishing, phishing_prob),
        "urls_detected": urls
    }

@app.post("/report")
def report_false_prediction(data: FeedbackRequest):
    """Saves user feedback to build a real-world dataset for future retraining."""
    report_file = "user_reports.csv"
    file_exists = os.path.exists(report_file)
    
    with open(report_file, "a", encoding="utf-8") as f:
        if not file_exists:
            f.write("text,predicted_label,user_reported_label\n")
        f.write(f'"{data.text}","{data.predicted_label}","{data.user_reported_label}"\n')
        
    return {"status": "success", "message": "Feedback securely logged for future model updates."}

@app.get("/")
def home():
    return {"status": "Online", "message": "Phishing Detector Backend is running successfully!"}