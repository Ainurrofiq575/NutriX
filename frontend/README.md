# Nutrix AI Frontend

Frontend Next.js untuk aplikasi Nutrix AI dengan UI modern dan responsif.

## Struktur

```
frontend/
├── app/                # App router Next.js
│   └── page.tsx        # Halaman utama
├── components/         # React components
│   ├── Header.tsx     # Header dengan model selector
│   ├── InputArea.tsx  # Area input teks/gambar
│   ├── MessageCard.tsx # Komponen chat message
│   └── ...
└── public/            # Assets statis
```

## Setup

1. Install dependencies:

```bash
bun install  # atau npm install
```

2. Jalankan development server:

```bash
bun dev  # atau npm run dev
```

Aplikasi akan berjalan di `http://localhost:3000`

## Fitur UI

- Model selector (Gemini/Nutrix)
- Input teks langsung
- Upload gambar (drag & drop, paste, file upload)
- Chat-like interface
- Dark/light mode
- Loading states
- Error handling

## Tech Stack

- Next.js 14
- TypeScript
- Tailwind CSS
- Shadcn UI
- Lucide Icons

## Development

- Format kode:

```bash
bun format  # atau npm run format
```

- Lint:

```bash
bun lint  # atau npm run lint
```

## Environment Variables

Tidak ada environment variables yang diperlukan di frontend karena semua konfigurasi API dihandle di backend.
