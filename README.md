Tugas Kelompok DDP 1/
│
├── manage.py                          # Script utama untuk menjalankan perintah Django
├── db.sqlite3                         # File database lokal (SQLite)
├── requirements.txt                   # Daftar dependensi library Python
│
├── laguhati/                          # FOLDER KONFIGURASI PROYEK
│   ├── settings.py                    # Pengaturan utama (Database, App aktif, Bahasa, dll)
│   ├── urls.py                        # Pintu gerbang utama routing URL web
│   └── wsgi.py / asgi.py              # Konfigurasi deployment server
│
└── rekomendasi/                       # APLIKASI UTAMA (Fitur Rekomendasi Lagu)
    │
    ├── models.py                      # Definisi tabel DB (Mood, Lagu, KutipanLirik)
    ├── views.py                       # Pengatur alur halaman (Home, Hasil, Detail, Import API)
    ├── urls.py                        # Daftar alamat URL untuk fitur rekomendasi
    ├── forms.py                       # Form input curhat dan mood
    │
    ├── utils.py                       # 🧠 Otak algoritma pencocokan curhat & lagu
    ├── api_service.py                 # 🌐 Modul penghubung ke API Luar (Deezer, iTunes, LRCLIB)
    ├── admin.py                       # Pendaftaran tabel ke halaman Django Admin
    │
    ├── management/commands/
    │   └── seed_data.py               # Script untuk mengisi database otomatis di awal
    │
    ├── templates/rekomendasi/         # BERKAS TAMPILAN HTML
    │   ├── base.html                  # Kerangka utama website (Navbar & Footer)
    │   ├── home.html                  # Halaman utama (Form curhat & pilihan mood)
    │   ├── hasil.html                 # Halaman hasil rekomendasi lagu & kutipan
    │   ├── detail.html                # Halaman detail lirik, video YouTube & lagu serupa
    │   ├── daftar_lagu.html           # Halaman katalog seluruh lagu yang tersimpan
    │   ├── cari_api.html              # Halaman pencarian lagu ke API global
    │   └── preview_import.html        # Halaman preview & konfirmasi simpan lagu dari API
    │
    └── static/rekomendasi/css/
        └── style.css                  # Desain tampilan UI (Dark-mode modern, kartu, animasi)