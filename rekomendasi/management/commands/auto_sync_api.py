"""
Management command untuk mengimpor puluhan lagu secara OTOMATIS dari API.
Jalankan: python manage.py auto_sync_api
"""

from django.core.management.base import BaseCommand
from rekomendasi.models import Mood, Lagu, KutipanLirik
from rekomendasi.api_service import (
    search_tracks_api,
    fetch_lyrics_api,
    find_youtube_id,
    analyze_lyrics_for_moods_and_quotes
)


class Command(BaseCommand):
    help = 'Mengimpor lagu-lagu populer secara otomatis dari API tanpa input manual satu per satu'

    def handle(self, *args, **options):
        self.stdout.write('⚡ Memulai Auto-Sync Lagu Populer dari API Global...\n')

        # Daftar kurasi lagu populer berdasarkan 8 Mood
        curated_queries = [
            # Happy
            ('GAC Bahagia', 'Happy', 'high', 'Indonesia'),
            ('Tulus Manusia Kuat', 'Happy', 'high', 'Indonesia'),
            ('RAN Selamat Pagi', 'Happy', 'high', 'Indonesia'),

            # Sad / Galau
            ('Bernadya Satu Bulan', 'Sad', 'low', 'Indonesia'),
            ('Mahalini Sial', 'Sad', 'medium', 'Indonesia'),
            ('Tulus Hati Hati di Jalan', 'Sad', 'low', 'Indonesia'),
            ('Nadin Amizah Rayuan Perempuan Gila', 'Sad', 'low', 'Indonesia'),

            # Romantic
            ('Raim Laode Komang', 'Romantic', 'medium', 'Indonesia'),
            ('Pamungkas To the Bone', 'Romantic', 'medium', 'English'),
            ('Afgan Panah Asmara', 'Romantic', 'medium', 'Indonesia'),

            # Relaxed
            ('Fourtwnty Zona Nyaman', 'Relaxed', 'low', 'Indonesia'),
            ('Sal Priadi Dari Planet Lain', 'Relaxed', 'low', 'Indonesia'),
            ('Ardhito Pramono Bitterlove', 'Relaxed', 'low', 'English'),

            # Focus
            ('Lofi Study Beats', 'Focus', 'low', 'Instrumental'),
            ('Acoustic Chill Guitar Study', 'Focus', 'low', 'Instrumental'),

            # Energetic
            ('Kotak Beraksi', 'Energetic', 'high', 'Indonesia'),
            ('Slank I Miss You But I Hate You', 'Energetic', 'high', 'Indonesia'),

            # Nostalgic
            ('Dewa 19 Kangen', 'Nostalgic', 'medium', 'Indonesia'),
            ('Chrisye Kala Cinta Menggoda', 'Nostalgic', 'medium', 'Indonesia'),
            ('Glenn Fredly Januari', 'Nostalgic', 'medium', 'Indonesia'),

            # Angry / Frustrated
            ('Feast Peradaban', 'Angry / Frustrated', 'high', 'Indonesia'),
            ('Barasuara Bahas Bahasa', 'Angry / Frustrated', 'high', 'Indonesia'),
        ]

        success_count = 0

        for query, target_mood_name, default_energy, default_bahasa in curated_queries:
            self.stdout.write(f"🔍 Mencari API untuk: '{query}'...")
            tracks = search_tracks_api(query, limit=1)

            if not tracks:
                self.stdout.write(self.style.WARNING(f"  ⚠️ Tidak ditemukan di API: {query}"))
                continue

            track = tracks[0]
            judul = track['judul']
            artis = track['artis']

            # Cek apakah sudah ada di DB
            if Lagu.objects.filter(judul__iexact=judul, artis__iexact=artis).exists():
                self.stdout.write(f"  ℹ️ Sudah ada di database: {judul} - {artis}")
                continue

            self.stdout.write(f"  📥 Menarik lirik untuk '{judul} - {artis}'...")
            lyrics = fetch_lyrics_api(judul, artis)
            if not lyrics:
                lyrics = f"Lirik lagu {judul} oleh {artis}."

            youtube_id = find_youtube_id(judul, artis)
            suggested_mood_ids, top_quotes = analyze_lyrics_for_moods_and_quotes(lyrics)

            target_mood = Mood.objects.filter(nama__iexact=target_mood_name).first()

            lagu = Lagu.objects.create(
                judul=judul,
                artis=artis,
                album=track.get('album', ''),
                genre=target_mood.contoh_genre.split(',')[0].strip() if target_mood and target_mood.contoh_genre else 'Pop',
                energy=default_energy,
                bahasa=default_bahasa,
                alunan='mellow' if default_energy == 'low' else 'upbeat',
                youtube_id=youtube_id,
                cover_url=track.get('cover_url', ''),
                audio_preview_url=track.get('preview_url', ''),
                lirik=lyrics,
            )

            # Assign mood
            if target_mood:
                lagu.moods.add(target_mood)
            if suggested_mood_ids:
                lagu.moods.add(*suggested_mood_ids)

            # Buat kutipan
            if top_quotes:
                for q_line in top_quotes:
                    KutipanLirik.objects.create(
                        lagu=lagu,
                        teks=q_line,
                        penjelasan=f"Kutipan lirik populer dari lagu {judul}"
                    )

            success_count += 1
            self.stdout.write(self.style.SUCCESS(f"  ✅ Berhasil diimpor otomatis: {judul} - {artis}"))

        self.stdout.write(self.style.SUCCESS(
            f"\n🎉 Auto-Sync selesai! Berhasil menambahkan {success_count} lagu baru secara otomatis."
        ))
