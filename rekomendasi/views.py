from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
import urllib.parse
import json
from .models import Mood, Lagu, KutipanLirik, FavoriteSong, MoodHistory, SongMotivationCache
from .forms import CurhatForm
from .utils import (
    rekomendasikan_lagu_moodify,
    detect_mood_from_text,
    rekomendasikan_lagu_moodify as rekomendasikan_lagu
)
from .api_service import (
    search_tracks_api,
    generate_search_keywords,
    generate_song_motivation,
    fetch_lyrics_quote,
    fetch_lyrics_api,
    find_youtube_id,
    analyze_lyrics_for_moods_and_quotes
)


def get_or_create_session_key(request):
    """Memastikan pengguna memiliki session_key unik untuk favorit dan history."""
    if not request.session.session_key:
        request.session.save()
    return request.session.session_key


def home(request):
    """
    Unified discovery page for direct search, free-form prompts, and mood chips.
    """
    moods = Mood.objects.all().order_by('id')
    total_lagu = Lagu.objects.count()

    # The three discovery paths share one result grid and one player.
    query = request.GET.get('q', '').strip()[:120]
    prompt = request.GET.get('prompt', '').strip()[:500]
    mood_id = request.GET.get('mood', '').strip()
    selected_mood = Mood.objects.filter(id=mood_id).first() if mood_id.isdigit() else None
    search_term = query
    search_mode = 'search'
    status_note = ''

    if prompt:
        search_mode = 'prompt'
        search_term = generate_search_keywords(prompt)
        if not search_term:
            stop_words = {
                'aku', 'saya', 'ingin', 'pengen', 'mau', 'lagu', 'musik', 'yang',
                'untuk', 'buat', 'saat', 'ketika', 'dengan', 'sambil', 'sedang',
                'mendengarkan', 'dengarkan', 'sesuatu', 'tolong', 'carikan', 'cari',
                'dong', 'nuansa', 'bernuansa', 'terasa', 'seperti', 'lebih', 'agak',
            }
            words = [word for word in prompt.lower().split() if word.strip('.,!?;:') not in stop_words]
            search_term = ' '.join(words[:8]) or prompt
            status_note = 'Pencarian prompt memakai pencocokan kata lokal. Gemini aktifkan dengan GEMINI_API_KEY.'
        else:
            status_note = 'Gemini menyederhanakan prompt menjadi kata kunci pencarian.'
    elif selected_mood:
        search_mode = 'mood'
        search_term = selected_mood.contoh_genre.split(',')[0].strip() if selected_mood.contoh_genre else selected_mood.nama
        aliases = {
            'happy': 'feel good pop', 'sad': 'sad acoustic ballad', 'romantic': 'romantic love songs',
            'relaxed': 'chill lo-fi', 'focus': 'instrumental study music', 'energetic': 'energetic rock',
            'nostalgic': 'nostalgic classic pop', 'angry / frustrated': 'intense rock',
        }
        search_term = aliases.get(selected_mood.nama.lower(), search_term)

    search_results = search_tracks_api(search_term, limit=10) if search_term else []

    mood_theme = {
        'happy': ('#FFD23F', '#241c08', 'Senang'),
        'sad': ('#7FB0FF', '#0c1730', 'Sedih'),
        'relaxed': ('#B79CFF', '#1b1230', 'Santai'),
        'energetic': ('#FF8A7E', '#351416', 'Semangat'),
        'romantic': ('#FF9ED8', '#32152b', 'Romantis'),
        'focus': ('#2ED1A0', '#0b2922', 'Fokus'),
        'nostalgic': ('#FFD23F', '#241c08', 'Nostalgia'),
        'angry / frustrated': ('#FF8A7E', '#351416', 'Intens'),
    }
    accent, mood_background, mood_label = mood_theme.get(
        selected_mood.nama.lower() if selected_mood else '',
        ('#B79CFF', '#171326', 'Pilihanmu'),
    )
    if prompt and not selected_mood:
        detected_name, _, _ = detect_mood_from_text(prompt)
        detected_key = {
            'Happy': 'happy', 'Sad': 'sad', 'Relaxed': 'relaxed',
            'Energetic': 'energetic', 'Romantic': 'romantic', 'Focus': 'focus',
            'Nostalgic': 'nostalgic', 'Angry / Frustrated': 'angry / frustrated',
        }.get(detected_name)
        if detected_key:
            accent, mood_background, mood_label = mood_theme[detected_key]

    context = {
        'moods': moods,
        'total_lagu': total_lagu,
        'search_results': search_results,
        'query': query,
        'prompt': prompt,
        'search_term': search_term,
        'search_mode': search_mode,
        'status_note': status_note,
        'selected_mood': selected_mood,
        'mood_accent': accent,
        'mood_background': mood_background,
        'mood_label': mood_label,
    }
    return render(request, 'rekomendasi/home.html', context)


def kutipan_lagu_api(request):
    """Fetch a short LRCLIB excerpt for the currently selected track."""
    judul = request.GET.get('judul', '').strip()[:200]
    artis = request.GET.get('artis', '').strip()[:200]
    if not judul or not artis:
        return JsonResponse({'quote': '', 'source_url': ''}, status=400)
    return JsonResponse(fetch_lyrics_quote(judul, artis))


def motivasi_lagu_api(request):
    """Return a cached track type and encouragement, generating it once when possible."""
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)
    try:
        data = json.loads(request.body.decode('utf-8'))
    except (UnicodeDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    if not isinstance(data, dict):
        return JsonResponse({'error': 'Invalid track'}, status=400)

    title = str(data.get('title', '')).strip()[:200]
    artist = str(data.get('artist', '')).strip()[:200]
    album = str(data.get('album', '')).strip()[:200]
    source = str(data.get('source', '')).strip()
    external_id = str(data.get('external_id', '')).strip()[:60]
    requested_type = str(data.get('type', 'Pilihanmu')).strip()[:40]
    if not title or not artist or not external_id or source not in {'Deezer', 'iTunes'}:
        return JsonResponse({'error': 'Invalid track'}, status=400)

    cached = SongMotivationCache.objects.filter(source=source, external_id=external_id).first()
    if cached:
        return JsonResponse({'song_type': cached.song_type, 'message': cached.message, 'generated': True})

    generated = generate_song_motivation(title, artist, album)
    if generated:
        cached, _ = SongMotivationCache.objects.get_or_create(
            source=source,
            external_id=external_id,
            defaults={
                'title': title,
                'artist': artist,
                'song_type': generated['song_type'],
                'message': generated['message'],
            },
        )
        return JsonResponse({'song_type': cached.song_type, 'message': cached.message, 'generated': True})

    fallback_messages = {
        'Senang': 'Nikmati momen baik ini. Kamu pantas merayakan hal-hal kecil.',
        'Sedih': 'Tidak apa-apa berjalan pelan. Perasaanmu layak diberi ruang.',
        'Santai': 'Tarik napas sejenak. Kamu tidak harus menyelesaikan semuanya hari ini.',
        'Semangat': 'Simpan energi baikmu dan arahkan satu langkah demi satu langkah.',
        'Romantis': 'Rawat rasa hangat itu, termasuk untuk dirimu sendiri.',
        'Fokus': 'Satu hal dalam satu waktu. Kemajuan kecil tetap berarti.',
        'Nostalgia': 'Kenangan boleh menemani, sambil kamu tetap melangkah ke depan.',
        'Intens': 'Beri ruang untuk emosimu, lalu pilih langkah yang menjaga dirimu.',
    }
    return JsonResponse({
        'song_type': requested_type,
        'message': fallback_messages.get(requested_type, 'Semoga lagu ini menemani langkahmu dengan baik.'),
        'generated': False,
    })


def hasil_rekomendasi(request):
    """
    Fitur A & B:
    - Menganalisis teks curhat (Mood, Energy, Activity)
    - Menghitung skor rekomendasi multi-parameter (Mood: 50, Genre: 20, Energy: 15, Bahasa: 15)
    - Menyimpan ke Mood History (Fitur E)
    """
    session_key = get_or_create_session_key(request)

    if request.method == 'POST':
        form = CurhatForm(request.POST)
        teks_curhat = request.POST.get('curhat', '').strip()
        mood_id = request.POST.get('mood_id') or None
        target_genre = request.POST.get('genre') or None
        target_energy = request.POST.get('energy') or None
        target_bahasa = request.POST.get('bahasa') or None

        # Jalankan mesin rekomendasi multi-parameter
        analysis = rekomendasikan_lagu_moodify(
            teks_curhat=teks_curhat,
            mood_id=mood_id,
            target_genre=target_genre,
            target_energy=target_energy,
            target_bahasa=target_bahasa,
            limit=8,
        )

        detected_mood_obj = analysis['detected_mood_obj']
        detected_energy = analysis['detected_energy']
        detected_activity = analysis['detected_activity']
        rekomendasi = analysis['rekomendasi']

        # Fitur E: Simpan riwayat rekomendasi ke MoodHistory
        if detected_mood_obj:
            history_entry = MoodHistory.objects.create(
                session_key=session_key,
                input_text=teks_curhat,
                detected_mood=detected_mood_obj,
                energy_level=detected_energy,
                activity=detected_activity,
            )
            song_objs = [item['lagu'] for item in rekomendasi[:4]]
            history_entry.recommended_songs.set(song_objs)

        # Ambil daftar favorit
        favorite_ids = set(FavoriteSong.objects.filter(session_key=session_key).values_list('lagu_id', flat=True))

        context = {
            'rekomendasi': rekomendasi,
            'curhat': teks_curhat,
            'mood_dipilih': detected_mood_obj,
            'detected_energy': detected_energy,
            'detected_activity': detected_activity,
            'jumlah_hasil': len(rekomendasi),
            'favorite_ids': favorite_ids,
        }
        return render(request, 'rekomendasi/hasil.html', context)

    return redirect('home')


def detail_lagu(request, lagu_id):
    """
    Fitur F: Halaman detail lagu dengan pemutar audio 30s,
    tautan Spotify, YouTube Music, dan YouTube embed resmi.
    """
    session_key = get_or_create_session_key(request)
    lagu = get_object_or_404(Lagu.objects.prefetch_related('moods', 'kutipan_set'), id=lagu_id)
    kutipan_list = lagu.kutipan_set.all()[:2]
    moods = lagu.moods.all()

    # Lagu serupa berdasarkan mood
    mood_ids = moods.values_list('id', flat=True)
    lagu_serupa = Lagu.objects.filter(moods__in=mood_ids).exclude(id=lagu.id).distinct()[:4]

    is_favorited = FavoriteSong.objects.filter(session_key=session_key, lagu=lagu).exists()

    context = {
        'lagu': lagu,
        'kutipan_list': kutipan_list,
        'moods': moods,
        'lagu_serupa': lagu_serupa,
        'is_favorited': is_favorited,
        'quote_source_url': 'https://lrclib.net/search?q=' + urllib.parse.quote(f'{lagu.artis} {lagu.judul}'),
    }
    return render(request, 'rekomendasi/detail.html', context)


def daftar_lagu(request):
    """
    Fitur C: Song Discovery (Eksplorasi Lagu).
    Filter berdasarkan Genre, Artist, Mood, Energy, Bahasa, dan Pencarian Judul.
    """
    session_key = get_or_create_session_key(request)
    query = request.GET.get('q', '').strip()
    mood_filter = request.GET.get('mood', '').strip()
    genre_filter = request.GET.get('genre', '').strip()
    energy_filter = request.GET.get('energy', '').strip()
    bahasa_filter = request.GET.get('bahasa', '').strip()

    lagu_list = Lagu.objects.prefetch_related('moods').all()

    if query:
        lagu_list = lagu_list.filter(judul__icontains=query) | lagu_list.filter(artis__icontains=query)
    if mood_filter:
        lagu_list = lagu_list.filter(moods__id=mood_filter)
    if genre_filter:
        lagu_list = lagu_list.filter(genre__icontains=genre_filter)
    if energy_filter:
        lagu_list = lagu_list.filter(energy=energy_filter)
    if bahasa_filter:
        lagu_list = lagu_list.filter(bahasa=bahasa_filter)

    lagu_list = lagu_list.distinct()
    moods = Mood.objects.all().order_by('id')

    # Daftar genre unik untuk dropdown filter
    all_genres = Lagu.objects.values_list('genre', flat=True).distinct()

    favorite_ids = set(FavoriteSong.objects.filter(session_key=session_key).values_list('lagu_id', flat=True))

    context = {
        'lagu_list': lagu_list,
        'moods': moods,
        'all_genres': all_genres,
        'query': query,
        'mood_terpilih': mood_filter,
        'genre_terpilih': genre_filter,
        'energy_terpilih': energy_filter,
        'bahasa_terpilih': bahasa_filter,
        'total_lagu': lagu_list.count(),
        'favorite_ids': favorite_ids,
    }
    return render(request, 'rekomendasi/daftar_lagu.html', context)


def toggle_favorite(request, lagu_id):
    """
    Fitur D: Favorite Songs toggle (tambah / hapus dari favorit).
    Bisa via AJAX / POST redirect.
    """
    session_key = get_or_create_session_key(request)
    lagu = get_object_or_404(Lagu, id=lagu_id)

    fav = FavoriteSong.objects.filter(session_key=session_key, lagu=lagu).first()
    if fav:
        fav.delete()
        is_favorited = False
        messages.info(request, f"'{lagu.judul}' dihapus dari daftar favorit.")
    else:
        FavoriteSong.objects.create(session_key=session_key, lagu=lagu)
        is_favorited = True
        messages.success(request, f"'{lagu.judul}' ditambahkan ke lagu favorit! ❤️")

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.GET.get('format') == 'json':
        return JsonResponse({'status': 'ok', 'is_favorited': is_favorited})

    return redirect(request.META.get('HTTP_REFERER', 'daftar_lagu'))


def list_favorites(request):
    """
    Fitur D: Halaman Koleksi Lagu Favorit Pengguna.
    """
    session_key = get_or_create_session_key(request)
    favorites = FavoriteSong.objects.filter(session_key=session_key).select_related('lagu').prefetch_related('lagu__moods')

    context = {
        'favorites': favorites,
        'total_favorites': favorites.count(),
    }
    return render(request, 'rekomendasi/favorit.html', context)


def mood_history_view(request):
    """
    Fitur E: Halaman Riwayat Mood (Mood History Log).
    """
    session_key = get_or_create_session_key(request)
    history_list = MoodHistory.objects.filter(session_key=session_key).select_related('detected_mood').prefetch_related('recommended_songs')

    context = {
        'history_list': history_list,
        'total_history': history_list.count(),
    }
    return render(request, 'rekomendasi/mood_history.html', context)


def cari_lagu_api(request):
    """
    Metode 3 (Hybrid): Pencarian lagu dari API Database Lagu eksternal (Deezer / iTunes).
    """
    query = request.GET.get('q', '').strip()
    hasil_api = []

    if query:
        hasil_api = search_tracks_api(query, limit=10)

    context = {
        'query': query,
        'hasil_api': hasil_api,
    }
    return render(request, 'rekomendasi/cari_api.html', context)


def auto_import_instant(request):
    """
    1-Click Auto Import: Otomatis mengambil lirik, mendeteksi mood,
    dan langsung menyimpan lagu dari API ke database TANPA perlu input manual.
    """
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        artis = request.POST.get('artis', '').strip()
        album = request.POST.get('album', '').strip()
        cover_url = request.POST.get('cover_url', '').strip()
        preview_url = request.POST.get('preview_url', '').strip()

        # Ambil lirik otomatis dari API LRCLIB
        lyrics = fetch_lyrics_api(judul, artis)
        if not lyrics:
            lyrics = f"Lirik lagu {judul} oleh {artis}."

        youtube_id = find_youtube_id(judul, artis)
        suggested_mood_ids, top_quotes = analyze_lyrics_for_moods_and_quotes(lyrics)

        lagu, created = Lagu.objects.update_or_create(
            judul=judul,
            artis=artis,
            defaults={
                'album': album,
                'cover_url': cover_url,
                'audio_preview_url': preview_url,
                'youtube_id': youtube_id,
                'lirik': '',
                'energy': 'medium',
                'bahasa': 'Indonesia',
                'genre': 'Pop',
            }
        )

        if suggested_mood_ids:
            lagu.moods.set(suggested_mood_ids)
        elif not lagu.moods.exists():
            relaxed = Mood.objects.filter(nama='Relaxed').first()
            if relaxed:
                lagu.moods.add(relaxed)

        if top_quotes and not lagu.kutipan_set.exists():
            for q in top_quotes:
                KutipanLirik.objects.create(
                    lagu=lagu,
                    teks=q,
                    penjelasan=f"Kutipan lirik pilihan dari {judul}"
                )

        messages.success(request, f"⚡ Sukses! Lagu '{judul} - {artis}' berhasil otomatis disimpan ke Moodify!")
        return redirect('detail_lagu', lagu_id=lagu.id)

    return redirect('cari_lagu_api')


def preview_import_lagu(request):
    """
    Metode 3 (Hybrid): Mengambil lirik dan metadata dari API, lalu ditampilkan untuk dikonfirmasi.
    """
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        artis = request.POST.get('artis', '').strip()
        album = request.POST.get('album', '').strip()
        cover_url = request.POST.get('cover_url', '').strip()
        preview_url = request.POST.get('preview_url', '').strip()

        lirik = fetch_lyrics_api(judul, artis)
        youtube_id = find_youtube_id(judul, artis)
        suggested_mood_ids, top_quotes = analyze_lyrics_for_moods_and_quotes(lirik)
        all_moods = Mood.objects.all().order_by('id')

        context = {
            'judul': judul,
            'artis': artis,
            'album': album,
            'cover_url': cover_url,
            'preview_url': preview_url,
            'youtube_id': youtube_id,
            # Keep the full API response server-side for quote extraction only.
            'lirik': '',
            'quote_source_url': 'https://lrclib.net/search?q=' + urllib.parse.quote(f'{artis} {judul}'),
            'all_moods': all_moods,
            'suggested_mood_ids': suggested_mood_ids,
            'top_quotes': '\n'.join(top_quotes),
        }
        return render(request, 'rekomendasi/preview_import.html', context)

    return redirect('cari_lagu_api')


def simpan_lagu_api(request):
    """
    Metode 3 (Hybrid): Menyimpan lagu dari API ke database SQLite lokal.
    """
    if request.method == 'POST':
        judul = request.POST.get('judul', '').strip()
        artis = request.POST.get('artis', '').strip()
        album = request.POST.get('album', '').strip()
        tahun = request.POST.get('tahun') or None
        genre = request.POST.get('genre', 'Pop').strip()
        energy = request.POST.get('energy', 'medium').strip()
        bahasa = request.POST.get('bahasa', 'Indonesia').strip()
        alunan = request.POST.get('alunan', 'santai').strip()
        youtube_id = request.POST.get('youtube_id', '').strip()
        cover_url = request.POST.get('cover_url', '').strip()
        audio_preview_url = request.POST.get('audio_preview_url', '').strip()
        lirik = request.POST.get('lirik', '').strip()
        mood_ids = request.POST.getlist('moods')
        kutipan_teks = request.POST.get('kutipan_teks', '').strip()
        kutipan_penjelasan = request.POST.get('kutipan_penjelasan', '').strip()

        if tahun:
            try:
                tahun = int(tahun)
            except ValueError:
                tahun = None

        if not lirik:
            lirik = f"Lirik lagu {judul} oleh {artis} belum tersedia secara otomatis."

        lagu, created = Lagu.objects.update_or_create(
            judul=judul,
            artis=artis,
            defaults={
                'album': album,
                'tahun': tahun,
                'genre': genre,
                'energy': energy,
                'bahasa': bahasa,
                'alunan': alunan,
                'youtube_id': youtube_id,
                'cover_url': cover_url,
                'audio_preview_url': audio_preview_url,
                # The public detail page only displays short attributed excerpts.
                'lirik': '',
            }
        )

        if mood_ids:
            lagu.moods.set(mood_ids)

        if kutipan_teks:
            for baris in kutipan_teks.split('\n'):
                baris_clean = baris.strip()
                if baris_clean:
                    KutipanLirik.objects.create(
                        lagu=lagu,
                        teks=baris_clean,
                        penjelasan=kutipan_penjelasan or 'Kutipan lirik pilihan'
                    )

        action = "berhasil ditambahkan" if created else "berhasil diperbarui"
        messages.success(request, f"Lagu '{judul} - {artis}' {action} ke database Moodify!")
        return redirect('detail_lagu', lagu_id=lagu.id)

    return redirect('cari_lagu_api')
