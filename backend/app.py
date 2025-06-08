from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# Environment Variables
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
host = os.getenv("HOST", "127.0.0.1")
port = int(os.getenv("PORT", 5000))


@app.route("/", methods=["GET"])
def index():
    return jsonify({"message": "Welcome to Nuvora AI Backend!"})


@app.route("/summarize", methods=["POST"])
def summarize_text():
    try:
        data = request.get_json()
        text = data.get("text", "").strip()

        if not text:
            return jsonify({"error": "No text provided"}), 400

        prompt = f"Summarize the following passage in a few sentences:\n\n{text}"

        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {GROQ_API_KEY}"
            },
            json={
                "model": "llama3-8b-8192",
                "messages": [{"role": "user", "content": prompt}]
            }
        )

        if response.status_code != 200:
            return jsonify({"error": "Groq API failed", "details": response.text}), 500

        result = response.json()
        summary = result["choices"][0]["message"]["content"]
        return jsonify({"summary": summary})

    except Exception as e:
        return jsonify({"error": "Server error", "message": str(e)}), 500


@app.route("/language-correct", methods=["POST"])
def language_correct():
    data = request.get_json()
    sentence = data.get("text", "").strip()

    if not sentence:
        return jsonify({"error": "No sentence provided"}), 400

    prompt = f"Correct the grammar and suggest improvements for this sentence: '{sentence}'"

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )

    if response.status_code != 200:
        return jsonify({"error": "Gemini API failed", "details": response.text}), 500

    result = response.json()
    reply = result["candidates"][0]["content"]["parts"][0]["text"]
    return jsonify({"correction": reply})


@app.route("/quiz", methods=["POST"])
def generate_quiz():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "No input text provided"}), 400

    prompt = f"Generate 3 multiple-choice quiz questions (with 4 options each) and their correct answers based on the following text:\n\n{text}"

    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GROQ_API_KEY}"
        },
        json={
            "model": "llama3-8b-8192",
            "messages": [{"role": "user", "content": prompt}]
        }
    )

    if response.status_code != 200:
        return jsonify({"error": "Groq API failed", "details": response.text}), 500

    result = response.json()
    quiz = result["choices"][0]["message"]["content"]
    return jsonify({"quiz": quiz})


@app.route("/daily-inspiration", methods=["GET"])
def daily_inspiration():
    prompt = (
        "Generate daily inspiration with the following:\n"
        "1. A motivational quote.\n"
        "2. A short productivity tip.\n"
        "3. A reflective journaling prompt.\n"
        "Respond in this format:\n"
        "- Quote: <quote>\n"
        "- Tip: <tip>\n"
        "- Prompt: <journaling prompt>"
    )

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )

    if response.status_code != 200:
        return jsonify({"error": "Gemini API failed", "details": response.text}), 500

    result = response.json()
    reply = result["candidates"][0]["content"]["parts"][0]["text"]
    return jsonify({"inspiration": reply})


@app.route("/reminder", methods=["POST"])
def daily_reminder():
    try:
        data = request.get_json()
        goal = data.get("goal", "").strip()
        time = data.get("time", "").strip()

        if not goal or not time:
            return jsonify({"error": "Missing goal or time"}), 400

        prompt = (
            f"You are a friendly AI assistant helping someone stay on track with personal growth.\n"
            f"User's Goal: {goal}\n"
            f"Target Time: {time}\n\n"
            "Generate:\n"
            "1. A motivational nudge.\n"
            "2. A gentle reminder to do one small task that moves them closer to their goal.\n"
            "Format:\n"
            "- Reminder: <message>\n"
            "- Goal Tip: <suggestion>\n"
            "Tone: friendly, warm, casual."
        )

        response = requests.post(
            f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": prompt}]}]}
        )

        if response.status_code != 200:
            return jsonify({"error": "Gemini API failed", "details": response.text}), 500

        result = response.json()
        reply = result["candidates"][0]["content"]["parts"][0]["text"]

        reminder_message = ""
        goal_tip = ""

        if "-Reminder:" in reply:
            reminder_message = reply.split("-Reminder:")[1].split("-Goal Tip:")[0].strip()

        if "-Goal Tip:" in reply:
            goal_tip = reply.split("-Goal Tip:")[1].strip()

        return jsonify({
            "reminder_message": reminder_message,
            "goal_tip": goal_tip
        })

    except Exception as e:
        return jsonify({"error": "Server error", "message": str(e)}), 500


@app.route("/conversation-prompt", methods=["POST"])
def conversation_prompt():
    data = request.get_json()
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"error": "No message provided"}), 400

    prompt = (
        f"You are a friendly and thoughtful AI assistant for personal growth and well-being.\n"
        f"Given this user message, respond supportively:\n"
        f"User: '{message}'\n\nAI:"
    )

    response = requests.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}",
        headers={"Content-Type": "application/json"},
        json={"contents": [{"parts": [{"text": prompt}]}]}
    )

    if response.status_code != 200:
        return jsonify({"error": "Gemini API failed", "details": response.text}), 500

    result = response.json()
    reply = result["candidates"][0]["content"]["parts"][0]["text"]
    return jsonify({"response": reply})


if __name__ == "__main__":
    app.run(host=host, port=port, debug=True)
