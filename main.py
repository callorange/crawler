from utils import *

song_list = get_top100_list(top=4)

# 출력
song_id_list = []
for song_info in song_list:
    print(song_info)
    song_id_list.append(song_info['ID'])

for id in song_id_list:
    song_detail = get_song_detail(id)
    print('------------------------------')
    for key, value in song_detail.items():
        print(f"{key}: {value}")
