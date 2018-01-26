from utils import *

song_list = get_top100_list(top=4)

# 출력
song_id_list = []
for song_info in song_list:
    print(song_info)
    song_id_list.append(song_info['ID'])


for song_id in song_id_list:
    song_detail = get_song_detail(song_id)
    print(song_detail)