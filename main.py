from utils import *

song_list = get_top100_list(top=1)

# 출력
# song_id_list = []
# for song_info in song_list:
#     print(song_info)
#     song_id_list.append(song_info['ID'])
#
#
# for song_id in song_id_list:
#     song_detail = get_song_detail(song_id)
#     print(f'----------------------------------\nSong ID: {song_id}\n----------------------------------')
#     for song_key, song_item in song_detail.items():
#         print(f'{song_key}: {song_item}')


search_string = '빨간맛'
print(f'----------------------------------\nSong Search: {search_string}\n----------------------------------')
for song_search in get_song_search(search_string):
    print(song_search)