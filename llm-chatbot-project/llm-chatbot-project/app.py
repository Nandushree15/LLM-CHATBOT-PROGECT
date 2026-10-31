
import os
import time
import uuid
from threading import Lock

from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from google import genai
from google.genai import types
from google.genai.errors import ClientError, ServerError

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add your API key to the .env file."
    )

client = genai.Client(api_key=API_KEY)

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3-flash-preview")
MODEL_FALLBACKS = (
    "gemini-3.5-flash",
    "gemini-3.6-flash",
)

SYSTEM_PROMPT = """
You are StudyBot, a friendly learning assistant.
Explain technical topics in simple, clear language.
Be accurate and helpful.
If you are unsure, say so instead of inventing facts.
Keep answers organized and appropriate for a student.
"""

# Demo-only conversation memory.
# Conversation history is cleared when the server restarts.
conversations = {}
history_lock = Lock()

MAX_HISTORY_MESSAGES = 10
MAX_RETRIES = 3


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/chat")
def chat():
    data = request.get_json(silent=True) or {}

    message = data.get("message", "")
    conversation_id = data.get("conversation_id", "")

    if not isinstance(message, str):
        return jsonify({"error": "Message must be text."}), 400

    message = message.strip()

    if not message:
        return jsonify({"error": "Please enter a message."}), 400

    if len(message) > 4000:
        return jsonify({
            "error": "Please enter 4,000 characters or fewer."
        }), 400

    if (
        not isinstance(conversation_id, str)
        or not conversation_id
        or len(conversation_id) > 100
    ):
        conversation_id = str(uuid.uuid4())

    with history_lock:
        previous_history = list(
            conversations.get(conversation_id, [])
        )

    request_history = previous_history + [
        {
            "role": "user",
            "parts": [{"text": message}]
        }
    ]

    try:
        response = None
        candidate_models = tuple(dict.fromkeys((MODEL_NAME,) + MODEL_FALLBACKS))

        # Try the configured model, then known working fallbacks when Gemini
        # is temporarily overloaded or a configured model is unavailable.
        for model_name in candidate_models:
            for attempt in range(MAX_RETRIES):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=request_history,
                        config=types.GenerateContentConfig(
                            system_instruction=SYSTEM_PROMPT,
                            temperature=0.7,
                        ),
                    )
                    break

                except (ClientError, ServerError) as exc:
                    status_code = getattr(exc, "status_code", None)
                    error_text = str(exc).lower()
                    temporary = status_code in (429, 500, 502, 503, 504) or any(
                        marker in error_text
                        for marker in ("429", "resource exhausted", "503 unavailable", "high demand", "overloaded")
                    )

                    if not temporary:
                        raise

                    if attempt == MAX_RETRIES - 1:
                        break

                    wait_seconds = 2 ** (attempt + 1)
                    app.logger.warning(
                        "Gemini model %s is temporarily unavailable (status %s). Retrying in %s seconds.",
                        model_name,
                        status_code,
                        wait_seconds,
                    )
                    time.sleep(wait_seconds)

            if response is not None:
                break

        answer = response.text if response else None

        if not answer or not answer.strip():
            return jsonify({
                "error": (
                    "The AI returned an empty response. "
                    "Please try again."
                )
            }), 502

        answer = answer.strip()

        updated_history = request_history + [
            {
                "role": "model",
                "parts": [{"text": answer}]
            }
        ]

        updated_history = updated_history[-MAX_HISTORY_MESSAGES:]

        with history_lock:
            conversations[conversation_id] = updated_history

        return jsonify({
            "reply": answer,
            "conversation_id": conversation_id,
        })

    except ServerError as exc:
        app.logger.exception("Gemini server error")

        if getattr(exc, "status_code", None) in (500, 502, 503, 504):
            error_message = (
                "Gemini is experiencing high demand. "
                "Please wait a little and try again."
            )
        else:
            error_message = (
                "The AI request failed. Check your model settings "
                "and API access."
            )

        return jsonify({"error": error_message}), 502

    except Exception as exc:
        app.logger.exception("LLM API request failed")

        status_code = getattr(exc, "status_code", None)
        message = str(exc).lower()

        if status_code == 401 or status_code == 403 or "api key" in message or "permission" in message:
            error_message = "Gemini rejected the API key or API access. Check your API settings."
            response_status = 502
        elif status_code == 429 or "rate" in message or "resource exhausted" in message:
            error_message = "The Gemini API rate limit was reached. Please wait and try again."
            response_status = 429
        else:
            error_message = (
                "StudyBot could not get a response. "
                "Check your internet connection and API settings."
            )
            response_status = 502

        return jsonify({"error": error_message}), response_status


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=int(os.getenv("PORT", "5000")),
        debug=False,
    )
