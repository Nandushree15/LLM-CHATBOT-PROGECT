# StudyBot — LLM API Integration

A beginner-friendly chatbot built with Python, Flask, Google Gemini, HTML, CSS, and JavaScript.

## Features

- Calls a real Gemini LLM API through a Python backend.
- Keeps separate message histories using conversation IDs.
- Includes a system prompt defining the bot as a friendly learning assistant.
- Limits retained history to the latest 10 messages.
- Handles empty and overly long messages, API failures, and empty responses.
- Keeps the API key in an environment file instead of source code.
- Includes a simple responsive web interface and a New conversation button.

## Requirements

- Python 3.10 or newer (use a currently supported Python version).
- A Google AI Studio API key with access to the selected Gemini model.
- Internet access.

## Setup on Windows (VS Code)

1. Download and extract this repository/project.
2. Open the `llm-chatbot-project` folder in VS Code.
3. Open **Terminal → New Terminal**.
4. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

5. Activate it:

   ```powershell
   .venv\Scripts\activate
   ```

6. Install dependencies:

   ```powershell
   pip install -r requirements.txt
   ```

7. Copy `.env.example` to a new file named `.env`.
8. Open `.env` and replace `replace_with_your_real_api_key` with your own key.
9. Run the server:

   ```powershell
   python app.py
   ```

10. Open http://127.0.0.1:5000 in your browser.

## Test conversation memory

Send these messages in the same conversation:

1. My name is Nandu.
2. I am learning Python.
3. What programming language am I learning?
4. What is my name?
5. Explain how Python can help me in my studies.

The bot should use the earlier context when answering messages 3 and 4. Test with your own example too.

## Context management

The backend stores a short history per conversation ID and truncates it to the latest 10 messages. This limits the context sent to the model. Because the history is in server memory, it is lost when the server restarts. This project is a learning/demo implementation, not a production deployment.

## Error handling

The backend validates incoming messages and returns a readable JSON error when the API request fails. Technical details are logged on the server; they are not sent to the browser.

## Security

- Never commit `.env` or share your API key.
- `.gitignore` excludes `.env`.
- If a key is accidentally uploaded, revoke it with the provider and create a replacement.

## Upload to GitHub

Create a **public** repository on GitHub, then from this project folder run:

```bash
git init
git add .
git status
git commit -m "Build LLM chatbot with conversation memory"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/llm-chatbot.git
git push -u origin main
```

Replace `YOUR_USERNAME` with your GitHub username. Before committing, confirm `.env` is not listed by `git status`. Do not upload secrets.

## Limitations and future improvements

- In-memory history is lost when the server restarts.
- This demo does not include user login, persistent database storage, or production rate limiting.
- The Gemini model name may need to be changed in `.env` if it is unavailable for your account. The app retries temporarily overloaded models and then tries its built-in fallbacks.
- <img width="1920" height="1080" alt="Screenshot (98)" src="https://github.com/user-attachments/assets/f55af51b-1d8c-44be-861e-8fdb24b26210" />
- <img width="1920" height="1080" alt="Screenshot (95)" src="https://github.com/user-attachments/assets/100b2b97-c4eb-4365-9c8d-366909786ac2" />
-<img width="1920" height="1080" alt="Screenshot (96)" src="https://github.com/user-attachments/assets/724c8162-c627-48a3-ac54-2c67369ea888" />





