from django.contrib import admin
from .models import Mood, Lagu, KutipanLirik, FavoriteSong, MoodHistory, SongMotivationCache


class KutipanInline(admin.TabularInline):
    model = KutipanLirik
    extra = 1


@admin.register(Mood)
class MoodAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'nama', 'slug', 'contoh_genre', 'warna']
    search_fields = ['nama', 'kata_kunci']


@admin.register(Lagu)
class LaguAdmin(admin.ModelAdmin):
    list_display = ['judul', 'artis', 'genre', 'energy', 'bahasa', 'alunan', 'tahun']
    list_filter = ['moods', 'genre', 'energy', 'bahasa', 'alunan']
    search_fields = ['judul', 'artis', 'lirik']
    filter_horizontal = ['moods']
    inlines = [KutipanInline]


@admin.register(KutipanLirik)
class KutipanLirikAdmin(admin.ModelAdmin):
    list_display = ['teks', 'lagu']
    search_fields = ['teks', 'lagu__judul']


@admin.register(FavoriteSong)
class FavoriteSongAdmin(admin.ModelAdmin):
    list_display = ['lagu', 'session_key', 'created_at']
    search_fields = ['lagu__judul', 'lagu__artis', 'session_key']


@admin.register(MoodHistory)
class MoodHistoryAdmin(admin.ModelAdmin):
    list_display = ['detected_mood', 'energy_level', 'activity', 'session_key', 'created_at']
    list_filter = ['detected_mood', 'energy_level', 'created_at']
    search_fields = ['input_text', 'session_key']


@admin.register(SongMotivationCache)
class SongMotivationCacheAdmin(admin.ModelAdmin):
    list_display = ['title', 'artist', 'source', 'song_type', 'created_at']
    search_fields = ['title', 'artist', 'message']
    list_filter = ['source', 'song_type']
