from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
import base64
import os
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# ─── Configure Gemini ────────────────────────────────────────────────────────
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ─── System prompt for crop disease expert ──────────────────────────────────
SYSTEM_PROMPT = """You are KrishiDoc, an expert agricultural plant pathologist and crop disease specialist.
Your job is to analyze crop images and provide detailed, structured advice to farmers.

When analyzing a crop image, always respond in the following structured format:

🌿 **CROP IDENTIFIED:** [Name of the crop]

🔴 **DISEASE DETECTED:** [Disease name or "No disease detected — crop appears healthy"]

📋 **SYMPTOMS OBSERVED:**
- [symptom 1]
- [symptom 2]
- [symptom 3]

⚠️ **SEVERITY LEVEL:** [Mild / Moderate / Severe / Critical]

💊 **TREATMENT & CURE:**
- [treatment step 1]
- [treatment step 2]
- [specific fungicide/pesticide/fertilizer if needed]

🛡️ **PRECAUTIONS:**
- [precaution 1]
- [precaution 2]
- [precaution 3]

🌱 **PREVENTION FOR FUTURE:**
- [prevention tip 1]
- [prevention tip 2]

📞 **RECOMMENDATION:** [Whether to consult a local agricultural expert or not]

If no image is provided but the user asks a crop-related question, answer it helpfully as a plant disease expert.
If the uploaded image is NOT a crop or plant, politely say so and ask for a valid crop image.
Always be empathetic toward farmers and use simple, actionable language."""


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "message": "KrishiDoc backend is running"})


@app.route("/analyze", methods=["POST"])
def analyze():
    """Analyze crop image and/or text message using Gemini Vision."""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data received"}), 400

        user_message = data.get("message", "").strip()
        image_data = data.get("image")  # base64 string
        chat_history = data.get("history", [])  # list of {role, text}

        parts = []

        # Add image if provided
        if image_data:
            try:
                # Strip data URL prefix if present
                if "," in image_data:
                    image_data = image_data.split(",")[1]
                image_bytes = base64.b64decode(image_data)
                img = Image.open(io.BytesIO(image_bytes))
                # Convert to RGB if needed
                if img.mode not in ("RGB", "L"):
                    img = img.convert("RGB")
                parts.append(img)
            except Exception as e:
                return jsonify({"error": f"Invalid image data: {str(e)}"}), 400

        # Build prompt from history + current message
        conversation_context = ""
        if chat_history:
            for turn in chat_history[-6:]:  # keep last 6 turns for context
                role = "User" if turn["role"] == "user" else "KrishiDoc"
                conversation_context += f"{role}: {turn['text']}\n"

        full_prompt = SYSTEM_PROMPT + "\n\n"
        if conversation_context:
            full_prompt += f"Conversation so far:\n{conversation_context}\n"
        if image_data:
            full_prompt += "The user has uploaded a crop image. Analyze it carefully.\n"
        full_prompt += f"User: {user_message or 'Please analyze this crop image.'}"

        parts.append(full_prompt)

        # Call Gemini
        response = model.generate_content(parts)
        reply = response.text

        return jsonify({"reply": reply, "status": "success"})

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


@app.route("/chat", methods=["POST"])
def chat():
    """Text-only chat for follow-up questions."""
    try:
        data = request.get_json()
        user_message = data.get("message", "").strip()
        chat_history = data.get("history", [])

        if not user_message:
            return jsonify({"error": "Message cannot be empty"}), 400

        conversation_context = ""
        if chat_history:
            for turn in chat_history[-8:]:
                role = "User" if turn["role"] == "user" else "KrishiDoc"
                conversation_context += f"{role}: {turn['text']}\n"

        full_prompt = (
            SYSTEM_PROMPT
            + "\n\n"
            + (f"Conversation so far:\n{conversation_context}\n" if conversation_context else "")
            + f"User: {user_message}"
        )

        response = model.generate_content(full_prompt)
        return jsonify({"reply": response.text, "status": "success"})

    except Exception as e:
        return jsonify({"error": str(e), "status": "error"}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)