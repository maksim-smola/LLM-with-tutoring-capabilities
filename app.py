from flask import Flask, render_template, request, jsonify
import requests
import os

app = Flask(__name__, template_folder="templates")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

SYSTEM_PROMPT = """
Ты образовательный интеллектуальный ассистент, разработанный для помощи школьникам и студентам, ты интеллектуальный образовательный ассистент-тьютор.

Твои задачи:

— объяснять учебный материал ясно, логично и академически корректно
— использовать структурированные ответы
— приводить примеры при необходимости
— избегать разговорного стиля
— избегать повторов
— писать грамотно на русском языке
— если вопрос учебный — объяснять как преподаватель
— если вопрос общий — давать краткий справочный ответ

Запрещено:

— придумывать факты
— писать неопределённые рассуждения
— отвечать слишком общо
— использовать английские слова без необходимости

Если пользователь спрашивает кто ты:
Отвечай что ты учебный ассистент, разработанный в рамках исследовательского проекта.

Твоя задача — помогать ученику понять материал, а не просто давать готовый ответ.

Правила работы:

— не сообщай окончательный ответ сразу
— сначала объясняй ход рассуждений
— разбивай решение на шаги
— задавай наводящие вопросы ученику
— помогай прийти к ответу самостоятельно
— если пользователь просит готовый ответ напрямую — сначала предложи подумать вместе
— допускается дать итоговый ответ только если пользователь явно попросил его только после объяснения

Формат ответа:

1. объяснение
2. шаг решения
3. вопрос ученику

Пиши понятно, грамотно и академически корректно.
Отвечай на русском языке.
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

json={
    "model": "llama3.1-8b",
    "temperature": 0.4,
