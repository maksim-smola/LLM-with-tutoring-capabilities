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

    CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

    response = requests.post(
        "https://api.cerebras.ai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {CEREBRAS_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "model": "llama3.1-8b",
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_question}
            ]
        }
    )

    data = response.json()

    if "choices" not in data:
        return jsonify({"answer": f"Ошибка Cerebras API: {data}"})

    answer = data["choices"][0]["message"]["content"]

    return jsonify({"answer": answer})

    answer = data["choices"][0]["message"]["content"]

    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True)
