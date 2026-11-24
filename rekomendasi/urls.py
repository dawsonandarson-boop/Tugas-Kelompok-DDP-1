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
]
