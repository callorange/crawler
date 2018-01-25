from utils import *

song_list = get_top100_list(refresh=True)

# 출력
for song_info in song_list:
    print(song_info)

