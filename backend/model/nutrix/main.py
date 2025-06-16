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
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from typing import Dict, Any, Optional
import os
import re

app = Flask(__name__)

# Variabel global untuk menyimpan model dan data
model = None  # Instance dari SentenceTransformer
food_embeddings = None  # Tensor berisi embedding nama makanan
food_names = None  # List nama makanan original
df = None  # DataFrame berisi data nutrisi makanan

def clean_food_name(name: str) -> str:
    """
    Membersihkan nama makanan dari karakter khusus
    
    Args:
        name: Nama makanan yang akan dibersihkan
    
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
    
    Proses:
    1. Bersihkan nama makanan input
    2. Hitung embedding untuk input
    3. Hitung similarity dengan semua makanan di database
    4. Ambil makanan dengan similarity tertinggi (jika di atas threshold)
    
    Args:
        food_name: Nama makanan yang dicari
    
    Returns:
        Optional[Dict]: Data makanan jika ditemukan, None jika tidak
    """
    if model is None or food_embeddings is None or df is None:
        if not load_model_and_data():
            return None
    
    try:
        # Bersihkan nama makanan input
        clean_query = clean_food_name(food_name)
        
        # Hitung embedding untuk query
        query_embedding = model.encode(clean_query, convert_to_tensor=True)
        
        # Hitung cosine similarity
        cos_scores = torch.nn.functional.cosine_similarity(query_embedding.unsqueeze(0), food_embeddings)
        
        # Ambil hasil terbaik
        best_match_score = torch.max(cos_scores).item()
        
        # Threshold 0.6 untuk memastikan hasil yang relevan
        if best_match_score >= 0.6:
            best_match_idx = torch.argmax(cos_scores).item()
            return df.iloc[best_match_idx]
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

def analyze_with_nutrix(prompt: str, image_data: dict = None) -> str:
    """
    Analisis makanan menggunakan model Nutrix
    
    Proses:
    1. Ekstrak nama makanan dari prompt
    2. Cari makanan di database
    3. Format dan return informasi nutrisi
    
    Args:
        prompt: Prompt dari pengguna (nama makanan)
        image_data: Data gambar (belum didukung)
    
    Returns:
        str: Informasi nutrisi terformat atau pesan error
    """
    try:
        # Saat ini hanya mendukung analisis teks
        if image_data:
            raise Exception("Maaf, analisis gambar belum didukung oleh model Nutrix")
        
        # Ekstrak nama makanan dari prompt
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
        POST request dengan JSON body berisi 'food_name'
    
    Returns:
        JSON response dengan data nutrisi atau error
    """
    data = request.get_json()
    food_name = data.get('food_name', '')
    
    if not food_name:
        return jsonify({'error': 'Nama makanan harus diisi'}), 400
    
    result = find_closest_food(food_name)
    if result:
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'error': 'Makanan tidak ditemukan'}), 404

# Buat direktori templates
os.makedirs('templates', exist_ok=True)

# Inisialisasi model saat modul diimport
load_model_and_data()

if __name__ == '__main__':
    app.run(debug=True)