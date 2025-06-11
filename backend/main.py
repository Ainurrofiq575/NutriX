import os
import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
import google.generativeai as genai
from dotenv import load_dotenv
from prompt import create_food_analysis_prompt

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Configure Google Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not configured")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        # Handle image file
        if "image" in request.files:
            image_file = request.files["image"]
            # Read and encode image
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Generate content with image
            response = model.generate_content([
                create_food_analysis_prompt(is_image=True),
                {
                    "inlineData": {
                        "data": image_base64,
                        "mimeType": image_file.content_type
                    }
                }
            ])
        # Handle text input
        elif "text" in request.form:
            text = request.form["text"]
            # Generate content with text
            response = model.generate_content(
                create_food_analysis_prompt(text, is_image=False)
            )
        else:
            return jsonify({
                "success": False,
                "error": "Mohon masukkan gambar atau teks untuk dianalisis"
            }), 400

        # Get response text
        response_text = response.text
        if not response_text:
            raise ValueError("Tidak ada respons dari AI")

        return jsonify({
            "success": True,
            "data": {"content": response_text}
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Terjadi kesalahan pada server"
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)