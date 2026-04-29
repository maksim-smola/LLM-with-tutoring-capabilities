from flask import Flask, jsonify, render_template, request, send_from_directory
import os
import requests


app = Flask(__name__, template_folder="templates")

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")

SYSTEM_PROMPT = """
Ты образовательный интеллектуальный ассистент-тьютор, разработанный для помощи школьникам и студентам.

Твои задачи:
- объяснять учебный материал ясно, логично и академически корректно;
- использовать структурированные ответы;
- приводить примеры при необходимости;
- избегать повторов;
- писать грамотно на русском языке;
- если вопрос учебный, объяснять как преподаватель;
- если вопрос общий, давать краткий справочный ответ.

Запрещено:
- придумывать факты;
- отвечать слишком общо;
- использовать английские слова без необходимости.

Твоя задача - помогать ученику понять материал, а не просто давать готовый ответ.

Правила работы:
- не сообщай окончательный ответ сразу;
- сначала объясняй ход рассуждений;
- разбивай решение на шаги;
- задавай наводящие вопросы ученику;
- помогай прийти к ответу самостоятельно;
- если пользователь просит готовый ответ напрямую, сначала предложи подумать вместе;
- итоговый ответ допустим только после объяснения.

Формат ответа:
1. Объяснение
2. Шаг решения
3. Вопрос ученику

Все математические формулы записывай строго в формате LaTeX.
Отвечай на русском языке.
"""


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/assistant")
def assistant():
    return render_template("assistant.html")


@app.route("/project")
def project():
    return render_template("project.html")


@app.route("/download/project")
def download_project():
    return send_from_directory("static/downloads", "Приказ №27С.docx", as_attachment=True)


@app.route("/about")
def about():
    return render_template("index.html")


@app.route("/architecture")
def architecture():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    user_question = (request.json or {}).get("question", "").strip()

    if not user_question:
        return jsonify({"answer": "Пожалуйста, введите учебный вопрос."}), 400

    if not CEREBRAS_API_KEY:
        return jsonify({
            "answer": (
                "Сервер запущен, но переменная окружения CEREBRAS_API_KEY не настроена. "
                "Добавьте ключ API в настройках Render или локального окружения."
            )
        }), 500

    try:
        response = requests.post(
            "https://api.cerebras.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {CEREBRAS_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "llama3.1-8b",
                "temperature": 0.4,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_question},
                ],
            },
            timeout=45,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        return jsonify({"answer": f"Не удалось получить ответ от API: {exc}"}), 502

    data = response.json()

    if "choices" not in data:
        return jsonify({"answer": f"Ошибка Cerebras API: {data}"}), 502

    answer = data["choices"][0]["message"]["content"]
    return jsonify({"answer": answer})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
