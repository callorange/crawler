from utils import models

if __name__ == '__main__':
    for song in models.MelonCrawler().get_song_search('빨간맛'):
        print(song.album)
        break
