from utils import Melon

if __name__ == '__main__':
    # q = input('Search Song:')
    # songs = Melon.MelonCrawler().get_song_search(q)

    # q = input('Search Artist:')
    q = "카라"
    artists = Melon.MelonCrawler().get_artist_search(q)

    for a in artists:
        print(a)
        # print(a.member)
        # print(a.debut)
        # print(a.debut_title)
        # print(a.agency)
        # print(a.awards)
        # print(a.intro)
        # for song in a.songs:
        #     print(f'Song: {song}, Artist:{song.artist}')
        # break;