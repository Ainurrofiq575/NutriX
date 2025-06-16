from flask import Flask, request, jsonify, render_template
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer
import torch
from typing import Dict, Any, Optional
import os
import re

app = Flask(__name__)

# Global variables to store model and embeddings
model = None
food_embeddings = None
food_names = None
df = None

def clean_food_name(name: str) -> str:
    """Clean food name by removing special characters and making it more readable"""
    # Remove text after comma and convert to title case
    name = name.split(',')[0].strip().title()
    # Remove special characters but keep spaces
    name = re.sub(r'[^\w\s]', '', name)
    return name

def load_model_and_data():
    """Load the model and precompute embeddings for all food names"""
    global model, food_embeddings, food_names, df
    
    # Load the model
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    
    # Load the food dataset
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        df = pd.read_csv(os.path.join(current_dir, 'food.csv'))
        
        # Get food names from the first column and clean them
        food_names = df.iloc[:, 0].tolist()
        clean_names = [clean_food_name(name) for name in food_names]
        
        # Add clean names as a new column
        df['clean_name'] = clean_names
        
        # Compute embeddings for clean food names
        food_embeddings = model.encode(clean_names, convert_to_tensor=True)
        print(f"Successfully loaded {len(food_names)} food items")
        
        # Print column names for debugging
        print("Available columns:", df.columns.tolist())
        return True
    except Exception as e:
        print(f"Error loading dataset: {e}")
        return False

def find_closest_food(food_name: str) -> Optional[Dict[str, Any]]:
    """Find the closest matching food using semantic search with Sentence Transformers"""
    if model is None or food_embeddings is None or df is None:
        if not load_model_and_data():
            return None
    
    try:
        # Clean the input food name
        clean_query = clean_food_name(food_name)
        
        # Encode the query
        query_embedding = model.encode(clean_query, convert_to_tensor=True)
        
        # Calculate cosine similarities
        cos_scores = torch.nn.functional.cosine_similarity(query_embedding.unsqueeze(0), food_embeddings)
        
        # Get the best match
        best_match_score = torch.max(cos_scores).item()
        
        if best_match_score >= 0.6:  # Threshold for minimum similarity
            best_match_idx = torch.argmax(cos_scores).item()
            return df.iloc[best_match_idx]
        return None
        
    except Exception as e:
        print(f"Error in semantic search: {e}")
        return None

def extract_food_name_from_prompt(prompt: str) -> str:
    """Extract food name from the prompt text"""
    # Try to find text between quotes
    match = re.search(r'"([^"]+)"', prompt)
    if match:
        return match.group(1)
    
    # If no quotes found, try to find text after "apakah"
    match = re.search(r'apakah\s+(.+?)\s+dan', prompt, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return prompt

def format_nutrition_response(food_data: pd.Series) -> str:
    """Format the nutrition data into a simple response format"""
    # Get the original food name (with details)
    original_name = food_data.iloc[0]
    clean_name = food_data['clean_name']
    
    try:
        response = f"""Nama: {clean_name}
Detail: {original_name}

Informasi Nutrisi (per 100g):"""

        # Group nutrients by category
        nutrients = {
            'Makronutrien': [],
            'Vitamin': [],
            'Mineral': [],
            'Lemak': [],
            'Lainnya': []
        }

        for col in food_data.index:
            col_name = str(col).lower()
            value = food_data[col]
            
            # Skip non-nutritional columns
            if any(skip in col_name for skip in ['clean_name', 'ndb_no', 'data_src', 'gm_wgt', 'deriv_code']):
                continue
            
            # Format numerical values
            if isinstance(value, (int, float)) and not pd.isna(value) and value != 0:
                # Clean up column name by removing prefixes and other cleanup
                display_name = col_name.replace('data.', '')
                display_name = display_name.replace('vitamins.', '')
                display_name = display_name.replace('major minerals.', '')
                display_name = display_name.replace('fat.', '')
                display_name = display_name.replace('household weights.', '')
                display_name = display_name.replace('1st', 'First')
                display_name = display_name.replace('_', ' ').title()
                display_name = re.sub(r'\([^)]*\)', '', display_name).strip()
                
                # Format the value with unit
                if 'kcal' in col_name.lower():
                    formatted_value = f"{value:.1f} kkal"
                elif any(unit in col_name.lower() for unit in ['mg)', 'mg']):
                    formatted_value = f"{value:.1f} mg"
                elif any(unit in col_name.lower() for unit in ['µg)', 'ug']):
                    formatted_value = f"{value:.1f} µg"
                else:
                    formatted_value = f"{value:.1f} g"

                # Categorize the nutrient
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

        # Add each category to response if it has items
        for category, items in nutrients.items():
            if items:
                response += f"\n\n{category}:"
                for item in sorted(items):
                    response += f"\n- {item}"  # Changed bullet point to dash

        return response

    except Exception as e:
        print(f"Error formatting response: {e}")
        return f"Error: Could not format nutrition data for {clean_name}"

def analyze_with_nutrix(prompt: str, image_data: dict = None) -> str:
    """Analyze food using Nutrix model"""
    try:
        # Currently we only support text analysis
        if image_data:
            raise Exception("Maaf, analisis gambar belum didukung oleh model Nutrix")
        
        # Extract food name from prompt
        food_name = extract_food_name_from_prompt(prompt)
        
        # Find the closest matching food
        result = find_closest_food(food_name)
        
        if result is not None:
            return format_nutrition_response(result)
        else:
            return f"""Makanan "{food_name}" tidak ditemukan dalam database.
Coba masukkan nama makanan yang lebih umum."""
            
    except Exception as e:
        print(f"Nutrix Error: {str(e)}")
        raise

@app.route('/api/nutrition', methods=['POST'])
def get_nutrition():
    data = request.get_json()
    food_name = data.get('food_name', '')
    
    if not food_name:
        return jsonify({'error': 'Food name is required'}), 400
    
    result = find_closest_food(food_name)
    if result:
        return jsonify({'success': True, 'data': result})
    return jsonify({'success': False, 'error': 'Food not found'}), 404

# Create templates directory and HTML template
os.makedirs('templates', exist_ok=True)

# Initialize the model when the module is imported
load_model_and_data()

if __name__ == '__main__':
    app.run(debug=True)