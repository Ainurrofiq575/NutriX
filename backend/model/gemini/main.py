"""
Gemini AI Model Handler
----------------------
Modul untuk mengintegrasikan Google's Gemini AI.
Mendukung analisis teks dan gambar makanan dengan model generatif.

Features:
1. Analisis teks - Menganalisis deskripsi makanan
2. Analisis gambar - Menganalisis gambar makanan
3. Konfigurasi otomatis - Setup API key dan model
"""

import os
import base64
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables untuk API key
load_dotenv()

def init_gemini():
    """
    Inisialisasi model Gemini AI
    
    Proses:
    1. Ambil API key dari environment
    2. Konfigurasi Gemini dengan API key
    3. Load model generatif terbaru
    
    Returns:
        GenerativeModel: Instance model Gemini yang siap digunakan
        
    Raises:
        ValueError: Jika GEMINI_API_KEY tidak dikonfigurasi
    """
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")
    
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

def analyze_with_gemini(prompt: str, image_data: dict = None):
    """
    Analisis makanan menggunakan Gemini AI
    
    Mendukung dua mode:
    1. Analisis teks - Menggunakan prompt untuk analisis makanan
    2. Analisis gambar - Menggunakan gambar + prompt untuk analisis visual
    
    Args:
        prompt: String prompt untuk analisis
        image_data: Dict berisi mime_type dan data gambar dalam base64 (opsional)
    
    Returns:
        str: Hasil analisis dari Gemini AI
        
    Raises:
        Exception: Jika terjadi error saat analisis
    """
    try:
        # Inisialisasi model
        model = init_gemini()
        
        if image_data:
            # Mode analisis gambar
            response = model.generate_content(
                contents=[
                    {
                        "parts": [
                            {"text": prompt},
                            {
                                "inline_data": {
                                    "mime_type": image_data["mime_type"],
                                    "data": image_data["data"]
                                }
                            }
                        ]
                    }
                ]
            )
        else:
            # Mode analisis teks
            response = model.generate_content(
                contents=[
                    {
                        "parts": [
                            {"text": prompt}
                        ]
                    }
                ]
            )

        return response.text if response.text else None
    except Exception as e:
        print(f"Gemini Error: {str(e)}")
        raise
