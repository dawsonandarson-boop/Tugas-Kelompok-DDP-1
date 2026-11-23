import urllib.parse
from django.db import models


class Mood(models.Model):
    """8 Kategori Mood Moodify."""
    nama = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, blank=True, default='')
    deskripsi = models.TextField(blank=True)
    emoji = models.CharField(max_length=10, default='🎵')
    contoh_genre = models.CharField(
        max_length=200, blank=True,
        help_text='Contoh genre: upbeat pop, ballad, lofi, dll'
    )
    kata_kunci = models.TextField(
        help_text='Kata kunci yang terkait, dipisahkan koma.'
    )
    warna = models.CharField(
        max_length=7, default='#6366f1',
        help_text='Warna hex untuk tampilan UI'
    )

    class Meta:
        verbose_name = 'Mood'
        verbose_name_plural = 'Mood'
        ordering = ['id']

    def __str__(self):
        return f"{self.emoji} {self.nama}"

    def get_kata_kunci_list(self):
        """Mengembalikan daftar kata kunci sebagai list."""
        return [k.strip().lower() for k in self.kata_kunci.split(',') if k.strip()]


class Lagu(models.Model):
    """Data lagu beserta metadata rekomendasi multi-parameter Moodify."""
    ENERGY_CHOICES = [
        ('low', 'Low / Tenang'),
        ('medium', 'Medium / Sedang'),
        ('high', 'High / Berenergi'),
    ]

    BAHASA_CHOICES = [
        ('Indonesia', 'Indonesia'),
        ('English', 'English'),
        ('Instrumental', 'Instrumental'),
        ('Lainnya', 'Lainnya'),
    ]

    judul = models.CharField(max_length=200)
    artis = models.CharField(max_length=200)
    album = models.CharField(max_length=200, blank=True)
    tahun = models.IntegerField(null=True, blank=True)
    genre = models.CharField(max_length=100, default='Pop')
    energy = models.CharField(max_length=20, choices=ENERGY_CHOICES, default='medium')
    bahasa = models.CharField(max_length=50, choices=BAHASA_CHOICES, default='Indonesia')
    lirik = models.TextField(
        help_text='Lirik lagu (atau cuplikan lirik utama)'
    )
    moods = models.ManyToManyField(Mood, related_name='lagu_set', blank=True)
    alunan = models.CharField(
        max_length=50, default='sedih',
        help_text='Jenis alunan: santai, tenang, upbeat, ballad, acoustic, rock, mellow'
    )
    youtube_id = models.CharField(
        max_length=20, blank=True,
        help_text='ID video YouTube (bagian setelah v=)'
    )
    cover_url = models.URLField(
        blank=True,
        help_text='URL gambar cover album'
    )
    audio_preview_url = models.URLField(
        blank=True,
        help_text='URL preview audio MP3 30 detik resmi'
    )

    class Meta:
        verbose_name = 'Lagu'
        verbose_name_plural = 'Lagu'
        ordering = ['judul']
        unique_together = ['judul', 'artis']

    def __str__(self):
        return f"{self.judul} - {self.artis}"

    @property
    def is_valid_youtube_id(self):
        return bool(self.youtube_id and len(self.youtube_id) == 11 and not self.youtube_id.startswith('ID_'))

    def get_youtube_embed_url(self):
        """Mengembalikan URL embed YouTube jika ID valid."""
        if self.is_valid_youtube_id:
            return f"https://www.youtube.com/embed/{self.youtube_id}"
        return ""

    def get_youtube_url(self):
        """Mengembalikan URL YouTube langsung atau pencarian otomatis."""
        if self.is_valid_youtube_id:
            return f"https://www.youtube.com/watch?v={self.youtube_id}"
        query = urllib.parse.quote_plus(f"{self.artis} {self.judul} official music video")
        return f"https://www.youtube.com/results?search_query={query}"

    def get_spotify_url(self):
        """Mengembalikan tautan pencarian langsung di Spotify."""
        query = urllib.parse.quote_plus(f"{self.artis} {self.judul}")
        return f"https://open.spotify.com/search/{query}"

    def get_youtube_music_url(self):
        """Mengembalikan tautan langsung di YouTube Music."""
        query = urllib.parse.quote_plus(f"{self.artis} {self.judul}")
        return f"https://music.youtube.com/search?q={query}"

    def get_cover_url(self):
        """Mengembalikan URL cover album atau thumbnail YouTube."""
        if self.cover_url:
            return self.cover_url
        if self.is_valid_youtube_id:
            return f"https://img.youtube.com/vi/{self.youtube_id}/hqdefault.jpg"
        return ""


class KutipanLirik(models.Model):
    """Kutipan/quote dari lirik lagu yang memorable."""
    lagu = models.ForeignKey(Lagu, on_delete=models.CASCADE, related_name='kutipan_set')
    teks = models.TextField(help_text='Kutipan lirik yang paling berkesan')
    penjelasan = models.TextField(
        blank=True,
        help_text='Penjelasan singkat mengapa kutipan ini relatable'
    )

    class Meta:
        verbose_name = 'Kutipan Lirik'
        verbose_name_plural = 'Kutipan Lirik'

    def __str__(self):
        return f'"{self.teks[:50]}..." — {self.lagu.judul}'


class FavoriteSong(models.Model):
    """Fitur D: Lagu Favorit Pengguna (disimpan per session)."""
    session_key = models.CharField(max_length=100, db_index=True)
    lagu = models.ForeignKey(Lagu, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lagu Favorit'
        verbose_name_plural = 'Lagu Favorit'
        unique_together = ['session_key', 'lagu']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.session_key[:8]}... ❤️ {self.lagu.judul}"


class MoodHistory(models.Model):
    """Fitur E: Mood History (Riwayat Rekomendasi Pengguna)."""
    session_key = models.CharField(max_length=100, db_index=True)
    input_text = models.TextField(blank=True)
    detected_mood = models.ForeignKey(Mood, on_delete=models.SET_NULL, null=True, blank=True)
    energy_level = models.CharField(max_length=20, blank=True)
    activity = models.CharField(max_length=100, blank=True)
    recommended_songs = models.ManyToManyField(Lagu, blank=True, related_name='history_appearances')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Riwayat Mood'
        verbose_name_plural = 'Riwayat Mood'
        ordering = ['-created_at']

    def __str__(self):
        mood_name = self.detected_mood.nama if self.detected_mood else 'Manual'
        return f"{self.session_key[:8]} - {mood_name} ({self.created_at.strftime('%d %b %H:%M')})"


class SongMotivationCache(models.Model):
    """One Gemini-generated mood label and original encouragement per external track."""
    source = models.CharField(max_length=20)
    external_id = models.CharField(max_length=60)
    title = models.CharField(max_length=200)
    artist = models.CharField(max_length=200)
    song_type = models.CharField(max_length=40)
    message = models.CharField(max_length=320)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Cache Motivasi Lagu'
        verbose_name_plural = 'Cache Motivasi Lagu'
        constraints = [
            models.UniqueConstraint(fields=['source', 'external_id'], name='unique_song_motivation_track')
        ]

    def __str__(self):
        return f"{self.title} - {self.artist} ({self.song_type})"
