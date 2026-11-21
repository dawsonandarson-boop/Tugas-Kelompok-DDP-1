"""
Management command untuk mengisi database Moodify dengan:
- 8 Kategori Mood Resmi Moodify
- Dataset Lagu Multi-Parameter (Mood, Genre, Energy, Bahasa, Kutipan, Video YouTube)
Jalankan: python manage.py seed_data
"""

from django.core.management.base import BaseCommand
from rekomendasi.models import Mood, Lagu, KutipanLirik


class Command(BaseCommand):
    help = 'Mengisi database dengan 8 Mood resmi Moodify dan dataset lagu multi-parameter'

    def handle(self, *args, **options):
        self.stdout.write('🎵 Memulai pengisian data Moodify...\n')

        # === 8 KATEGORI MOOD RESMI MOODIFY ===
        moods_data = [
            {
                'nama': 'Happy',
                'slug': 'happy',
                'emoji': '😊',
                'deskripsi': 'Saat merasa senang, bersemangat, dan ingin menikmati suasana.',
                'contoh_genre': 'upbeat pop, dance, funk',
                'warna': '#eab308',
                'kata_kunci': 'senang,bahagia,gembira,ceria,riang,sukacita,happy,tersenyum,tertawa,asik,fun,seru,menikmati,pesta,joget',
            },
            {
                'nama': 'Sad',
                'slug': 'sad',
                'emoji': '🌧️',
                'deskripsi': 'Saat sedang sedih, kecewa, atau ingin mendengarkan lagu yang emosional.',
                'contoh_genre': 'ballad, acoustic, mellow pop',
                'warna': '#3b82f6',
                'kata_kunci': 'sedih,kecewa,galau,menangis,nangis,patah hati,luka,hancur,terluka,sakit hati,hampa,kosong,kesepian,sendiri,sepi,ga setara,minder,insecure,tidak setara,ditinggal,pilu',
            },
            {
                'nama': 'Romantic',
                'slug': 'romantic',
                'emoji': '❤️',
                'deskripsi': 'Saat ingin menikmati suasana romantis atau lagu bertema cinta.',
                'contoh_genre': 'R&B, love songs, soft pop',
                'warna': '#ec4899',
                'kata_kunci': 'romantis,cinta,sayang,jatuh cinta,kasmaran,naksir,pacar,kekasih,manis,peluk,dekap,berdua,soulmate,pujaan hati',
            },
            {
                'nama': 'Relaxed',
                'slug': 'relaxed',
                'emoji': '🌿',
                'deskripsi': 'Saat ingin bersantai dan menikmati suasana tenang.',
                'contoh_genre': 'lo-fi, ambient, chill acoustic',
                'warna': '#10b981',
                'kata_kunci': 'santai,tenang,rileks,relax,chill,rebahan,istirahat,capek,lelah,penat,melepas lelah,sore,adem,sejuk,damai,healing,ngopi',
            },
            {
                'nama': 'Focus',
                'slug': 'focus',
                'emoji': '🎧',
                'deskripsi': 'Saat belajar, membaca, atau mengerjakan sesuatu yang membutuhkan konsentrasi.',
                'contoh_genre': 'instrumental, classical, lo-fi',
                'warna': '#8b5cf6',
                'kata_kunci': 'belajar,fokus,konsentrasi,tugas,kuliah,kerja,nugas,skripsi,membaca,coding,ujian,mengerjakan,deadline,proyek,produktif',
            },
            {
                'nama': 'Energetic',
                'slug': 'energetic',
                'emoji': '⚡',
                'deskripsi': 'Saat ingin meningkatkan semangat dan energi.',
                'contoh_genre': 'rock, EDM, upbeat hip-hop',
                'warna': '#f97316',
                'kata_kunci': 'semangat,energi,bersemangat,workout,olahraga,gym,lari,membara,gas,bangkit,kuat,bertenaga,pesta,joget,dance',
            },
            {
                'nama': 'Nostalgic',
                'slug': 'nostalgic',
                'emoji': '📷',
                'deskripsi': 'Saat ingin mengenang masa lalu atau menikmati lagu yang membawa kenangan.',
                'contoh_genre': 'oldies, retro pop, classic hits',
                'warna': '#d97706',
                'kata_kunci': 'nostalgia,kenangan,masa lalu,teringat,memori,dulu,masa sma,masa kecil,waktu dulu,kangen dulu,jadul,klasik,rindu masa',
            },
            {
                'nama': 'Angry / Frustrated',
                'slug': 'angry',
                'emoji': '🔥',
                'deskripsi': 'Saat sedang kesal, frustrasi, atau ingin menyalurkan emosi melalui musik.',
                'contoh_genre': 'rock, metal, intense hip-hop',
                'warna': '#ef4444',
                'kata_kunci': 'marah,kesal,frustrasi,benci,emosi,muak,jengkel,dendam,berontak,amarah,muak dengan semua,capek dibohongi,geram,panas',
            },
        ]

        mood_objects = {}
        for m_data in moods_data:
            mood, created = Mood.objects.update_or_create(
                nama=m_data['nama'],
                defaults=m_data
            )
            mood_objects[m_data['nama']] = mood
            status = '✅ Dibuat' if created else '🔄 Diperbarui'
            self.stdout.write(f"  {status}: {mood}")

        # === DATASET LAGU MULTI-PARAMETER MOODIFY ===
        lagu_data = [
            # 1. SAD / GALAU / GA SETARA
            {
                'judul': 'Aku Bukan Untukmu',
                'artis': 'Rossa',
                'album': 'Kembali',
                'tahun': 2005,
                'genre': 'Pop Ballad',
                'energy': 'low',
                'bahasa': 'Indonesia',
                'alunan': 'mellow',
                'youtube_id': 'OK-DNdo5VWE',
                'lirik': (
                    "Mungkin memang benar aku bukan untukmu\n"
                    "Mungkin memang benar kita tak ditakdirkan bersama\n"
                    "Aku terlalu biasa untuk dirimu\n"
                    "Kau terlalu sempurna untuk diriku\n\n"
                    "Aku sadar aku bukan untukmu\n"
                    "Betapapun aku mencintaimu\n"
                    "Aku harus pergi meninggalkanmu\n"
                    "Karena aku tahu aku bukan untukmu"
                ),
                'moods': ['Sad'],
                'kutipan': [
                    {
                        'teks': 'Aku terlalu biasa untuk dirimu, kau terlalu sempurna untuk diriku',
                        'penjelasan': 'Merasa minder dan tidak sebanding dengan orang yang kita suka',
                    },
                ],
            },
            {
                'judul': 'Bukan Cinta Biasa',
                'artis': 'Afgan',
                'album': 'Confession No. 1',
                'tahun': 2008,
                'genre': 'Pop R&B',
                'energy': 'low',
                'bahasa': 'Indonesia',
                'alunan': 'mellow',
                'youtube_id': 'nshdkoeu_fY',
                'lirik': (
                    "Ini bukan cinta biasa, rasa ini begitu dalam\n"
                    "Namun aku hanya bisa menatap dari jauh aku mengagumi\n"
                    "Karena aku tahu kau terlalu indah untuk seseorang sepertiku"
                ),
                'moods': ['Sad', 'Romantic'],
                'kutipan': [
                    {
                        'teks': 'Karena aku tahu kau terlalu indah untuk seseorang sepertiku',
                        'penjelasan': 'Mengagumi dari kejauhan karena merasa tidak layak mendekati',
                    },
                ],
            },
            {
                'judul': 'Separuh Aku',
                'artis': 'NOAH',
                'album': 'Seperti Seharusnya',
                'tahun': 2012,
                'genre': 'Pop Rock',
                'energy': 'medium',
                'bahasa': 'Indonesia',
                'alunan': 'ballad',
                'youtube_id': 'b0ZBBjViV8Y',
                'lirik': (
                    "Dan terjadi lagi kisah lama yang terulang kembali\n"
                    "Kau membuat aku merasa tak bisa apa-apa\n"
                    "Separuh aku dirimu, separuh aku hidupmu"
                ),
                'moods': ['Sad', 'Nostalgic'],
                'kutipan': [
                    {
                        'teks': 'Kau membuat aku merasa tak bisa apa-apa',
                        'penjelasan': 'Rasa putus asa dan tidak berdaya karena seseorang',
                    },
                ],
            },
            {
                'judul': 'Butiran Debu',
                'artis': 'Rumor',
                'album': 'Single',
                'tahun': 2011,
                'genre': 'Pop Ballad',
                'energy': 'low',
                'bahasa': 'Indonesia',
                'alunan': 'acoustic',
                'youtube_id': 'l0QDenxw9Iw',
                'lirik': (
                    "Aku bagaikan butiran debu yang tertiup angin tak tentu arah\n"
                    "Jatuh di tanah tak ada yang peduli"
                ),
                'moods': ['Sad'],
                'kutipan': [
                    {
                        'teks': 'Aku bagaikan butiran debu, yang tertiup angin tak tentu arah',
                        'penjelasan': 'Perasaan sangat kecil dan diabaikan',
                    },
                ],
            },

            # 2. RELAXED / CHILL / HEALING
            {
                'judul': 'Berdua Saja',
                'artis': 'Payung Teduh',
                'album': 'Dunia Batas',
                'tahun': 2012,
                'genre': 'chill acoustic',
                'energy': 'low',
                'bahasa': 'Indonesia',
                'alunan': 'santai',
                'youtube_id': 'Tct7qR2bhHA',
                'lirik': (
                    "Ada yang tak sempat tergambarkan oleh kata\n"
                    "Ketika kita berdua menatap senja\n"
                    "Tenanglah hatiku, damailah jiwaku\n"
                    "Berdua saja di bawah teduhnya payung ini"
                ),
                'moods': ['Relaxed', 'Romantic'],
                'kutipan': [
                    {
                        'teks': 'Tenanglah hatiku, damailah jiwaku, berdua saja di bawah teduh',
                        'penjelasan': 'Momen damai melepas lelah bersama suasana tenang',
                    },
                ],
            },
            {
                'judul': 'Ruang Rindu',
                'artis': 'Letto',
                'album': 'Truth, Cry & Lie',
                'tahun': 2005,
                'genre': 'ambient pop',
                'energy': 'low',
                'bahasa': 'Indonesia',
                'alunan': 'tenang',
                'youtube_id': '9JS47BC0WXc',
                'lirik': (
                    "Di daun yang ikut mengalir lembut terbawa sungai ke ujung mata\n"
                    "Dan aku mulai takut terbawa cinta\n"
                    "Menghirup rindu yang kau tebarkan"
                ),
                'moods': ['Relaxed', 'Nostalgic'],
                'kutipan': [
                    {
                        'teks': 'Di daun yang ikut mengalir lembut terbawa sungai ke ujung mata',
                        'penjelasan': 'Suasana tenang dan damai menenangkan pikiran',
                    },
                ],
            },

            # 3. FOCUS / STUDYING / INSTRUMENTAL VIBES
            {
                'judul': 'Sitar Sonata (Lo-Fi Study)',
                'artis': 'Moodify Sanctuary',
                'album': 'Deep Focus Vol. 1',
                'tahun': 2024,
                'genre': 'lo-fi',
                'energy': 'low',
                'bahasa': 'Instrumental',
                'alunan': 'instrumental',
                'youtube_id': 'fQ3H3U6MzSE',
                'lirik': (
                    "[Instrumental Lo-Fi Beats for Study and Focus]\n"
                    "Alunan ketukan lembut dan melodi santai untuk menemani membaca dan mengerjakan tugas."
                ),
                'moods': ['Focus', 'Relaxed'],
                'kutipan': [
                    {
                        'teks': 'Focus your mind, let the ambient melodies guide your study flow.',
                        'penjelasan': 'Alunan tanpa lirik pengganggu untuk konsentrasi belajar maksimal',
                    },
                ],
            },

            # 4. HAPPY / CHEERFUL
            {
                'judul': 'Pernah Muda',
                'artis': 'Bunga Citra Lestari',
                'album': 'Tentang Kamu',
                'tahun': 2008,
                'genre': 'upbeat pop',
                'energy': 'high',
                'bahasa': 'Indonesia',
                'alunan': 'ceria',
                'youtube_id': 'eb3m13rH-K8',
                'lirik': (
                    "Bilang papa mama kita masih muda\n"
                    "Jangan kau batasi langkah kaki kita\n"
                    "Hidup ini indah nikmatilah saja\n"
                    "Tertawa gembira bersama kawan-kawan"
                ),
                'moods': ['Happy', 'Energetic'],
                'kutipan': [
                    {
                        'teks': 'Hidup ini indah nikmatilah saja, tertawa gembira bersama',
                        'penjelasan': 'Semangat menikmati hidup dengan ceria dan penuh tawa',
                    },
                ],
            },

            # 5. ENERGETIC / WORKOUT / BANGKIT
            {
                'judul': 'Jangan Menyerah',
                'artis': "D'Masiv",
                'album': 'Perjalanan',
                'tahun': 2009,
                'genre': 'rock',
                'energy': 'high',
                'bahasa': 'Indonesia',
                'alunan': 'upbeat',
                'youtube_id': 'mTp-OxfkCao',
                'lirik': (
                    "Tak ada manusia yang terlahir sempurna\n"
                    "Jangan kau sesali segala yang telah terjadi\n"
                    "Jangan menyerah, jangan menyerah!\n"
                    "Syukuri apa yang ada, hidup adalah anugerah"
                ),
                'moods': ['Energetic', 'Happy'],
                'kutipan': [
                    {
                        'teks': 'Jangan menyerah, syukuri apa yang ada, hidup adalah anugerah',
                        'penjelasan': 'Suntikan energi positif untuk bangkit dan tetap berjuang',
                    },
                ],
            },
            {
                'judul': 'Laskar Pelangi',
                'artis': 'Nidji',
                'album': 'Ost Laskar Pelangi',
                'tahun': 2008,
                'genre': 'upbeat pop',
                'energy': 'high',
                'bahasa': 'Indonesia',
                'alunan': 'semangat',
                'youtube_id': 'fO1iJqBdXrc',
                'lirik': (
                    "Mimpi adalah kunci untuk kita menaklukkan dunia\n"
                    "Berlarilah tanpa lelah sampai engkau meraihnya\n"
                    "Laskar pelangi takkan terikat waktu"
                ),
                'moods': ['Energetic', 'Nostalgic'],
                'kutipan': [
                    {
                        'teks': 'Mimpi adalah kunci untuk kita menaklukkan dunia, berlarilah tanpa lelah',
                        'penjelasan': 'Membangkitkan daya juang dan semangat yang membara',
                    },
                ],
            },

            # 6. ROMANTIC / LOVE
            {
                'judul': 'Cinta Sejati',
                'artis': 'Bunga Citra Lestari',
                'album': 'Ost Habibie Ainun',
                'tahun': 2012,
                'genre': 'love songs',
                'energy': 'medium',
                'bahasa': 'Indonesia',
                'alunan': 'ballad',
                'youtube_id': 'Bgt9g1q-xj0',
                'lirik': (
                    "Saat aku tak lagi di sisimu, ku tunggu kau di keabadian\n"
                    "Cinta kita melukiskan sejarah, menggelarkan cerita penuh pesona\n"
                    "Membagi kebahagiaan dan cinta"
                ),
                'moods': ['Romantic'],
                'kutipan': [
                    {
                        'teks': 'Cinta kita melukiskan sejarah, menggelarkan cerita penuh pesona',
                        'penjelasan': 'Ungkapan cinta sejati yang mendalam dan abadi',
                    },
                ],
            },
            {
                'judul': 'Menunggu Kamu',
                'artis': 'Anji',
                'album': 'Single',
                'tahun': 2018,
                'genre': 'soft pop',
                'energy': 'medium',
                'bahasa': 'Indonesia',
                'alunan': 'mellow',
                'youtube_id': 'NpKD379eRy8',
                'lirik': (
                    "Ku selalu mencoba untuk menguatkan hati dari kamu yang belum juga mengerti\n"
                    "Biar aku yang mengalah dan menunggu kamu di sini"
                ),
                'moods': ['Romantic', 'Sad'],
                'kutipan': [
                    {
                        'teks': 'Biar aku yang mengalah dan menunggu kamu di sini',
                        'penjelasan': 'Kesabaran tulus seorang pecinta',
                    },
                ],
            },

            # 7. NOSTALGIC / RETRO HITS
            {
                'judul': 'Tak Seperti Yang Dulu',
                'artis': 'Sheila On 7',
                'album': 'Kisah Klasik Untuk Masa Depan',
                'tahun': 2000,
                'genre': 'classic hits',
                'energy': 'medium',
                'bahasa': 'Indonesia',
                'alunan': 'retro pop',
                'youtube_id': 'vPIQdOZ5guI',
                'lirik': (
                    "Kini semua berubah tak seperti yang dulu\n"
                    "Kala kau dan aku masih saling percaya\n"
                    "Mengenang hari-hari indah saat SMA"
                ),
                'moods': ['Nostalgic', 'Sad'],
                'kutipan': [
                    {
                        'teks': 'Kini semua berubah tak seperti yang dulu, kala kau dan aku masih saling percaya',
                        'penjelasan': 'Nostalgia masa lalu yang hangat sekaligus mengharukan',
                    },
                ],
            },
            {
                'judul': 'Mungkin Nanti',
                'artis': 'Peterpan',
                'album': 'Bintang Di Surga',
                'tahun': 2004,
                'genre': 'retro pop',
                'energy': 'medium',
                'bahasa': 'Indonesia',
                'alunan': 'classic pop',
                'youtube_id': 'SWcMwUySDvI',
                'lirik': (
                    "Saat hatimu terluka, hapuslah air mata\n"
                    "Dan bila kau merasa sepi ingatlah aku kan selalu ada\n"
                    "Mungkin nanti kau kan mengerti mengapa aku begini"
                ),
                'moods': ['Nostalgic', 'Romantic'],
                'kutipan': [
                    {
                        'teks': 'Dan bila kau merasa sepi ingatlah aku kan selalu ada',
                        'penjelasan': 'Lagu klasik nostalgia yang menemani masa remaja',
                    },
                ],
            },

            # 8. ANGRY / FRUSTRATED
            {
                'judul': 'Aku Yang Tersakiti',
                'artis': 'Judika',
                'album': 'Mencari Cinta',
                'tahun': 2013,
                'genre': 'rock',
                'energy': 'high',
                'bahasa': 'Indonesia',
                'alunan': 'rock ballad',
                'youtube_id': '9tZPmSv6DTs',
                'lirik': (
                    "Pernahkah kau merasa hatimu hancur berkeping-keping?\n"
                    "Akulah yang tersakiti! Akulah yang terluka!\n"
                    "Kau tega menduakan cintaku, kau hancurkan semua mimpiku!"
                ),
                'moods': ['Angry / Frustrated', 'Sad'],
                'kutipan': [
                    {
                        'teks': 'Akulah yang tersakiti! Kau tega menduakan cintaku!',
                        'penjelasan': 'Penyaluran emosi kekesalan dan amarah karena dikhianati',
                    },
                ],
            },
            {
                'judul': 'Hampa',
                'artis': 'Ari Lasso',
                'album': 'Keseimbangan',
                'tahun': 2003,
                'genre': 'rock',
                'energy': 'high',
                'bahasa': 'Indonesia',
                'alunan': 'rock',
                'youtube_id': 'fQ3H3U6MzSE',
                'lirik': (
                    "Kututup pintu hatiku untuk semua kata manismu\n"
                    "Cukup sudah kau permainkan aku!\n"
                    "Hampa kini kurasa tanpa dirimu"
                ),
                'moods': ['Angry / Frustrated', 'Sad'],
                'kutipan': [
                    {
                        'teks': 'Kututup pintu hatiku untuk semua kata manismu, cukup sudah kau permainkan aku!',
                        'penjelasan': 'Rasa muak dan marah terhadap kebohongan berulang',
                    },
                ],
            },
        ]

        for s_data in lagu_data:
            mood_names = s_data.pop('moods')
            quotes = s_data.pop('kutipan')

            lagu, created = Lagu.objects.update_or_create(
                judul=s_data['judul'],
                artis=s_data['artis'],
                defaults=s_data
            )

            # Relasi mood
            matched_moods = [mood_objects[m] for m in mood_names if m in mood_objects]
            lagu.moods.set(matched_moods)

            # Buat kutipan jika belum ada
            if created or not lagu.kutipan_set.exists():
                for q in quotes:
                    KutipanLirik.objects.create(lagu=lagu, **q)

            status = '✅ Dibuat' if created else '🔄 Diperbarui'
            self.stdout.write(f"  {status}: {lagu.judul} ({', '.join(mood_names)})")

        self.stdout.write(self.style.SUCCESS(
            f'\n🎉 Selesai! {Mood.objects.count()} Mood resmi Moodify & {Lagu.objects.count()} Lagu multi-parameter aktif!'
        ))
