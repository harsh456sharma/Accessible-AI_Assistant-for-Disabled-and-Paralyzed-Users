from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__)

# 🔑 Set your Gemini API key here (replace this with your actual Gemini API key)
GEMINI_API_KEY = "AIzaSyATH3TaEZO1FjG4ihofdJ4MzU2pm3AUZzI"  # Replace with your key

# Corrected Gemini API URL (without the key in the URL)
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=${GEMINI_API_KEY}',

# 🏠 Home Page
@app.route('/')
def home():
    return render_template('index.html')

# 🎤 Voice Typing Page
@app.route('/voice')
def voice_typing():
    return render_template('voice.html')

# 🤖 AI Assistant Page
@app.route('/assistant')
def ai_assistant():
    return render_template('assistant.html')

# 🔁 API Endpoint for Gemini Response
@app.route('/get-response', methods=['POST'])
def get_response():
    data = request.get_json()

    # 🛡️ Validate incoming message
    user_message = data.get("message", "").strip()
    if not user_message:
        return jsonify({"reply": "❗ Please say something to begin."}), 400

    try:
        # 🧠 Gemini API call (Adjust based on Gemini's API structure)
        headers = {
            'Content-Type': 'application/json',
            'x-goog-api-key': GEMINI_API_KEY  # Use the correct header for API key
        }

        payload = {
            'contents': [
                {
                    'parts': [
                        {"text": user_message}
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 300
            }
        }

        response = requests.post(GEMINI_API_URL, json=payload, headers=headers)

        # 📝 Extract response from Gemini API
        if response.status_code == 200:
            try:
                reply = response.json()['candidates'][0]['content']['parts'][0]['text'].strip()
                return jsonify({"reply": reply})
            except (KeyError, IndexError):
                print(f"⚠️ Unexpected response structure from Gemini: {response.json()}")
                return jsonify({"reply": "⚠️ Error processing Gemini response."}), 500
        else:
            print(f"⚠️ Error from Gemini API: {response.status_code} - {response.text}")
            return jsonify({"reply": f"⚠️ Error from Gemini API: {response.text}"}), 500

    except requests.exceptions.RequestException as e:
        print(f"❌ Network error calling Gemini API: {e}")
        return jsonify({"reply": f"⚠️ Network error: {str(e)}"}), 500
    except Exception as e:
        print("❌ General error calling Gemini API:", e)
        return jsonify({"reply": f"⚠️ API error: {str(e)}"}), 500

# 🚀 Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)