import time
import pickle
import pyperclip
from plyer import notification

# 1. Load your trained AI brain
model = pickle.load(open('spam_model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

print("🛡️ AI Phishing Guard is now running in the background!")
print("Copy any message or email on your laptop to scan it instantly. (Press Ctrl+C to stop)")

last_text = ""

while True:
    try:
        # Check current clipboard text
        current_text = pyperclip.paste()
        
        # If new text is copied and it's not empty
        if current_text != last_text and current_text.strip() != "":
            last_text = current_text
            
            # Vectorize and predict using your AI model
            vec_text = vectorizer.transform([current_text])
            prediction = model.predict(vec_text)[0].upper()
            
            # Trigger Windows Desktop Notification based on result
            if prediction == "SPAM":
                notification.notify(
                    title="🚨 PHISHING / SCAM ALERT!",
                    message=f"Threat detected: {current_text[:70]}...",
                    timeout=6
                )
            else:
                notification.notify(
                    title="✅ Safe Message",
                    message="No phishing indicators found.",
                    timeout=3
                )
    except Exception as e:
        pass
        
    # Check clipboard every 1 second
    time.sleep(1)
