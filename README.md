# 🎵 Aplikasi Rekomendasi Lagu Berdasarkan Curhat dan Mood

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
    ├── utils.py                 # Algoritma pencocokan curhat dan lagu
    ├── api_service.py            # Integrasi dengan API eksternal
    │
    ├── migrations/               # Riwayat perubahan struktur database
    │   ├── 0001_initial.py
    │   ├── 0002_lagu_audio_preview_url.py
    │   ├── 0003_...
    │   └── __init__.py
    │
    ├── management/               # Custom Django management commands
    │   └── commands/
    │       ├── seed_data.py      # Mengisi database dengan data awal
    │       └── auto_sync_api.py  # Sinkronisasi data melalui API
    │
    ├── templates/
    │   └── rekomendasi/          # TEMPLATE HTML APLIKASI
    │       ├── base.html         # Template dasar (Navbar dan Footer)
    │       ├── home.html         # Halaman utama dan form curhat
    │       ├── hasil.html        # Hasil rekomendasi lagu
    │       ├── detail.html       # Detail lagu, lirik, dan informasi terkait
    │       ├── daftar_lagu.html  # Katalog seluruh lagu
    │       ├── cari_api.html     # Pencarian lagu melalui API eksternal
    │       ├── preview_import.html # Preview sebelum menyimpan lagu
    │       ├── favorit.html      # Daftar lagu favorit pengguna
    │       └── mood_history.html # Riwayat mood pengguna
    │
    └── static/
        └── rekomendasi/
            └── css/
                └── style.css    # Styling dan desain antarmuka
```

**Catatan:** `db.sqlite3` tidak disimpan di repository GitHub karena merupakan database lokal. File tersebut akan dibuat secara otomatis ketika database diinisialisasi melalui Django migrations.

---

## ⚙️ Penjelasan Fungsi Setiap Bagian

### 1. Konfigurasi Project (`laguhati/`)

Direktori ini berisi konfigurasi inti Django yang mengatur bagaimana keseluruhan project berjalan.

| File | Fungsi |
|---|---|
| `settings.py` | Mengatur database, aplikasi yang digunakan, middleware, template, bahasa, dan konfigurasi lainnya. |
| `urls.py` | Mengatur routing utama dan menghubungkan URL dengan aplikasi `rekomendasi`. |
| `wsgi.py` | Menjadi titik masuk aplikasi untuk server deployment berbasis WSGI. |
| `asgi.py` | Menjadi titik masuk aplikasi untuk server deployment berbasis ASGI. |

### 2. Aplikasi Utama (`rekomendasi/`)

Direktori ini merupakan pusat seluruh fitur aplikasi LaguHati.

**`models.py` — Struktur Database**

Mendefinisikan model atau tabel yang digunakan untuk menyimpan data aplikasi, seperti:

- `Mood`: Menyimpan informasi kategori suasana hati.
- `Lagu`: Menyimpan informasi lagu, seperti judul, artis, lirik, dan atribut lagu lainnya.
- `KutipanLirik`: Menyimpan kutipan lirik yang dapat ditampilkan sebagai bagian dari hasil rekomendasi.

**`views.py` — Pengatur Alur Aplikasi**

Bertanggung jawab menerima request dari pengguna, menjalankan logika aplikasi, berinteraksi dengan database, dan mengirimkan response berupa halaman HTML.

Beberapa proses yang ditangani antara lain:

- Menampilkan halaman utama.
- Memproses cerita dan pilihan mood pengguna.
- Menampilkan hasil rekomendasi lagu.
- Menampilkan detail lagu.
- Menangani pencarian dan proses import lagu dari API.

**`forms.py` — Input Pengguna**

Mengatur form yang digunakan untuk menerima masukan pengguna, seperti cerita atau curhat dan pilihan mood.

**`utils.py` — Algoritma Rekomendasi**

Merupakan bagian yang menangani logika pencocokan antara cerita pengguna dengan lagu yang tersedia.

Secara umum, prosesnya adalah:

1. Menerima teks cerita atau curhat dari pengguna.
2. Memproses teks untuk menemukan kata atau informasi yang relevan.
3. Melakukan pencocokan dengan informasi mood dan atribut lagu.
4. Menghasilkan kandidat lagu yang paling sesuai.
5. Mengembalikan hasil pencocokan untuk ditampilkan kepada pengguna.

Dengan demikian, rekomendasi tidak hanya bergantung pada pilihan mood, tetapi juga mempertimbangkan isi cerita pengguna.

**`api_service.py` — Integrasi API Eksternal**

Berfungsi sebagai penghubung antara aplikasi LaguHati dengan layanan penyedia data lagu dari luar.

Integrasi yang digunakan dalam project ini meliputi:

- **Deezer API:** Membantu mendapatkan informasi katalog lagu.
- **iTunes API:** Membantu pencarian informasi lagu dan preview audio.
- **LRCLIB:** Membantu mendapatkan data lirik lagu.

Modul ini memisahkan proses komunikasi dengan API dari logika utama aplikasi sehingga kode lebih terorganisasi dan mudah dikembangkan.

**`admin.py` — Django Administration**

Mendaftarkan model database agar data aplikasi dapat dikelola melalui halaman Django Admin.

**`migrations/` — Pengelolaan Database**

Menyimpan riwayat perubahan struktur database. Django menggunakan migration untuk membuat atau memperbarui tabel berdasarkan perubahan pada `models.py`.

**`management/commands/` — Perintah Otomatis**

Menyimpan custom management command yang dapat dijalankan melalui terminal Django.

- `seed_data.py`: Digunakan untuk memasukkan data awal ke database.
- `auto_sync_api.py`: Menyediakan perintah untuk melakukan sinkronisasi data melalui API.

### 3. Tampilan Aplikasi (`templates/`)

Bagian ini berisi file HTML yang menentukan tampilan setiap halaman aplikasi.

| Template | Kegunaan |
|---|---|
| `base.html` | Kerangka utama halaman, termasuk navbar dan footer. |
| `home.html` | Halaman utama untuk memasukkan cerita dan memilih mood. |
| `hasil.html` | Menampilkan lagu-lagu hasil rekomendasi. |
| `detail.html` | Menampilkan informasi detail lagu dan lirik. |
| `daftar_lagu.html` | Menampilkan katalog lagu yang tersedia di database. |
| `cari_api.html` | Menyediakan fitur pencarian lagu melalui API. |
| `preview_import.html` | Menampilkan preview data lagu sebelum diimpor ke database. |
| `favorit.html` | Menampilkan daftar lagu yang ditandai sebagai favorit. |
| `mood_history.html` | Menampilkan riwayat mood pengguna. |

### 4. Tampilan dan Desain (`static/`)

**`static/rekomendasi/css/style.css`**

Berisi kode CSS yang mengatur tampilan visual aplikasi, seperti:

- Dark mode.
- Layout dan tata letak halaman.
- Desain kartu lagu.
- Tipografi dan warna.
- Animasi serta efek interaksi antarmuka.

### 5. File Utama Project

| File | Fungsi |
|---|---|
| `manage.py` | Entry point untuk menjalankan perintah administratif Django. |
| `requirements.txt` | Daftar library Python yang diperlukan untuk menjalankan project. |
| `.gitignore` | Menentukan file dan folder yang tidak perlu dimasukkan ke Git. |
| `README.md` | Dokumentasi project dan panduan penggunaan. |

---

## 🔄 Alur Kerja Aplikasi

Berikut gambaran sederhana bagaimana aplikasi LaguHati bekerja ketika pengguna ingin mendapatkan rekomendasi lagu.

```text
              PENGGUNA
                  |
                  v
          Membuka Halaman Home
                  |
                  v
       Mengisi Cerita / Curhat
                  |
                  v
          Memilih Kategori Mood
                  |
                  v
          Form Mengirim Data
                  |
                  v
             views.py
                  |
                  v
             utils.py
        (Proses Pencocokan)
                  |
                  v
       Mengakses Data Lagu
           dari Database
                  |
                  v
       Menghasilkan Rekomendasi
                  |
                  v
             hasil.html
                  |
                  v
       Hasil Ditampilkan kepada
              Pengguna
```

Selain melalui database lokal, aplikasi juga menyediakan proses pencarian dan pengambilan data lagu dari API eksternal.

Alur sederhananya:

```text
       Pengguna Membuka Fitur Cari Lagu
                     |
                     v
               cari_api.html
                     |
                     v
                 views.py
                     |
                     v
              api_service.py
                     |
            +--------+--------+
            |        |        |
            v        v        v
          Deezer  iTunes   LRCLIB
            |        |        |
            +--------+--------+
                     |
                     v
             Data Lagu Diterima
                     |
                     v
             preview_import.html
                     |
                     v
         Pengguna Melakukan Konfirmasi
                     |
                     v
               Database
```

---

## 💻 Cara Menjalankan Project

Ikuti langkah-langkah berikut untuk menjalankan aplikasi LaguHati di komputer masing-masing.

### 1. Clone Repository

```bash
git clone https://github.com/dawsonandarson-boop/Tugas-Kelompok-DDP-1.git
```

Masuk ke direktori project:

```bash
cd Tugas-Kelompok-DDP-1
```

### 2. Membuat Virtual Environment

Disarankan menggunakan virtual environment agar dependency project tidak bercampur dengan instalasi Python lainnya.

```bash
python -m venv venv
```

Aktifkan virtual environment.

**Windows PowerShell:**

```powershell
.\venv\Scripts\Activate.ps1
```

**Linux/macOS:**

```bash
source venv/bin/activate
```

### 3. Menginstal Dependencies

Pastikan virtual environment sudah aktif, kemudian jalankan:

```bash
python -m pip install -r requirements.txt
```

Perintah tersebut akan menginstal library yang dibutuhkan oleh project.

### 4. Menyiapkan Database

Jalankan perintah migration:

```bash
python manage.py migrate
```

Perintah ini membuat atau memperbarui tabel database berdasarkan file migrations yang tersedia.

Untuk memasukkan data awal ke database, jalankan:

```bash
python manage.py seed_data
```

### 5. (Opsional) Mengaktifkan Gemini API

Fitur pencarian judul/artis dan pilihan mood dapat digunakan tanpa Gemini. Untuk memakai prompt bebas dan pesan motivasi dari Gemini, atur API key di environment sebelum menjalankan server. Ganti nilai contoh di bawah dengan key milikmu; jangan commit atau membagikan key tersebut.

**Windows PowerShell:**

```powershell
$env:GEMINI_API_KEY = "isi-kunci-dari-Google-AI-Studio"
$env:GEMINI_MODEL = "gemini-3.8-flash"
```

**Linux/macOS:**

```bash
export GEMINI_API_KEY="isi-kunci-dari-Google-AI-Studio"
export GEMINI_MODEL="gemini-3.8-flash"
```

Variabel ini berlaku untuk terminal yang sedang digunakan. Jalankan server dari terminal yang sama.

### 6. Menjalankan Server Django

```bash
python manage.py runserver
```

Buka browser dan kunjungi:

```text
http://127.0.0.1:8000/
```

Aplikasi LaguHati sekarang dapat diakses melalui browser lokal. Biarkan terminal tetap terbuka selama menggunakan web; tekan `Ctrl+C` untuk menghentikan server.

---

## 👥 Kolaborasi Pengembangan

Project ini menggunakan Git dan GitHub untuk mempermudah kolaborasi antaranggota kelompok.

Beberapa perintah Git yang sering digunakan:

**Mengambil perubahan terbaru dari GitHub:**

```bash
git pull
```

**Memeriksa perubahan file:**

```bash
git status
```

**Menambahkan perubahan:**

```bash
git add .
```

**Membuat commit:**

```bash
git commit -m "Menambahkan fitur baru"
```

**Mengirim perubahan ke GitHub:**

```bash
git push
```

Disarankan setiap anggota melakukan `git pull` sebelum mulai mengerjakan project agar kode yang digunakan tetap mengikuti perkembangan terbaru.

Untuk pengembangan bersama, gunakan branch terpisah untuk fitur baru dan lakukan Pull Request sebelum menggabungkan perubahan ke branch `main`.

---

## 🛠️ Teknologi yang Digunakan

| Teknologi | Kegunaan |
|---|---|
| Python | Bahasa pemrograman utama. |
| Django | Framework backend untuk membangun aplikasi web. |
| SQLite | Database lokal untuk menyimpan data aplikasi. |
| HTML | Menyusun struktur halaman web. |
| CSS | Mengatur tampilan dan desain antarmuka. |
| Deezer API | Mengambil informasi katalog lagu. |
| iTunes API | Mengambil informasi dan preview lagu. |
| LRCLIB | Mengambil kutipan singkat dan tautan sumber lirik. |
| Gemini API | Menyederhanakan prompt dan menulis pesan motivasi per lagu. |
| Git & GitHub | Version control dan kolaborasi pengembangan. |

### Menyiapkan prompt Gemini

Prompt bebas memakai Gemini untuk menyederhanakan permintaan menjadi kata kunci Deezer. Saat lagu dipilih, Gemini juga memberi tipe lagu dan pesan motivasi orisinal. Hasil motivasi disimpan sekali per ID lagu agar pemilihan berikutnya tidak memanggil Gemini lagi. Atur kunci di environment sebelum menjalankan Django; jangan masukkan kunci API ke GitHub.

PowerShell:

```powershell
$env:GEMINI_API_KEY = "isi-kunci-dari-Google-AI-Studio"
$env:GEMINI_MODEL = "gemini-3.8-flash"
python manage.py runserver
```

Tanpa `GEMINI_API_KEY`, prompt memakai pencocokan kata lokal dan panel lagu menampilkan pesan sesuai mood. Pencarian judul/artis dan pilihan mood mengambil hasil langsung dari Deezer; Gemini hanya dipakai untuk prompt bebas dan pesan lagu setelah lagu dipilih.

---

## 🎯 Tujuan Pengembangan

Melalui LaguHati, kami ingin mengembangkan aplikasi yang dapat menghubungkan suasana hati dan cerita seseorang dengan musik yang relevan.

Project ini juga menjadi sarana untuk menerapkan konsep pemrograman Python, pengembangan aplikasi web menggunakan Django, pengelolaan database, integrasi API, serta kolaborasi menggunakan Git dan GitHub.

**LaguHati — Because Every Feeling Has Its Own Song.** 🎶
