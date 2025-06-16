import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from model.prompts import create_food_analysis_prompt
from model.gemini.main import analyze_with_gemini
from model.nutrix.main import analyze_with_nutrix

# Initialize Flask app
app = Flask(__name__)
CORS(app)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    try:
        # Get model type from request
        model_type = request.form.get("model", "gemini")  # default to gemini if not specified
        
        if model_type not in ["gemini", "nutrix"]:
            return jsonify({
                "success": False,
                "error": "Model tidak valid. Gunakan 'gemini' atau 'nutrix'."
            }), 400

        # Handle image file
        if "image" in request.files:
            image_file = request.files["image"]
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Prepare image data
            image_data = {
                "mime_type": image_file.content_type,
                "data": image_base64
            }
            
            # Get prompt for image
            prompt = create_food_analysis_prompt(is_image=True)
            
            # Analyze with selected model
            if model_type == "gemini":
                result = analyze_with_gemini(prompt, image_data)
            else:  # nutrix
                result = analyze_with_nutrix(prompt, image_data)

        # Handle text input
        elif "text" in request.form:
            text = request.form["text"]
            
            # Get prompt for text
            prompt = create_food_analysis_prompt(text, is_image=False)
            
            # Analyze with selected model
            if model_type == "gemini":
                result = analyze_with_gemini(prompt)
            else:  # nutrix
                result = analyze_with_nutrix(prompt)
        else:
            return jsonify({
                "success": False,
                "error": "Mohon masukkan gambar atau teks untuk dianalisis"
            }), 400

        if not result:
            raise ValueError("Tidak ada respons dari model")

        return jsonify({
            "success": True,
            "data": {"content": result}
        })

    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            "success": False,
            "error": "Terjadi kesalahan pada server"
        }), 500

if __name__ == "__main__":
    app.run(debug=True, port=5000)