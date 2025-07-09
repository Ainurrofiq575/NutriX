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
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Configure Gemini API with the correct environment variable
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found in environment variables")

genai.configure(api_key=GEMINI_API_KEY)

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

def detect_food_from_image(image_data: str) -> str:
    """
    Detect food from base64 encoded image using Gemini 
    Returns only the food name in English
    
    Args:
        image_data: Base64 encoded image string
    
    Returns:
        str: Detected food name (e.g. "chicken", "rice", "egg")
    """
    try:
        # Decode base64 image
        image_bytes = base64.b64decode(image_data.split(',')[1])
        image = Image.open(io.BytesIO(image_bytes))
        
        # Initialize Gemini model
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create prompt for food detection
        prompt = """You are a food detection AI. Look at this image and tell me what food item it is.
        Return ONLY the food name in English, single word if possible. For example:
        - "chicken" for chicken dishes
        - "rice" for rice dishes
        - "noodles" for noodle dishes
        DO NOT include any descriptions or additional text."""
        
        # Generate response
        response = model.generate_content([prompt, image])
        
        # Clean and return the food name
        food_name = response.text.strip().lower()
        food_name = food_name.replace('"', '').replace("'", "")
        
        return food_name
        
    except Exception as e:
        print(f"Error detecting food: {str(e)}")
        raise
