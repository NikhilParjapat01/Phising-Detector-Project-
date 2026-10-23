import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

# 1. Create dataset directly in Python using double quotes for strings
data = {
    'label': ['ham', 'ham', 'ham', 'spam', 'spam', 'spam'],
    'message': [
        "Hey, are we still meeting for lunch today at 2 PM?",
        "Can you send me the notes from the computer science lecture?",
        "Don't forget to buy milk and eggs on your way home.",
        "URGENT! Your bank account has been locked. Click here immediately to verify: http://fake-bank-login.com",
        "Congratulations! You won a free iPhone. Claim your prize now by entering your details here: http://win-free-prize.xyz",
        "Your Netflix subscription has expired. Update your billing info instantly to avoid suspension: http://netflix-secure-update.tk"
    ]
}

df = pd.DataFrame(data)
print(f"Loaded {len(df)} messages for training.")

# 2. Split into inputs and labels
X = df['message']
y = df['label']

# 3. Convert text words into numerical math vectors
vectorizer = TfidfVectorizer(stop_words='english')
X_vectors = vectorizer.fit_transform(X)

# 4. Train the AI model
model = MultinomialNB()
model.fit(X_vectors, y)

# 5. Save the trained brain
with open('spam_model.pkl', 'wb') as f:
    pickle.dump(model, f)

with open('vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)

print('Success! Model trained with all messages and saved as spam_model.pkl')
