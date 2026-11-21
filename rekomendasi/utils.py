"""
Moodify Recommendation Engine
Arsitektur Rekomendasi Berbasis Rule-Based Multi-Parameter:
- Mood Detection from Text
- Energy Level Detection (Low, Medium, High)
- Activity Detection (Studying, Relaxing, Workout, etc.)
- Weighted Multi-Parameter Scoring:
    * Mood Cocok: 50 poin
    * Genre Cocok: 20 poin
    * Energy Cocok: 15 poin
    * Bahasa Cocok: 15 poin
    * Total: 100 poin (ditambah bonus kecocokan lirik)
"""

import re
from .models import Mood, Lagu


# Pemetaan Kata Kunci 8 Mood Utama Moodify
MOOD_KEYWORDS = {
    'Happy': [
        'senang', 'bahagia', 'gembira', 'ceria', 'riang', 'sukacita', 'happy',
        'tersenyum', 'tertawa', 'asik', 'fun', 'seru', 'gembira', 'menikmati'
    ],
    'Sad': [
        'sedih', 'kecewa', 'galau', 'menangis', 'nangis', 'patah hati', 'luka',
        'hancur', 'terluka', 'sakit hati', 'hampa', 'kosong', 'kesepian',
        'sendiri', 'sendirian', 'sepi', 'ga setara', 'nggak setara', 'tidak setara',
        'minder', 'insecure', 'beda level', 'tak pantas', 'bertepuk sebelah tangan',
        'ditinggal', 'dicampakkan', 'down', 'pilu', 'lara'
    ],
    'Romantic': [
        'romantis', 'cinta', 'sayang', 'jatuh cinta', 'kasmaran', 'naksir',
        'pacar', 'kekasih', 'sweet', 'peluk', 'dekap', 'berdua', 'manis',
        'terpesona', 'pujaan hati', 'soulmate'
    ],
    'Relaxed': [
        'santai', 'tenang', 'rileks', 'relax', 'chill', 'rebahan', 'istirahat',
        'capek', 'lelah', 'penat', 'melepas lelah', 'sore', 'adem', 'sejuk',
        'damai', 'healing', 'libur', 'ngopi', 'santai sejenak'
    ],
    'Focus': [
        'belajar', 'fokus', 'konsentrasi', 'tugas', 'kuliah', 'kerja', 'nugas',
        'skripsi', 'membaca', 'baca', 'coding', 'ujian', 'mengerjakan',
        'deadline', 'proyek', 'produktif', 'instrumental'
    ],
    'Energetic': [
        'semangat', 'energi', 'bersemangat', 'energetic', 'workout', 'olahraga',
        'gym', 'lari', 'membara', 'gas', 'bangkit', 'kuat', 'bertenaga',
        'pesta', 'joget', 'dance', 'membakar'
    ],
    'Nostalgic': [
        'nostalgia', 'kenangan', 'masa lalu', 'teringat', 'memori', 'dulu',
        'masa sma', 'masa kecil', 'waktu dulu', 'kangen dulu', 'jadul',
        'klasik', 'rindu masa', 'teringat kembali'
    ],
    'Angry / Frustrated': [
        'marah', 'kesal', 'frustrasi', 'benci', 'emosi', 'muak', 'jengkel',
        'dendam', 'berontak', 'amarah', 'muak dengan semua', 'muak',
        'capek dibohongi', 'geram', 'panas'
    ],
}

# Pemetaan Deteksi Level Energi
ENERGY_KEYWORDS = {
    'low': [
        'capek', 'lelah', 'penat', 'tenang', 'santai', 'rebahan', 'tidur',
        'pelan', 'mellow', 'sepi', 'sunyi', 'hampa', 'adem', 'sedih', 'lemas'
    ],
    'high': [
        'semangat', 'energi', 'workout', 'olahraga', 'gym', 'lari', 'pesta',
        'joget', 'membara', 'marah', 'kesal', 'bertenaga', 'berenergi', 'teriak'
    ],
    'medium': [
        'belajar', 'fokus', 'nugas', 'kerja', 'jalan-jalan', 'ngobrol', 'biasa', 'sedang'
    ],
}

# Pemetaan Deteksi Aktivitas
ACTIVITY_KEYWORDS = {
    'Studying / Nugas': ['belajar', 'fokus', 'tugas', 'kuliah', 'nugas', 'skripsi', 'membaca', 'ujian', 'mengerjakan'],
    'Relaxing / Healing': ['capek', 'lelah', 'santai', 'rebahan', 'istirahat', 'healing', 'penat', 'melepas lelah'],
    'Working Out / Gym': ['olahraga', 'workout', 'gym', 'lari', 'jogging', 'pemanasan'],
    'Heartbreak / Galau': ['patah hati', 'putus', 'minder', 'ga setara', 'sedih', 'menangis', 'kecewa', 'galau'],
    'Romance / Dating': ['kencan', 'pacar', 'kangen', 'rindu', 'cinta', 'sayang', 'berdua'],
    'Nostalgia / Mengenang': ['kenangan', 'masa lalu', 'sma', 'dulu', 'teringat', 'nostalgia'],
}


def tokenize(text):
    """Memecah teks menjadi token kata bersih."""
    text = text.lower()
    text = re.sub(r'[^\w\s\-]', ' ', text)
    return [w for w in text.split() if len(w) > 1]


def detect_mood_from_text(text):
    """
    Fitur A: Mood Detection from Text.
    Menganalisis teks bebas untuk menentukan Mood, Energy Level, dan Activity.
    """
    if not text:
        return 'Relaxed', 'medium', 'Umum'

    text_lower = text.lower()
    tokens = tokenize(text)

    # 1. Hitung skor per mood
    mood_scores = {}
    for mood_name, keywords in MOOD_KEYWORDS.items():
        score = 0
        for kw in keywords:
            if kw in text_lower:
                score += 3
            for token in tokens:
                if len(token) > 3 and len(kw) > 3 and token[:4] == kw[:4]:
                    score += 1
        mood_scores[mood_name] = score

    # Pilih mood dengan skor tertinggi
    sorted_moods = sorted(mood_scores.items(), key=lambda x: x[1], reverse=True)
    detected_mood = sorted_moods[0][0] if sorted_moods and sorted_moods[0][1] > 0 else 'Relaxed'

    # 2. Deteksi Energy Level
    energy_scores = {'low': 0, 'medium': 1, 'high': 0}
    for energy_level, kws in ENERGY_KEYWORDS.items():
        for kw in kws:
            if kw in text_lower:
                energy_scores[energy_level] += 2
    detected_energy = max(energy_scores, key=energy_scores.get)

    # 3. Deteksi Activity
    detected_activity = 'Mendengarkan Santai'
    for activity_name, kws in ACTIVITY_KEYWORDS.items():
        for kw in kws:
            if kw in text_lower:
                detected_activity = activity_name
                break

    return detected_mood, detected_energy, detected_activity


def cari_kutipan_terbaik(lagu, keywords):
    """Mengambil kutipan lirik terbaik yang paling sesuai."""
    kutipan_list = lagu.kutipan_set.all()
    if not kutipan_list:
        lines = [b.strip() for b in lagu.lirik.split('\n') if b.strip()]
        return ' / '.join(lines[:2]) if lines else lagu.lirik[:100]

    best_kutipan = None
    best_score = -1

    for kutipan in kutipan_list:
        score = 0
        teks_lower = kutipan.teks.lower()
        for kw in keywords:
            if kw in teks_lower:
                score += 2
        if score > best_score:
            best_score = score
            best_kutipan = kutipan

    if not best_kutipan:
        best_kutipan = kutipan_list.first()

    return best_kutipan.teks if best_kutipan else ''


def rekomendasikan_lagu_moodify(teks_curhat='', mood_id=None, target_genre=None, target_energy=None, target_bahasa=None, limit=8):
    """
    Fitur B: Multi-Parameter Music Recommendation System (Skor 0 - 100).

    Formula Bobot:
      - Mood Match:    50 poin
      - Genre Match:   20 poin
      - Energy Match:  15 poin
      - Bahasa Match:  15 poin
      Total: 100 poin (+ bonus kecocokan lirik)
    """
    all_lagu = Lagu.objects.prefetch_related('moods', 'kutipan_set').all()
    if not all_lagu.exists():
        return {
            'detected_mood_obj': None,
            'detected_energy': 'medium',
            'detected_activity': 'Mendengarkan Musik',
            'rekomendasi': [],
        }

    # Inisialisasi parameter
    detected_mood_obj = None
    detected_energy = target_energy or 'medium'
    detected_activity = 'Mendengarkan Musik'
    keywords = []

    # Skenario 1: Input Mood Manual
    if mood_id:
        try:
            detected_mood_obj = Mood.objects.get(id=mood_id)
        except Mood.DoesNotExist:
            pass

    # Skenario 2: Input Teks Bebas
    if teks_curhat:
        mood_name, auto_energy, auto_act = detect_mood_from_text(teks_curhat)
        keywords = tokenize(teks_curhat)
        if not target_energy:
            detected_energy = auto_energy
        detected_activity = auto_act

        if not detected_mood_obj:
            detected_mood_obj = Mood.objects.filter(nama__icontains=mood_name).first()

    # Fallback mood jika belum ada
    if not detected_mood_obj:
        detected_mood_obj = Mood.objects.filter(nama__icontains='Relaxed').first() or Mood.objects.first()

    # Kriteria Bobot
    hasil = []
    lirik_keywords = keywords if keywords else (detected_mood_obj.get_kata_kunci_list() if detected_mood_obj else [])

    for lagu in all_lagu:
        score_breakdown = {
            'mood_score': 0,
            'genre_score': 0,
            'energy_score': 0,
            'bahasa_score': 0,
            'lyrics_bonus': 0,
        }

        # 1. Mood Match (Bobot: 50)
        if detected_mood_obj and detected_mood_obj in lagu.moods.all():
            score_breakdown['mood_score'] = 50
        elif detected_mood_obj:
            # Partial match jika ada kata kunci yang mirip
            mood_kws = detected_mood_obj.get_kata_kunci_list()
            matched_kws = sum(1 for kw in mood_kws if kw in lagu.alunan.lower() or kw in lagu.lirik.lower())
            if matched_kws > 0:
                score_breakdown['mood_score'] = min(35, matched_kws * 10)

        # 2. Genre Match (Bobot: 20)
        if target_genre:
            if target_genre.lower() in lagu.genre.lower():
                score_breakdown['genre_score'] = 20
        elif detected_mood_obj and detected_mood_obj.contoh_genre:
            for g in detected_mood_obj.contoh_genre.split(','):
                if g.strip().lower() in lagu.genre.lower():
                    score_breakdown['genre_score'] = 20
                    break
        else:
            score_breakdown['genre_score'] = 15  # default baseline

        # 3. Energy Match (Bobot: 15)
        if lagu.energy == detected_energy:
            score_breakdown['energy_score'] = 15
        elif lagu.energy == 'medium':
            score_breakdown['energy_score'] = 10
        else:
            score_breakdown['energy_score'] = 5

        # 4. Bahasa Match (Bobot: 15)
        if target_bahasa:
            if lagu.bahasa.lower() == target_bahasa.lower():
                score_breakdown['bahasa_score'] = 15
            else:
                score_breakdown['bahasa_score'] = 5
        else:
            score_breakdown['bahasa_score'] = 15

        # 5. Bonus Kecocokan Lirik (Hingga +15 poin)
        lirik_lower = lagu.lirik.lower()
        lyric_matches = 0
        for kw in lirik_keywords:
            if kw in lirik_lower:
                lyric_matches += 1
        score_breakdown['lyrics_bonus'] = min(15, lyric_matches * 3)

        total_skor = (
            score_breakdown['mood_score'] +
            score_breakdown['genre_score'] +
            score_breakdown['energy_score'] +
            score_breakdown['bahasa_score'] +
            score_breakdown['lyrics_bonus']
        )

        kutipan = cari_kutipan_terbaik(lagu, lirik_keywords)

        hasil.append({
            'lagu': lagu,
            'skor': total_skor,
            'breakdown': score_breakdown,
            'kutipan': kutipan,
            'moods': list(lagu.moods.all()),
        })

    # Urutkan berdasarkan total skor tertinggi
    hasil.sort(key=lambda x: x['skor'], reverse=True)

    return {
        'detected_mood_obj': detected_mood_obj,
        'detected_energy': detected_energy,
        'detected_activity': detected_activity,
        'rekomendasi': hasil[:limit],
    }
