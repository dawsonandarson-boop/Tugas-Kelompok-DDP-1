from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('kutipan/', views.kutipan_lagu_api, name='kutipan_lagu_api'),
    path('motivasi/', views.motivasi_lagu_api, name='motivasi_lagu_api'),
    path('hasil/', views.hasil_rekomendasi, name='hasil'),
    path('lagu/<int:lagu_id>/', views.detail_lagu, name='detail_lagu'),
    path('semua-lagu/', views.daftar_lagu, name='daftar_lagu'),
    path('lagu/<int:lagu_id>/favorit/', views.toggle_favorite, name='toggle_favorite'),
    path('favorit/', views.list_favorites, name='list_favorites'),
    path('riwayat/', views.mood_history_view, name='mood_history'),
    path('tambah-api/', views.cari_lagu_api, name='cari_lagu_api'),
    path('tambah-api/instant/', views.auto_import_instant, name='auto_import_instant'),
    path('tambah-api/preview/', views.preview_import_lagu, name='preview_import_lagu'),
    path('tambah-api/simpan/', views.simpan_lagu_api, name='simpan_lagu_api'),
]
