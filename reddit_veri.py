import requests
from bs4 import BeautifulSoup
import time
import os
import csv
import re
import random
import pathlib

GENIUS_API_TOKEN = '06erJrobbb8HTiX1exQ_J8ptFsDX8WVj_86o-iy9LN1LqzvzIfL9MP1A0ATpg1UY'
HEADERS = {'Authorization': f'Bearer {GENIUS_API_TOKEN}'}
SEARCH_URL = "https://api.genius.com/search"

MOOD_TERMS = {
    'öfke': ['anger', 'furious', 'hate', 'rage', 'mad', 'revenge'],
    'mutluluk': ['happy', 'joy', 'celebration', 'cheerful', 'smile'],
    'sevgi': ['love', 'romantic', 'affection', 'crush', 'heart'],
    'yalnızlık': ['lonely', 'alone', 'missing you', 'emptiness', 'sadness'],
    'üzüntü': ['sad', 'depression', 'crying', 'grief', 'broken heart']
}

KÜFÜRLER = [
    'fuck', 'shit', 'bitch', 'asshole', 'damn', 'motherfucker', 'nigga', 'faggot', 'pussy', 'dick', 'cock'
]

def temizle_lyrics(lyrics):
    if not lyrics:
        return None

    if any(küfür in lyrics.lower() for küfür in KÜFÜRLER):
        return None

    lyrics = re.sub(r'http\S+', '', lyrics)
    lyrics = re.sub(r'\[.*?\]', '', lyrics)
    lyrics = re.sub(r'[^\w\s,.!?\'"]+', '', lyrics)
    lyrics = re.sub(r'\s+', ' ', lyrics).strip()

    if len(lyrics) < 200:
        return None

    return lyrics

def get_song_lyrics(song_url):
    try:
        page = requests.get(song_url)
        html = BeautifulSoup(page.text, "html.parser")
        lyrics_divs = html.find_all("div", attrs={"data-lyrics-container": "true"})
        lyrics = "\n".join([div.get_text(separator="\n") for div in lyrics_divs])
        return temizle_lyrics(lyrics)
    except Exception as e:
        print(f"Lyrics çekme hatası: {e}")
        return None

def get_desktop_path():
    home = pathlib.Path.home()

    for folder_name in ['Desktop', 'Masaüstü']:
        desktop_path = home / folder_name
        if desktop_path.exists():
            return str(desktop_path)
    return str(home)  

def load_existing_titles(filename):
    existing_titles = set()
    if os.path.exists(filename):
        with open(filename, mode='r', encoding='utf-8', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                existing_titles.add((row['title'], row['artist']))
    return existing_titles

def search_songs_by_mood(mood, max_songs=500):
    desktop_path = get_desktop_path()
    filename = os.path.join(desktop_path, f"{mood}_songs.csv")

    existing = load_existing_titles(filename)
    print(f"{len(existing)} şarkı zaten kayıtlı, hedef: {max_songs}")

    songs_collected = len(existing)

    with open(filename, mode='a', encoding='utf-8', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['title', 'artist', 'mood', 'lyrics'])
        if songs_collected == 0:
            writer.writeheader()

        mood_terms = MOOD_TERMS.get(mood, [mood])
        random.shuffle(mood_terms)

        while songs_collected < max_songs:
            for term in mood_terms:
                page = 1
                while songs_collected < max_songs:
                    print(f"Aranıyor: '{term}' - Sayfa {page}")
                    params = {'q': term, 'page': page}
                    try:
                        response = requests.get(SEARCH_URL, headers=HEADERS, params=params, timeout=20)
                        data = response.json()
                    except Exception as e:
                        print(f"API hatası: {e}")
                        break

                    hits = data.get('response', {}).get('hits', [])
                    if not hits:
                        break

                    for hit in hits:
                        if songs_collected >= max_songs:
                            break

                        title = hit['result']['title']
                        artist = hit['result']['primary_artist']['name']
                        url = hit['result']['url']

                        if (title, artist) in existing:
                            print(f"Zaten var: {title} - {artist}")
                            continue

                        lyrics = get_song_lyrics(url)
                        if lyrics:
                            writer.writerow({
                                'title': title,
                                'artist': artist,
                                'mood': mood,
                                'lyrics': lyrics
                            })
                            existing.add((title, artist))
                            songs_collected += 1
                            print(f"[{songs_collected}/{max_songs}] ✅ {title} - {artist}")
                        else:
                            print(f"⛔ Temizlenemedi: {title}")

                        time.sleep(0.5)
                    page += 1

                if songs_collected >= max_songs:
                    break

    print(f"✅ {mood.upper()} için {songs_collected} temiz şarkı tamamlandı.")

def main():
    moods = ['öfke', 'mutluluk', 'sevgi', 'yalnızlık', 'üzüntü']
    for mood in moods:
        search_songs_by_mood(mood, max_songs=500)

if __name__ == "__main__":
    main()
