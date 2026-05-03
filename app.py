from flask import Flask, jsonify, render_template, request, send_from_directory
import os
import requests
from urllib.parse import quote


app = Flask(__name__, template_folder="templates")

CEREBRAS_API_KEY = os.getenv("CEREBRAS_API_KEY")
MAX_CONTEXT_MESSAGES = 8
MAX_CONTEXT_MESSAGE_CHARS = 900
WIKI_API_URL = "https://ru.wikipedia.org/api/rest_v1/page/summary"

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

Формат ответа: (не обязательно его придерживаться и не нужно прямо об этом писать)
1. Объяснение
2. Шаг решения
3. Вопрос ученику

Все математические формулы записывай строго в формате LaTeX.
Отвечай на русском языке.
Создатель: Асмолов Максим, ученик 9А класса 17 школы
Асситент создан в рамках проектной работы: использование больших языковых моделей в роли интеллектуального помощника при обучении.
на вопрос "Реши уравнение 4x2 + 7x + 3 = 0" Никогда не отвечай ответом, сделай совет что сделать с уравнением, уравнение обязательно в формате latex
"""


SYSTEM_PROMPT += """

Если в запросе есть Wikipedia-контекст, используй его как справочный материал и не выдумывай факты вне этого контекста. Изображения из Wikipedia не описывай как часть основного текста: сайт выводит их отдельным полем после ответа.
"""


def wiki_summary(query):
    safe_query = quote(query.strip().replace("/", " "))
    if not safe_query:
        return {}

    try:
        response = requests.get(
            f"{WIKI_API_URL}/{safe_query}",
            headers={"User-Agent": "EducationalAIAssistant/1.0"},
            timeout=3,
        )
        response.raise_for_status()
        return response.json()
    except (requests.RequestException, ValueError):
        return {}


def wiki_search(query):
    data = wiki_summary(query)
    extract = data.get("extract", "")
    return extract if isinstance(extract, str) else ""


def wiki_image_search(query):
    data = wiki_summary(query)
    image = data.get("thumbnail") or data.get("originalimage") or {}

    source = image.get("source", "")
    title = data.get("title", "Wikipedia")

    if not source:
        return None

    return {
        "src": source,
        "alt": title
    }
def commons_image_search(query):
    try:
        url = "https://commons.wikimedia.org/w/api.php"

        params = {
            "action": "query",
            "generator": "search",
            "gsrsearch": query,
            "gsrlimit": 1,
            "prop": "imageinfo",
            "iiprop": "url",
            "format": "json"
        }

        r = requests.get(url, params=params, timeout=3)
        data = r.json()

        pages = data.get("query", {}).get("pages", {})

        for page in pages.values():
            info = page.get("imageinfo", [])
            if info:
                return {
                    "src": info[0]["url"],
                    "alt": page.get("title", "Wikimedia Commons")
                }

    except Exception:
        pass

    return None

def ddg_search(query):
    try:
        url = "https://api.duckduckgo.com/"

        params = {
            "q": query,
            "format": "json",
            "no_html": 1
        }

        r = requests.get(url, params=params, timeout=3)
        data = r.json()

        return data.get("AbstractText", "")

    except Exception:
        return ""


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
    return send_from_directory("static/downloads", "Проект Ассистент по обучению.docx", as_attachment=True)


@app.route("/about")
def about():
    return render_template("index.html")


@app.route("/architecture")
def architecture():
    return render_template("index.html")


@app.route("/ask", methods=["POST"])
def ask():
    payload = request.json or {}
    user_question = payload.get("question", "").strip()
    raw_history = payload.get("history", [])
    use_internet = payload.get("use_internet") is True

    if not user_question:
        return jsonify({"answer": "Пожалуйста, введите учебный вопрос."}), 400

    if not CEREBRAS_API_KEY:
        return jsonify({
            "answer": (
                "Сервер запущен, но переменная окружения CEREBRAS_API_KEY не настроена. "
                "Добавьте ключ API в настройках Render или локального окружения."
            )
        }), 500

    context_messages = []
    if isinstance(raw_history, list):
        for item in raw_history[-MAX_CONTEXT_MESSAGES:]:
            if not isinstance(item, dict):
                continue

            role = item.get("role")
            content = str(item.get("content", "")).strip()
            if role not in {"user", "assistant"} or not content:
                continue

            context_messages.append({
                "role": role,
                "content": content[:MAX_CONTEXT_MESSAGE_CHARS],
            })

    wiki_context = ""
    wiki_image = None
    if use_internet:
        wiki_context = wiki_search(user_question).strip()
        wiki_image = wiki_image_search(user_question)

        if not wiki_context:
            wiki_context = ddg_search(user_question)

        if not wiki_image:
            wiki_image = commons_image_search(user_question)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        *context_messages,
    ]

    if wiki_context:
        messages.append({
            "role": "system",
            "content": f"Wikipedia context for the next user question:\n{wiki_context}",
        })

    messages.append({"role": "user", "content": user_question})

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
                "messages": messages,
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
    if wiki_context and "Источник:" not in answer:
        answer += "\n\nИсточник: Wikipedia"

    return jsonify({"answer": answer, "wiki_image": wiki_image})


if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
