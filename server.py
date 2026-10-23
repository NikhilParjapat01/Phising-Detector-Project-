import pickle
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI()

# Load trained AI brain
model = pickle.load(open('spam_model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Phishing & Scam Detector</title>
    <style>
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
        body { background: #0f172a; color: #f8fafc; display: flex; justify-content: center; align-items: center; min-height: 100vh; padding: 20px; }
        .card { background: #1e293b; padding: 30px; border-radius: 16px; width: 100%; max-width: 600px; box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5); border: 1px solid #334155; }
        h1 { font-size: 1.8rem; margin-bottom: 8px; color: #38bdf8; text-align: center; }
        p.subtitle { font-size: 0.95rem; color: #94a3b8; text-align: center; margin-bottom: 24px; }
        textarea { width: 100%; height: 120px; padding: 14px; border-radius: 10px; border: 1px solid #475569; background: #0f172a; color: #fff; font-size: 1rem; resize: none; outline: none; margin-bottom: 16px; }
        textarea:focus { border-color: #38bdf8; }
        button { width: 100%; padding: 14px; background: #2563eb; color: #fff; font-weight: 600; font-size: 1rem; border: none; border-radius: 10px; cursor: pointer; transition: background 0.2s; }
        button:hover { background: #1d4ed8; }
        .result-box { margin-top: 20px; padding: 16px; border-radius: 10px; text-align: center; font-weight: bold; font-size: 1.2rem; display: none; }
        .spam { background: #7f1d1d; color: #fca5a5; border: 1px solid #ef4444; display: block; }
        .ham { background: #14532d; color: #86efac; border: 1px solid #22c55e; display: block; }
    </style>
</head>
<body>
    <div class="card">
        <h1>🛡️ AI Phishing & Scam Detector</h1>
        <p class="subtitle">Paste any SMS, Gmail, or message link below to scan it instantly</p>
        <textarea id="messageInput" placeholder="Paste suspicious message here..."></textarea>
        <button onclick="analyzeMessage()">Analyze Message</button>
        <div id="result" class="result-box"></div>
    </div>

    <script>
        async function analyzeMessage() {
            const text = document.getElementById('messageInput').value.trim();
            const resultDiv = document.getElementById('result');
            if (!text) return;

            resultDiv.className = 'result-box';
            resultDiv.style.display = 'block';
            resultDiv.innerText = 'Scanning...';

            const formData = new FormData();
            formData.append('text', text);

            const response = await fetch('/predict', { method: 'POST', body: formData });
            const data = await response.json();

            if (data.prediction === 'SPAM') {
                resultDiv.className = 'result-box spam';
                resultDiv.innerHTML = '🚨 PHISHING / SCAM DETECTED!';
            } else {
                resultDiv.className = 'result-box ham';
                resultDiv.innerHTML = '✅ SAFE MESSAGE (No Phishing Detected)';
            }
        }
    </script>
</body>
</html>
"""

@app.get("/", response_class=HTMLResponse)
def home():
    return HTML_TEMPLATE

@app.post("/predict")
def predict(text: str = Form(...)):
    vec_text = vectorizer.transform([text])
    prediction = model.predict(vec_text)[0].upper()
    return {"prediction": prediction}
