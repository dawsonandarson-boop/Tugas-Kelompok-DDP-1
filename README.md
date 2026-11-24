# 🎵 Aplikasi Rekomendasi Lagu Berdasarkan Curhat dan Mood

Moodify adalah aplikasi web untuk mencari lagu berdasarkan judul/artis, prompt, atau mood. Aplikasi ini dibuat dengan Python dan Django.

Dengan memanfaatkan algoritma pencocokan teks dan integrasi API eksternal, Moodify berusaha menemukan lagu yang sesuai dengan kondisi emosional pengguna. Selain rekomendasi lagu, aplikasi ini juga menyediakan fitur pencarian lagu, katalog lagu, favorit, riwayat mood, serta informasi detail lagu dan lirik.

## 🧭 Cara Kerja Moodify

Pengguna menyampaikan apa yang ingin didengar, aplikasi mencari lagu, lalu mengirimkan hasilnya kembali ke halaman web.

Ada dua cara utama menemukan lagu:

1. **Jalur utama: cari lagu, tulis prompt, atau pilih mood di beranda.** Aplikasi meminta daftar lagu ke Deezer. Jika Deezer tidak memberi hasil, aplikasi mencoba iTunes. Untuk prompt bebas, Gemini (jika API key disediakan) mengubah cerita menjadi kata pencarian. Tanpa Gemini, aplikasi memakai kata-kata dari prompt. Hasil pencarian langsung ditampilkan dan tidak otomatis dimasukkan ke katalog database Moodify.
2. **Jalur rekomendasi katalog lokal:** jika curhat dikirim ke alamat `/hasil/`, aplikasi membaca kata-kata untuk memperkirakan mood, energi, dan aktivitas. Lalu aplikasi membandingkannya dengan data lagu di database, memberi skor kecocokan, dan menampilkan lagu dengan skor tertinggi. Form untuk mengirim curhat lagi tersedia di halaman hasil.

Setelah lagu dipilih di beranda, browser meminta kutipan pendek ke LRCLIB dan pesan motivasi ke aplikasi. Aplikasi meminta Gemini membuat pesan jika tersedia; kalau Gemini tidak aktif, aplikasi menampilkan pesan bawaan. Lagu favorit dan riwayat mood disimpan di database lokal dan dikaitkan dengan sesi browser pengguna.

**Istilah singkat:** halaman web adalah bagian yang dilihat pengguna; database adalah penyimpanan milik aplikasi; API adalah layanan luar yang dimintai data. Hasil dari API pencarian lagu hanya ditampilkan, sedangkan favorit, riwayat, dan katalog lagu lokal disimpan di database.

Alur request web secara umum:

```text
Pengguna mengisi halaman
        ↓
Alamat halaman memilih fungsi yang tepat
        ↓
Fungsi memproses input dan meminta data ke logika, database, atau API
        ↓
Halaman menerima hasil dan menampilkannya
```

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
├── Moodify/                      # KONFIGURASI UTAMA PROJECT DJANGO
│   ├── __init__.py
│   ├── settings.py               # Pengaturan utama project Django
│   ├── urls.py                   # Routing URL utama aplikasi
│   ├── asgi.py                   # Konfigurasi server ASGI
│   └── wsgi.py                   # Konfigurasi server WSGI
│
└── rekomendasi/                  # APLIKASI UTAMA MOODIFY
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
    │       └── seed_data.py      # Mengisi database dengan data awal
    │
    ├── templates/
    │   └── rekomendasi/          # TEMPLATE HTML APLIKASI
    │       ├── base.html         # Template dasar (Navbar dan Footer)
    │       ├── home.html         # Halaman utama dan form curhat
    │       ├── hasil.html        # Hasil rekomendasi lagu
    │       ├── detail.html       # Detail lagu, lirik, dan informasi terkait
    │       ├── daftar_lagu.html  # Katalog seluruh lagu
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

### 1. Konfigurasi Project (`Moodify/`)

Direktori ini berisi konfigurasi inti Django yang mengatur bagaimana keseluruhan project berjalan.

| File | Fungsi |
|---|---|
| `settings.py` | Mengatur database, aplikasi yang digunakan, middleware, template, bahasa, dan konfigurasi lainnya. |
| `urls.py` | Mengatur routing utama dan menghubungkan URL dengan aplikasi `rekomendasi`. |
| `wsgi.py` | Menjadi titik masuk aplikasi untuk server deployment berbasis WSGI. |
| `asgi.py` | Menjadi titik masuk aplikasi untuk server deployment berbasis ASGI. |

### 2. Aplikasi Utama (`rekomendasi/`)

Direktori ini merupakan pusat seluruh fitur aplikasi Moodify.

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
- Menangani pencarian lagu langsung melalui API eksternal.

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

Berfungsi sebagai penghubung antara aplikasi Moodify dengan layanan penyedia data lagu dari luar.

Integrasi yang digunakan dalam project ini meliputi:

- **Deezer API:** Mencari lagu untuk hasil di beranda.
- **iTunes API:** Menjadi layanan pencarian cadangan jika Deezer tidak memberi hasil.
- **LRCLIB:** Mencari kutipan pendek lirik untuk lagu yang dipilih.
- **Gemini API:** Mengubah prompt menjadi kata pencarian dan membuat pesan motivasi, jika API key tersedia.

Modul ini memisahkan proses komunikasi dengan API dari logika utama aplikasi sehingga kode lebih terorganisasi dan mudah dikembangkan.

**`admin.py` — Django Administration**

Mendaftarkan model database agar data aplikasi dapat dikelola melalui halaman Django Admin.

**`migrations/` — Pengelolaan Database**

Menyimpan riwayat perubahan struktur database. Django menggunakan migration untuk membuat atau memperbarui tabel berdasarkan perubahan pada `models.py`.

**`management/commands/` — Perintah Otomatis**

Menyimpan custom management command yang dapat dijalankan melalui terminal Django.

- `seed_data.py`: Digunakan untuk memasukkan data awal ke database.

### Ringkasan File dengan Bahasa Sehari-hari

| File atau folder | Gampangnya, ini bagian untuk... |
|---|---|
| `manage.py` | Menyalakan server atau menjalankan perintah pengelolaan aplikasi. |
| `requirements.txt` | Mencatat paket Python yang perlu dipasang agar aplikasi bisa jalan. |
| `.gitignore` | Memberi tahu Git file lokal mana yang tidak perlu dibagikan, seperti database lokal dan virtual environment. |
| `Moodify/settings.py` | Mengatur hal dasar aplikasi: database, bahasa, aplikasi yang aktif, dan pengaturan Django lainnya. |
| `Moodify/urls.py` | Pintu masuk alamat web; meneruskan alamat Moodify ke aplikasi utama. |
| `Moodify/asgi.py` dan `Moodify/wsgi.py` | Penghubung aplikasi ke server saat aplikasi dijalankan atau dipasang di hosting. Biasanya tidak perlu diubah untuk tugas tampilan biasa. |
| `rekomendasi/urls.py` | Daftar alamat fitur, misalnya beranda, katalog, favorit, dan riwayat. |
| `rekomendasi/views.py` | Pengatur kerja: menerima permintaan halaman, mengambil atau mengolah data, lalu menentukan halaman/hasil yang dikirim. |
| `rekomendasi/forms.py` | Bentuk input yang dikirim pengguna, seperti kolom curhat dan pilihan mood. |
| `rekomendasi/utils.py` | Cara aplikasi menebak mood dari kata-kata dan menghitung kecocokan lagu di katalog lokal. |
| `rekomendasi/api_service.py` | Cara aplikasi berbicara dengan layanan luar seperti Deezer, iTunes, LRCLIB, dan Gemini. |
| `rekomendasi/models.py` | Jenis data yang disimpan, seperti lagu, mood, favorit, serta riwayat. Bisa dibayangkan sebagai rancangan lemari penyimpanan. |
| `rekomendasi/admin.py` | Mengatur data yang bisa dikelola lewat halaman admin Django. |
| `rekomendasi/apps.py` | Informasi pendaftaran aplikasi `rekomendasi` ke Django. |
| `rekomendasi/migrations/` | Catatan perubahan bentuk database, supaya database bisa dibuat atau diperbarui. |
| `rekomendasi/management/commands/seed_data.py` | Mengisi database dengan contoh data awal untuk dicoba. |
| `rekomendasi/templates/rekomendasi/base.html` | Kerangka yang dipakai bersama, seperti menu navigasi dan footer. |
| File HTML lain di `templates/rekomendasi/` | Isi masing-masing halaman yang dilihat pengguna, seperti beranda, hasil, detail, katalog, favorit, dan riwayat. |
| `rekomendasi/static/rekomendasi/css/style.css` | Mengatur warna, ukuran, jarak, tata letak, dan tampilan halaman di berbagai ukuran layar. |
| `README.md` | Panduan project, cara menjalankan aplikasi, dan penjelasan cara kerjanya. |

**Kalau ingin mengubah tampilan**, biasanya mulai dari file HTML halaman terkait dan `style.css`. **Kalau ingin mengubah cara halaman bekerja**, lihat `views.py`. **Kalau ingin mengubah cara lagu dicocokkan**, lihat `utils.py`. **Kalau ingin mengubah layanan musik/Gemini yang dihubungi**, lihat `api_service.py`.

### 3. Tampilan Aplikasi (`templates/`)

Bagian ini berisi file HTML yang menentukan tampilan setiap halaman aplikasi.

| Template | Kegunaan |
|---|---|
| `base.html` | Kerangka utama halaman, termasuk navbar dan footer. |
| `home.html` | Halaman utama untuk memasukkan cerita dan memilih mood. |
| `hasil.html` | Menampilkan lagu-lagu hasil rekomendasi. |
| `detail.html` | Menampilkan informasi detail lagu dan lirik. |
| `daftar_lagu.html` | Menampilkan katalog lagu yang tersedia di database. |
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

Berikut alur rekomendasi katalog lokal saat pengguna mengirim curhat dari form di halaman hasil.

```text
              PENGGUNA
                  |
                  v
       Mengirim Curhat Lagi
                  |
                  v
          views.py menerima
             curhat
                  |
                  v
        utils.py menebak mood
        dan memberi skor lagu
                  |
                  v
       Membaca katalog lokal
          di database
                  |
                  v
        hasil.html menampilkan
            rekomendasi
```

Pencarian lagu di halaman utama mengambil hasil dari API eksternal dan langsung menampilkannya. Hasil tersebut tidak otomatis disimpan ke katalog database lokal.

Alur sederhananya:

```text
       Pengguna Mencari Lagu di Beranda
                     |
                     v
               home.html
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
          Deezer  iTunes
            |        |        |
            +--------+--------+
                     |
                     v
             Data Lagu Diterima
                     |
                     v
          Hasil Tampil di Beranda
```

---

## 💻 Cara Menjalankan Project

Ikuti langkah-langkah berikut untuk menjalankan aplikasi Moodify di komputer masing-masing.

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
$geminiSecureInput = Read-Host "Tempel Gemini API key" -AsSecureString
$geminiKeyPointer = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($geminiSecureInput)
try {
    $env:GEMINI_API_KEY = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($geminiKeyPointer)
} finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($geminiKeyPointer)
}

$env:GEMINI_MODEL = "gemini-3.8-flash"
.\venv\Scripts\python.exe manage.py runserver
```

Buka browser dan kunjungi:

```text
http://127.0.0.1:8000/
```

Aplikasi Moodify sekarang dapat diakses melalui browser lokal. Biarkan terminal tetap terbuka selama menggunakan web; tekan `Ctrl+C` untuk menghentikan server.

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

Melalui Moodify, kami ingin mengembangkan aplikasi yang dapat menghubungkan suasana hati dan cerita seseorang dengan musik yang relevan.

Project ini juga menjadi sarana untuk menerapkan konsep pemrograman Python, pengembangan aplikasi web menggunakan Django, pengelolaan database, integrasi API, serta kolaborasi menggunakan Git dan GitHub.

**Moodify — Because Every Feeling Has Its Own Song.** 🎶
