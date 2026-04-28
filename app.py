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

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_question}
            ]
        }
    )

    data = response.json()

    if "choices" not in data:
        return jsonify({"answer": f"Ошибка OpenAI: {data}"})

    answer = data["choices"][0]["message"]["content"]

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
