# Nutrix AI 🍎

Aplikasi analisis nutrisi makanan menggunakan AI. Mendukung input teks dan gambar untuk menganalisis kandungan nutrisi dalam makanan.

## Fitur

- 🤖 Dua model AI:
  - **Gemini AI**: Analisis umum dan gambar makanan
  - **Nutrix**: Analisis detail nutrisi dari database
- 📱 Interface modern dan responsif
- 📸 Mendukung input gambar (drag & drop, paste, upload)
- 📝 Analisis teks langsung dengan nama makanan
- 🌙 Mode gelap/terang

## Teknologi

- **Frontend**: Next.js 14, TypeScript, Tailwind CSS
- **Backend**: Flask, Sentence Transformers
- **AI Models**: Google Gemini AI, Custom Nutrix Model
- **Database**: Food Nutrition CSV Database

## Cara Menjalankan

### Prerequisites

- Node.js 18+ dan npm/bun
- Python 3.8+
- Google Gemini API Key

### Setup

1. Clone repository:

```bash
git clone https://github.com/yourusername/nutrix-app.git
cd nutrix-app
```

2. Setup environment variables:

```bash
# Di root folder, buat .env
GEMINI_API_KEY=your_gemini_api_key
```

3. Jalankan Backend:

```bash
cd backend
python -m venv venv

# Unix
source venv/bin/activate
# windows
.\venv\Scripts\activate

pip install -r requirements.txt
python main.py
```

4. Jalankan Frontend:

```bash
cd frontend
bun install  # atau npm install
bun dev     # atau npm run dev
```

5. Buka aplikasi di browser:

```
http://localhost:3000
```

## Struktur Proyek

```
nutrix-app/
├── frontend/          # Next.js frontend
├── backend/           # Flask backend
│   ├── model/
│   │   ├── gemini/   # Gemini AI integration
│   │   └── nutrix/   # Custom nutrition model
│   └── main.py       # Backend entry point
└── README.md
```

## Penggunaan

1. Buka aplikasi di browser
2. Pilih model AI (Gemini/Nutrix)
3. Masukkan nama makanan atau upload gambar
4. Lihat hasil analisis nutrisi

## Catatan

- Model Gemini memerlukan API key dari Google
- Model Nutrix menggunakan database lokal (CSV)
- Analisis gambar hanya tersedia untuk model Gemini
