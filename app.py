from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

SYSTEM_PROMPT = """
Ты образовательный ассистент.
Отвечай понятно, структурировано и академически корректно.
"""

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    user_question = request.json.get("question")

    # Пока заглушка вместо модели
    response = f"Учебный ответ модели на вопрос: {user_question}"

    return jsonify({"answer": response})


if __name__ == "__main__":
    app.run(debug=True)
