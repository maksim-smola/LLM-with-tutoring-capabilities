from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__, template_folder="templates")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
Ты образовательный ассистент.
Объясняй понятным академическим языком.
Приводи примеры.
Отвечай структурировано.
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():

    import os
    import requests

    user_question = request.json.get("question")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

    response = requests.post(
        f"{url}?key={GOOGLE_API_KEY}",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "contents": [
                {
                    "parts": [
                        {"text": SYSTEM_PROMPT + "\n\nВопрос пользователя:\n" + user_question}
                    ]
                }
            ]
        }
    )

    data = response.json()

    if "candidates" not in data:
        return jsonify({"answer": f"Ошибка Google API: {data}"})

    answer = data["candidates"][0]["content"]["parts"][0]["text"]

    return jsonify({"answer": answer})

    answer = data["choices"][0]["message"]["content"]

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
