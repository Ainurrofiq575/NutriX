"""
Modul Model Nutrix
-----------------
Modul ini mengimplementasikan sistem analisis nutrisi makanan menggunakan pencarian semantik.
Menggunakan model sentence transformer untuk menemukan makanan yang paling mirip
dari database dan mengembalikan informasi nutrisinya.

Komponen Utama:
1. Database Makanan - Memuat data dari CSV
2. Pencarian Semantik - Menggunakan sentence transformers untuk pencocokan nama makanan
3. Format Nutrisi - Mengorganisir dan memformat data nutrisi berdasarkan kategori
4. Endpoint API - Menyediakan endpoint HTTP untuk analisis makanan
"""

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from typing import Dict, Any, Optional, List, Tuple
import os
import re
from ..gemini.main import detect_food_from_image

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Variabel global untuk menyimpan model dan data
model = None  # Instance dari SentenceTransformer
food_embeddings = None  # Tensor berisi embedding nama makanan
food_names = None  # List nama makanan original
df = None  # DataFrame berisi data nutrisi makanan

# Kamus terjemahan sederhana untuk kata-kata umum dalam makanan
FOOD_TRANSLATIONS = {
    # Bahan dasar
    "nasi": ["rice", "cooked rice"],
    "mie": ["noodle", "noodles", "pasta"],
    "roti": ["bread", "toast"],
    "telur": ["egg", "eggs"],
    "ayam": ["chicken"],
    "bebek": ["duck"],
    "ikan": ["fish"],
    "daging": ["meat", "beef"],
    "sayur": ["vegetable"],
    "buah": ["fruit"],
    "beras": ["rice", "uncooked rice"],
    "jagung": ["corn", "maize"],
    "kacang": ["bean", "nut", "peanut"],
    "tahu": ["tofu"],
    "tempe": ["tempeh"],
    "udang": ["shrimp", "prawn"],
    "cumi": ["squid", "calamari"],
    "kepiting": ["crab"],
    
    # Daging dan Protein
    "sapi": ["beef", "cow meat"],
    "kambing": ["goat", "mutton"],
    "babi": ["pork", "pig meat"],
    "bebek": ["duck"],
    "kelinci": ["rabbit"],
    "ati": ["liver"],
    "ampela": ["gizzard"],
    "paru": ["lung"],
    "usus": ["intestine"],
    "bakso": ["meatball"],
    "sosis": ["sausage"],
    
    # Sayuran
    "wortel": ["carrot"],
    "bayam": ["spinach"],
    "kangkung": ["water spinach"],
    "kentang": ["potato"],
    "kubis": ["cabbage"],
    "kol": ["cabbage"],
    "brokoli": ["broccoli"],
    "kembang kol": ["cauliflower"],
    "terong": ["eggplant", "aubergine"],
    "timun": ["cucumber"],
    "tomat": ["tomato"],
    "buncis": ["green beans"],
    "kacang panjang": ["long beans"],
    "labu": ["pumpkin", "squash"],
    "pare": ["bitter gourd"],
    "selada": ["lettuce"],
    "sawi": ["mustard greens", "chinese cabbage"],
    "tauge": ["bean sprouts"],
    "jamur": ["mushroom"],
    
    # Buah-buahan
    "pisang": ["banana"],
    "apel": ["apple"],
    "jeruk": ["orange"],
    "mangga": ["mango"],
    "pepaya": ["papaya"],
    "semangka": ["watermelon"],
    "melon": ["melon"],
    "anggur": ["grape"],
    "nanas": ["pineapple"],
    "alpukat": ["avocado"],
    "stroberi": ["strawberry"],
    "rambutan": ["rambutan"],
    "durian": ["durian"],
    "salak": ["snake fruit"],
    "manggis": ["mangosteen"],
    "sirsak": ["soursop"],
    
    # Bumbu dan Rempah
    "bawang": ["onion"],
    "bawang putih": ["garlic"],
    "bawang merah": ["shallot"],
    "jahe": ["ginger"],
    "kunyit": ["turmeric"],
    "lengkuas": ["galangal"],
    "serai": ["lemongrass"],
    "cabai": ["chili", "pepper"],
    "lada": ["pepper", "black pepper"],
    "ketumbar": ["coriander"],
    "jintan": ["cumin"],
    "pala": ["nutmeg"],
    "kayu manis": ["cinnamon"],
    "kemiri": ["candlenut"],
    "daun salam": ["bay leaf"],
    "daun jeruk": ["kaffir lime leaf"],
    
    # Metode memasak
    "goreng": ["fried", "deep fried"],
    "rebus": ["boiled", "steamed"],
    "panggang": ["grilled", "roasted", "baked"],
    "kukus": ["steamed"],
    "tumis": ["stir fried", "sauteed"],
    "bakar": ["grilled", "barbecued"],
    "sangrai": ["roasted", "toasted"],
    "tim": ["steamed"],
    
    # Jenis makanan
    "sup": ["soup"],
    "soto": ["soup", "traditional soup"],
    "sambal": ["chili sauce", "hot sauce"],
    "kecap": ["soy sauce"],
    "gulai": ["curry"],
    "sate": ["satay", "skewered meat"],
    "rendang": ["rendang"],
    "opor": ["coconut milk curry"],
    "pepes": ["steamed in banana leaf"],
    "gado-gado": ["vegetable salad"],
    "nasi goreng": ["fried rice"],
    "mie goreng": ["fried noodles"],
    "bubur": ["porridge", "congee"],
    
    # Rasa dan Tekstur
    "pedas": ["spicy", "hot"],
    "manis": ["sweet"],
    "asin": ["salty"],
    "asam": ["sour"],
    "pahit": ["bitter"],
    "gurih": ["savory", "umami"],
    "renyah": ["crispy", "crunchy"],
    "lembut": ["soft", "tender"],
    "keras": ["hard"],
    "kenyal": ["chewy"],
    
    # Minuman
    "jus": ["juice"],
    "susu": ["milk"],
    "teh": ["tea"],
    "kopi": ["coffee"],
    "es": ["ice", "iced"],
    "panas": ["hot"],
    "dingin": ["cold"],
    
    # Hidangan Penutup
    "kue": ["cake", "pastry"],
    "puding": ["pudding"],
    "es krim": ["ice cream"],
    "coklat": ["chocolate"],
    "keju": ["cheese"],
    
    # Ukuran dan Porsi
    "sepotong": ["piece", "slice"],
    "seporsi": ["portion", "serving"],
    "secangkir": ["cup"],
    "segelas": ["glass"],
    "sendok": ["spoon", "tablespoon"],
    "mangkok": ["bowl"],
    "piring": ["plate"]
}

def translate_to_english(food_name: str) -> List[str]:
    """
    Menerjemahkan nama makanan dari Bahasa Indonesia ke Bahasa Inggris
    menggunakan kamus sederhana dan aturan penerjemahan.
    
    Args:
        food_name: Nama makanan dalam Bahasa Indonesia
    
    Returns:
        List[str]: Daftar kemungkinan terjemahan dalam Bahasa Inggris
    """
    # Bersihkan dan lowercase input
    food_name = food_name.lower().strip()
    translations = []
    
    # Cek apakah ada terjemahan langsung
    words = food_name.split()
    translated_parts = []
    
    for word in words:
        if word in FOOD_TRANSLATIONS:
            translated_parts.append(FOOD_TRANSLATIONS[word])
        else:
            # Jika tidak ada terjemahan, gunakan kata asli
            translated_parts.append([word])
    
    # Generate semua kemungkinan kombinasi terjemahan
    def generate_combinations(parts: List[List[str]], current: str = "", index: int = 0) -> List[str]:
        if index == len(parts):
            translations.append(current.strip())
            return
        
        for translation in parts[index]:
            new_current = current + " " + translation if current else translation
            generate_combinations(parts, new_current, index + 1)
    
    generate_combinations(translated_parts)
    
    # Jika tidak ada terjemahan yang ditemukan, kembalikan input asli
    if not translations:
        translations = [food_name]
    
    return translations

def clean_food_name(name: str) -> str:
    """
    Membersihkan nama makanan dari karakter khusus
    
    Args:
        name: Nama makanan yang akan dibersihkan
    5
    Returns:
        str: Nama makanan yang sudah dibersihkan
    """
    # Hapus teks setelah koma dan ubah ke title case
    name = name.split(',')[0].strip().title()
    # Hapus karakter khusus tapi pertahankan spasi
    name = re.sub(r'[^\w\s]', '', name)
    return name

def load_model_and_data():
    """
    Inisialisasi model dan data:
    1. Load model sentence-transformer
    2. Baca database makanan dari CSV
    3. Bersihkan nama makanan
    4. Hitung embedding untuk setiap nama makanan
    
    Returns:
        bool: True jika berhasil, False jika gagal
    """
    global model, food_embeddings, food_names, df
    
    # Load model sentence-transformer
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    try:
        # Baca file CSV dari direktori yang sama
        current_dir = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(current_dir, 'food.csv'))
        
        # Ambil dan bersihkan nama makanan
        food_names = df.iloc[:, 0].tolist()
        clean_names = [clean_food_name(name) for name in food_names]
        df['clean_name'] = clean_names
        
        # Hitung embedding untuk pencarian semantik
        food_embeddings = model.encode(clean_names, convert_to_tensor=True)
        print(f"Berhasil memuat {len(food_names)} item makanan")
        print("Kolom yang tersedia:", df.columns.tolist())
        return True
    except Exception as e:
        print(f"Error saat memuat dataset: {e}")
        return False

def find_closest_food(food_name: str) -> Optional[Dict[str, Any]]:
    """
    Mencari makanan yang paling mirip menggunakan pencarian semantik
    dengan dukungan untuk input Bahasa Indonesia
    
    Proses:
    1. Terjemahkan input Bahasa Indonesia ke Bahasa Inggris
    2. Bersihkan nama makanan input
    3. Hitung embedding untuk setiap terjemahan
    4. Hitung similarity dengan semua makanan di database
    5. Ambil makanan dengan similarity tertinggi (jika di atas threshold)
    
    Args:
        food_name: Nama makanan yang dicari (dalam Bahasa Indonesia)
    
    Returns:
        Optional[Dict]: Data makanan jika ditemukan, None jika tidak
    """
    if model is None or food_embeddings is None or df is None:
        if not load_model_and_data():
            return None
    
    try:
        # Terjemahkan query ke Bahasa Inggris
        english_translations = translate_to_english(food_name)
        best_match = None
        best_score = 0
        
        # Coba setiap kemungkinan terjemahan
        for translation in english_translations:
            # Bersihkan nama makanan input
            clean_query = clean_food_name(translation)
            
            # Hitung embedding untuk query
            query_embedding = model.encode(clean_query, convert_to_tensor=True)
            
            # Hitung cosine similarity
            cos_scores = torch.nn.functional.cosine_similarity(query_embedding.unsqueeze(0), food_embeddings)
            
            # Update best match jika ditemukan yang lebih baik
            current_score = torch.max(cos_scores).item()
            if current_score > best_score:
                best_score = current_score
                best_match_idx = torch.argmax(cos_scores).item()
                best_match = df.iloc[best_match_idx]
        
        # Threshold 0.5 untuk memastikan hasil yang relevan
        # Threshold diturunkan karena kemungkinan perbedaan bahasa
        if best_score >= 0.5:
            return best_match
        return None
        
    except Exception as e:
        print(f"Error dalam pencarian semantik: {e}")
        return None

def extract_food_name_from_prompt(prompt: str) -> str:
    """
    Ekstrak nama makanan dari prompt pengguna
    
    Mencoba beberapa pattern:
    1. Teks dalam tanda kutip
    2. Teks setelah kata 'apakah'
    3. Jika tidak ada pattern yang cocok, gunakan seluruh prompt
    
    Args:
        prompt: Prompt dari pengguna
    
    Returns:
        str: Nama makanan yang diekstrak
    """
    # Coba cari teks dalam tanda kutip
    match = re.search(r'"([^"]+)"', prompt)
    if match:
        return match.group(1)
    
    # Jika tidak ada tanda kutip, cari setelah 'apakah'
    match = re.search(r'apakah\s+(.+?)\s+dan', prompt, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return prompt

def format_nutrition_response(food_data: pd.Series) -> str:
    """
    Format data nutrisi ke dalam respons yang terstruktur
    
    Mengorganisir nutrisi dalam kategori:
    - Makronutrien (protein, karbohidrat, dll)
    - Vitamin
    - Mineral
    - Lemak
    - Lainnya
    
    Args:
        food_data: Series pandas berisi data nutrisi
    
    Returns:
        str: Respons terformat dengan kategori nutrisi
    """
    # Ambil nama makanan (original dan yang sudah dibersihkan)
    original_name = food_data.iloc[0]
    clean_name = food_data['clean_name']
    
    try:
        # Buat header respons
        response = f"""Nama: {clean_name}
Detail: {original_name}

Informasi Nutrisi (per 100g):"""

        # Kelompokkan nutrisi berdasarkan kategori
        nutrients = {
            'Makronutrien': [],
            'Vitamin': [],
            'Mineral': [],
            'Lemak': [],
            'Lainnya': []
        }

        # Proses setiap kolom nutrisi
        for col in food_data.index:
            col_name = str(col).lower()
            value = food_data[col]
            
            # Skip kolom non-nutrisi
            if any(skip in col_name for skip in ['clean_name', 'ndb_no', 'data_src', 'gm_wgt', 'deriv_code']):
                continue
            
            # Format nilai numerik dan kategorikan nutrisi
            if isinstance(value, (int, float)) and not pd.isna(value) and value != 0:
                # Bersihkan nama kolom
                display_name = col_name.replace('data.', '')
                display_name = display_name.replace('vitamins.', '')
                display_name = display_name.replace('major minerals.', '')
                display_name = display_name.replace('fat.', '')
                display_name = display_name.replace('household weights.', '')
                display_name = display_name.replace('1st', 'First')
                display_name = display_name.replace('_', ' ').title()
                display_name = re.sub(r'\([^)]*\)', '', display_name).strip()
                
                # Format nilai dengan unit yang sesuai
                if 'kcal' in col_name.lower():
                    formatted_value = f"{value:.1f} kkal"
                elif any(unit in col_name.lower() for unit in ['mg)', 'mg']):
                    formatted_value = f"{value:.1f} mg"
                elif any(unit in col_name.lower() for unit in ['µg)', 'ug']):
                    formatted_value = f"{value:.1f} µg"
                else:
                    formatted_value = f"{value:.1f} g"

                # Kategorikan nutrisi
                nutrient_line = f"{display_name}: {formatted_value}"
                
                if any(macro in display_name.lower() for macro in ['protein', 'carbohydrate', 'sugar', 'fiber']):
                    nutrients['Makronutrien'].append(nutrient_line)
                elif 'vitamin' in display_name.lower():
                    nutrients['Vitamin'].append(nutrient_line)
                elif any(mineral in display_name.lower() for mineral in ['iron', 'zinc', 'copper', 'manganese', 'minerals']):
                    nutrients['Mineral'].append(nutrient_line)
                elif any(fat in display_name.lower() for fat in ['fat', 'lipid']):
                    nutrients['Lemak'].append(nutrient_line)
                else:
                    nutrients['Lainnya'].append(nutrient_line)

        # Tambahkan setiap kategori ke respons
        for category, items in nutrients.items():
            if items:
                response += f"\n\n{category}:"
                for item in sorted(items):
                    response += f"\n- {item}"

        return response

    except Exception as e:
        print(f"Error saat memformat respons: {e}")
        return f"Error: Tidak dapat memformat data nutrisi untuk {clean_name}"

# konfigurasi gambar di model nutrix
def analyze_with_nutrix(prompt: str, image_data: dict = None) -> str:
    """
    Analisis makanan menggunakan model Nutrix
    
    Proses:
    1. Jika ada gambar, deteksi makanan menggunakan Gemini
    2. Cari makanan di database
    3. Format dan return informasi nutrisi
    
    Args:
        prompt: Prompt dari pengguna (nama makanan)
        image_data: Data gambar dalam format base64
    
    Returns:
        str: Informasi nutrisi terformat atau pesan error
    """
    try:
        # Jika ada gambar, gunakan Gemini untuk deteksi
        if image_data:
            food_name = detect_food_from_image(image_data)
        else:
            food_name = extract_food_name_from_prompt(prompt)
        
        # Cari makanan di database
        result = find_closest_food(food_name)
        
        if result is not None:
            return format_nutrition_response(result)
        else:
            return f"""Makanan "{food_name}" tidak ditemukan dalam database.
Coba masukkan nama makanan yang lebih umum."""
            
    except Exception as e:
        print(f"Error Nutrix: {str(e)}")
        raise

@app.route('/api/nutrition', methods=['POST'])
def get_nutrition():
    """
    Endpoint API untuk analisis nutrisi
    
    Expects:
        POST request dengan JSON body berisi 'food_name' dan/atau 'image_data'
    
    Returns:
        JSON response dengan data nutrisi atau error 
    """
    try:
        data = request.get_json()   # Ambil data dari user/terima data dari frontend
        if data is None:
            return jsonify({'success': False, 'error': 'Invalid JSON data'}), 400
            
        food_name = data.get('food_name', '')
        image_data = data.get('image_data')
        
        if not food_name and not image_data:
            return jsonify({'success': False, 'error': 'Nama makanan atau gambar harus diisi'}), 400
        
        try:
            result = analyze_with_nutrix(food_name, image_data) # Analisis makanan dengan model Nutrix dan teruskan
            return jsonify({'success': True, 'data': result})
        except Exception as e:
            print(f"Error in analyze_with_nutrix: {str(e)}")
            return jsonify({'success': False, 'error': str(e)}), 500
            
    except Exception as e:
        print(f"Error processing request: {str(e)}")
        return jsonify({'success': False, 'error': 'Invalid request format'}), 400

# Buat direktori templates
os.makedirs('templates', exist_ok=True)

# Inisialisasi model saat modul diimport
load_model_and_data()

if __name__ == '__main__':
    app.run(debug=True)