"""
Layanan integrasi API untuk pencarian lagu dan konten terkait (Deezer, iTunes,
LRCLIB, YouTube, dan Gemini). Hasil pencarian lagu ditampilkan langsung;
modul ini tidak mengimpor lagu ke katalog lokal.
"""

import json
import os
import re
import urllib.parse
import urllib.request


def _gemini_output_text(data):
    """Read text output from Gemini's Interactions REST response."""
    if data.get('output_text'):
        return data['output_text']
    for step in data.get('steps', []):
        if step.get('type') == 'model_output':
            parts = step.get('content', [])
            return ' '.join(part.get('text', '') for part in parts if part.get('type') == 'text').strip()
    return ''


def search_tracks_api(query, limit=8):
    """
    Mencari lagu dari Deezer API (database global puluhan juta lagu).
    Fallback ke iTunes Search API jika Deezer tidak merespons.
    """
    results = []
    
    # 1. Coba Deezer API
    try:
        encoded_query = urllib.parse.quote(query)
        url = f"https://api.deezer.com/search?q={encoded_query}&limit={limit}"
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        )
        with urllib.request.urlopen(req, timeout=8) as response:
            data = json.loads(response.read().decode('utf-8'))
            for item in data.get('data', []):
                results.append({
                    'source': 'Deezer',
                    'judul': item.get('title_short') or item.get('title'),
                    'artis': item.get('artist', {}).get('name', 'Unknown Artist'),
                    'album': item.get('album', {}).get('title', ''),
                    'cover_url': item.get('album', {}).get('cover_medium') or item.get('album', {}).get('cover_big', ''),
                    'preview_url': item.get('preview', ''),
                    'duration': item.get('duration', 0),
                    'external_id': str(item.get('id', '')),
                    'track_url': item.get('link', ''),
                })
    except Exception as e:
        print(f"Error fetching from Deezer: {e}")

    # 2. Fallback ke iTunes jika Deezer kosong
    if not results:
        try:
            encoded_query = urllib.parse.quote(query)
            url = f"https://itunes.apple.com/search?term={encoded_query}&entity=song&limit={limit}"
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            )
            with urllib.request.urlopen(req, timeout=8) as response:
                data = json.loads(response.read().decode('utf-8'))
                for item in data.get('results', []):
                    # Ubah cover 100x100 jadi 300x300
                    cover = item.get('artworkUrl100', '').replace('100x100bb', '300x300bb')
                    results.append({
                        'source': 'iTunes',
                        'judul': item.get('trackName', ''),
                        'artis': item.get('artistName', ''),
                        'album': item.get('collectionName', ''),
                        'cover_url': cover,
                        'preview_url': item.get('previewUrl', ''),
                        'duration': int(item.get('trackTimeMillis', 0) / 1000),
                        'external_id': str(item.get('trackId', '')),
                        'track_url': item.get('trackViewUrl', ''),
                    })
        except Exception as e:
            print(f"Error fetching from iTunes: {e}")

    return results


def generate_search_keywords(prompt):
    """Turn a natural-language music request into a short Deezer query.

    Gemini is optional. An empty result lets the caller use its local fallback.
    """
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key or not prompt:
        return ''

    model = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash').strip()
    url = 'https://generativelanguage.googleapis.com/v1beta/interactions'
    body = {
        'model': model,
        'input': (
            'Convert this Indonesian music request into a short music search query '
            'that works well on Deezer. Return only 2 to 6 keywords, no explanation. '
            'Preserve requested language, activity, mood, and genre when useful. '
            f'Request: {prompt[:500]}'
        ),
    }
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode('utf-8'),
        headers={
            'Content-Type': 'application/json',
            'x-goog-api-key': api_key,
        },
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode('utf-8'))
        text = _gemini_output_text(data)
        query = re.sub(r'[\r\n"`]+', ' ', text).strip(' .')
        return query[:120]
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return ''


def generate_song_motivation(judul, artis, album=''):
    """Classify a selected track and write a short original encouragement."""
    api_key = os.environ.get('GEMINI_API_KEY', '').strip()
    if not api_key:
        return None

    model = os.environ.get('GEMINI_MODEL', 'gemini-3.8-flash').strip()
    url = 'https://generativelanguage.googleapis.com/v1beta/interactions'
    prompt = (
        'Classify this music track as one of: Senang, Sedih, Santai, Semangat, Romantis, Fokus, '
        'Nostalgia, Intens. Write one or two original Indonesian encouragement sentences that fit '
        'that type. Do not quote song lyrics or attribute the words to a real person. '
        'Reply exactly in two lines: TYPE: <type> and MESSAGE: <message>. '
        f'Track title: {judul[:200]}\nArtist: {artis[:200]}\nAlbum: {album[:200]}'
    )
    body = {'model': model, 'input': prompt}
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode('utf-8'),
        headers={'Content-Type': 'application/json', 'x-goog-api-key': api_key},
        method='POST',
    )
    try:
        with urllib.request.urlopen(request, timeout=12) as response:
            data = json.loads(response.read().decode('utf-8'))
        text = _gemini_output_text(data)
        type_match = re.search(r'^\s*TYPE:\s*(.+?)\s*$', text, re.I | re.M)
        message_match = re.search(r'^\s*MESSAGE:\s*(.+?)\s*$', text, re.I | re.M)
        if not type_match or not message_match:
            return None
        song_type = type_match.group(1).strip()[:40]
        message = re.sub(r'[\r\n"`]+', ' ', message_match.group(1)).strip()[:320]
        if not message:
            return None
        return {'song_type': song_type, 'message': message}
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return None


def fetch_lyrics_quote(judul, artis):
    """Return at most two short lines and an LRCLIB source URL."""
    query = urllib.parse.quote(f'{artis} {judul}')
    source_url = f'https://lrclib.net/search/{query}'
    lyrics = ''
    track_id = ''
    try:
        q_artist = urllib.parse.quote(artis)
        q_track = urllib.parse.quote(judul)
        url = f'https://lrclib.net/api/get?artist_name={q_artist}&track_name={q_track}'
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'Moodify/1.0 (music discovery app)'},
        )
        with urllib.request.urlopen(req, timeout=6) as response:
            data = json.loads(response.read().decode('utf-8'))
        lyrics = clean_lyrics(data.get('plainLyrics', ''))
        track_id = str(data.get('id', ''))
    except (OSError, ValueError, TypeError):
        pass

    if not lyrics:
        try:
            url = f'https://lrclib.net/api/search?q={query}'
            req = urllib.request.Request(
                url,
                headers={'User-Agent': 'Moodify/1.0 (music discovery app)'},
            )
            with urllib.request.urlopen(req, timeout=6) as response:
                results = json.loads(response.read().decode('utf-8'))
            if isinstance(results, list):
                for item in results:
                    candidate = clean_lyrics(item.get('plainLyrics', ''))
                    if candidate:
                        lyrics = candidate
                        track_id = str(item.get('id', ''))
                        break
        except (OSError, ValueError, TypeError):
            pass

    lines = [line.strip() for line in lyrics.splitlines() if line.strip()]
    if not lines:
        return {'quote': '', 'source_url': source_url}

    # Prefer short, meaningful lines and never send the full lyrics to the page.
    candidates = [line for line in lines if 12 <= len(line) <= 110]
    chosen = candidates[:2] if candidates else lines[:1]
    quote = '\n'.join(line[:110] for line in chosen)
    if track_id:
        source_url = f'https://lrclib.net/tracks/{urllib.parse.quote(track_id)}'
    return {'quote': quote, 'source_url': source_url}


def clean_lyrics(text):
    """Membersihkan format lirik."""
    if not text:
        return ""
    # Hapus tag timestamp [00:12.34] jika ada
    text = re.sub(r'\[\d{2}:\d{2}(?:\.\d{2,3})?\]', '', text)
    # Hapus baris kosong berlebihan
    lines = [line.strip() for line in text.split('\n')]
    cleaned = []
    prev_blank = False
    for line in lines:
        if not line:
            if not prev_blank:
                cleaned.append('')
                prev_blank = True
        else:
            cleaned.append(line)
            prev_blank = False
    return '\n'.join(cleaned).strip()


