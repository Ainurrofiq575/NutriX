import os
import base64
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def init_gemini():
    """Initialize Gemini AI model"""
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    if not GEMINI_API_KEY:
        raise ValueError("GEMINI_API_KEY is not configured")
    
    genai.configure(api_key=GEMINI_API_KEY)
    return genai.GenerativeModel("gemini-2.0-flash")

def analyze_with_gemini(prompt: str, image_data: dict = None):
    """Analyze food using Gemini AI model"""
    try:
        model = init_gemini()
        
        if image_data:
            # Handle image analysis
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
            # Handle text analysis
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
