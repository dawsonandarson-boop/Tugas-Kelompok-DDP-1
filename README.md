# 🎵 LaguHati — Aplikasi Rekomendasi Lagu Berdasarkan Curhat dan Mood

LaguHati adalah aplikasi berbasis web yang dikembangkan menggunakan **Python dan Django**. Aplikasi ini memungkinkan pengguna mendapatkan rekomendasi lagu berdasarkan cerita, perasaan, atau suasana hati (*mood*) yang sedang mereka alami.

Dengan memanfaatkan algoritma pencocokan teks dan integrasi API eksternal, LaguHati berusaha menemukan lagu yang sesuai dengan kondisi emosional pengguna. Selain rekomendasi lagu, aplikasi ini juga menyediakan fitur pencarian lagu, katalog lagu, favorit, riwayat mood, serta informasi detail lagu dan lirik.

---

## 📁 Struktur Folder Project

Berikut merupakan struktur utama project beserta penjelasan fungsi dari setiap direktori dan file:

```text
Tugas Kelompok DDP 1/
│
├── manage.py
├── requirements.txt
├── .gitignore
├── README.md
│
├── laguhati/                     # KONFIGURASI UTAMA PROJECT DJANGO
│   ├── __init__.py
│   ├── settings.py               # Pengaturan utama project Django
│   ├── urls.py                   # Routing URL utama aplikasi
│   ├── asgi.py                   # Konfigurasi server ASGI
│   └── wsgi.py                   # Konfigurasi server WSGI
│
└── rekomendasi/                  # APLIKASI UTAMA LAGUHATI
    │
    ├── __init__.py
    ├── admin.py                 # Registrasi model ke Django Admin
    ├── apps.py                  # Konfigurasi aplikasi Django
    ├── models.py                # Struktur tabel database
    ├── views.py                 # Logika pemrosesan request dan response
    ├── urls.py                  # Routing URL aplikasi rekomendasi
    ├── forms.py                 # Form input pengguna
    │
    ├── utils.py                 # Algoritma pencocokan curhat dan