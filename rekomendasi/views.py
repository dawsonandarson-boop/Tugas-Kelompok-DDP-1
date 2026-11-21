from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Mood, Lagu, KutipanLirik, FavoriteSong, MoodHistory
from .forms import CurhatForm
from .utils import (
    rekomendasikan_lagu_moodify,
    detect_mood_from_text,
    rekomendasikan_lagu_moodify as rekomendasikan_lagu
)
from .api_service import (
    search_tracks_api,
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
    Halaman utama Moodify:
    - Input curhat / text mood detection (Fitur A)
    - 8 Kategori mood resmi Moodify
    - Mood History pengguna (Fitur E)
    - Kurasi lagu pilihan (Fitur C & F)
    """
    session_key = get_or_create_session_key(request)
    moods = Mood.objects.all().order_by('id')
    form = CurhatForm()
    total_lagu = Lagu.objects.count()
    featured_lagu = Lagu.objects.prefetch_related('moods', 'kutipan_set').all()[:8]

    # Fitur E: Ambil riwayat mood pengguna dari session ini
    mood_history = MoodHistory.objects.filter(session_key=session_key).select_related('detected_mood')[:5]

    # Ambil daftar ID lagu favorit pengguna
    favorite_ids = set(FavoriteSong.objects.filter(session_key=session_key).values_list('lagu_id', flat=True))

    context = {
        'form': form,
        'moods': moods,
        'total_lagu': total_lagu,
        'featured_lagu': featured_lagu,
        'mood_history': mood_history,
        'favorite_ids': favorite_ids,
    }
    return render(request, 'rekomendasi/home.html', context)


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
    kutipan_list = lagu.kutipan_set.all()
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
                'lirik': lyrics,
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
            'lirik': lirik,
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
                'lirik': lirik,
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
