import pickle

# 1. Load the saved model and vectorizer
model = pickle.load(open('spam_model.pkl', 'rb'))
vectorizer = pickle.load(open('vectorizer.pkl', 'rb'))

# 2. Test messages
test_messages = [
    "Hey Yash, are we still studying for the exam tonight?",
    "URGENT! Your account has been compromised. Click here to reset your password: http://fake-bank-security.com"
]

# 3. Predict
for msg in test_messages:
    vec_text = vectorizer.transform([msg])
    prediction = model.predict(vec_text)[0]
    print(f"Message: '{msg}'")
    print(f"Result: ➔ **{prediction.upper()}**\n")
