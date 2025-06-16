"""
Nutrix AI Backend Server
-----------------------
Server utama yang menangani request dari frontend untuk analisis makanan.
Mendukung dua model AI:
1. Gemini - Untuk analisis umum dan gambar
2. Nutrix - Untuk analisis nutrisi dari database

Flow:
1. Terima request dari frontend (gambar/teks)
2. Tentukan model yang digunakan (gemini/nutrix)
3. Proses input dan kirim ke model yang sesuai
4. Kembalikan hasil analisis ke frontend
"""

import base64
from flask import Flask, request, jsonify
from flask_cors import CORS
from model.prompts import create_food_analysis_prompt
from model.gemini.main import analyze_with_gemini
from model.nutrix.main import analyze_with_nutrix

# Inisialisasi Flask app dengan CORS
app = Flask(__name__)
CORS(app)

@app.route("/api/analyze", methods=["POST"])
def analyze():
    """
    Endpoint utama untuk analisis makanan
    
    Menerima:
    - model: string ('gemini' atau 'nutrix')
    - image: file (opsional)
    - text: string (opsional)
    
    Returns:
    - JSON response dengan hasil analisis atau error
    """
    try:
        # Validasi model yang dipilih
        model_type = request.form.get("model", "gemini")
        if model_type not in ["gemini", "nutrix"]:
            return jsonify({
                "success": False,
                "error": "Model tidak valid. Gunakan 'gemini' atau 'nutrix'."
            }), 400

        # Proses input gambar
        if "image" in request.files:
            # Baca dan encode gambar ke base64
            image_file = request.files["image"]
            image_bytes = image_file.read()
            image_base64 = base64.b64encode(image_bytes).decode("utf-8")
            
            # Siapkan data gambar untuk model
            image_data = {
                "mime_type": image_file.content_type,
                "data": image_base64
            }
            
            # Untuk gambar, gunakan prompt khusus analisis gambar
            prompt = create_food_analysis_prompt(is_image=True)
            
            # Analisis dengan model yang dipilih
            if model_type == "gemini":
                result = analyze_with_gemini(prompt, image_data)
            else:  # nutrix
                result = analyze_with_nutrix(prompt, image_data)

        # Proses input teks
        elif "text" in request.form:
            text = request.form["text"].strip()
            
            # Jika menggunakan Nutrix, langsung gunakan teks sebagai nama makanan
            if model_type == "nutrix":
                result = analyze_with_nutrix(text)
            else:
                # Untuk Gemini, buat prompt lengkap untuk analisis
                prompt = create_food_analysis_prompt(text, is_image=False)
                result = analyze_with_gemini(prompt)

        else:
            return jsonify({
                "success": False,
                "error": "Mohon masukkan gambar atau teks untuk dianalisis"
            }), 400

        # Validasi hasil analisis
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