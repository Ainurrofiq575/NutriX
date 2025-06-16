# Nutrix AI Backend

Backend Flask untuk aplikasi Nutrix AI, mengintegrasikan Gemini AI dan model nutrisi kustom.

## Struktur

```
backend/
├── model/
│   ├── gemini/        # Integrasi Google Gemini AI
│   │   └── main.py    # Handler Gemini AI
│   ├── nutrix/        # Model nutrisi kustom
│   │   ├── main.py    # Logic pencarian semantik
│   │   └── food.csv   # Database nutrisi makanan
│   └── prompts.py     # Template prompt AI
└── main.py            # Entry point dan API routes
```

## Setup

1. Buat virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Unix
# atau
.\venv\Scripts\activate  # Windows
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Setup environment variables:

```bash
# Buat file .env
GEMINI_API_KEY=your_gemini_api_key
```

4. Jalankan server:

```bash
python main.py
```

Server akan berjalan di `http://localhost:5000`

## API Endpoints

### POST /api/analyze

Analisis makanan menggunakan model AI.

Request:

```json
{
  "model": "gemini|nutrix",
  "text": "nama makanan",
  // atau
  "image": "file gambar"
}
```

Response:

```json
{
  "success": true,
  "data": {
    "content": "hasil analisis..."
  }
}
```

## Dependencies Utama

- Flask
- Sentence Transformers
- Google Generative AI
- Pandas
- PyTorch
