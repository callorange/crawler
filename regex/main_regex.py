import re
from regex.utils import *

_READ_FILE_NAME = 'melon.txt'

_RE_TBODY = re.compile(r"<form id=\"frm\".*<tbody>(.*)</tbody", re.DOTALL)
_RE_TR = re.compile(r"<tr class=\"(?:lst50|lst100)\".*?>.*?</tr>", re.DOTALL)
_RE_TD = re.compile(r"<td>.*?</td>", re.DOTALL)
_RE_RANK = re.compile(r"class=\"rank.*?>(.*?)</span>")
_RE_TITLE = re.compile(r"class=['\"]wrap_song_info['\"]>.*?rank01\">.*?playSong\([\"'].*?>([\w\W\s]*?)</a>", re.DOTALL)
_RE_ARTIST = re.compile(r"class=['\"]wrap_song_info['\"]>.*?rank02\">.*?goArtistDetail\([\"'].*?>([\w\W\s]*?)</a>", re.DOTALL)
_RE_IMG = re.compile(r"class=\"image_typeAll\">.*?<img.*?src=\"(.*?)/melon/resize", re.DOTALL)
_RE_ALBUM = re.compile(r"class=['\"]wrap_song_info['\"]>.*?rank03\">.*?goAlbumDetail\([\"'].*?>([\w\W\s]*?)</a>", re.DOTALL)


_SCH_BODY = ''
_SCH_SONG_TABLE = ''
_SCH_SONG_TD = ''
_SCH_SONG_TR = ''

_SCH_RESULT = []

# 멜론 차트를 새로 저장한다.
# import save_melon
# save_melon.save_melon_chart(_READ_FILE_NAME)
# 혹은 이렇게
# from save_melon import *
# save_melon_chart(_READ_FILE_NAME)

# 저장한 차트를 읽어 온다
with open(_READ_FILE_NAME, 'rt', encoding='utf-8') as f:
    _SCH_BODY = f.read()


# 테이블을 찾는다
_SCH_SONG_TABLE = _RE_TBODY.search(_SCH_BODY).group(1)

# TR을 찾는다.
_SCH_SONG_TR = _RE_TR.findall(_SCH_SONG_TABLE)

# TD를 찾는다.
for i, song_tr in enumerate(_SCH_SONG_TR):
    _SCH_SONG_TD = _RE_TD.findall(song_tr)

    # _SCH_SONG_RANK = i
    _SCH_SONG_RANK = _RE_RANK.search(_SCH_SONG_TD[1]).group(1)
    _SCH_SONG_TITLE = _RE_TITLE.search(_SCH_SONG_TD[5]).group(1)
    _SCH_SONG_TITLE = get_tag_cont(_SCH_SONG_TD[5])
    _SCH_SONG_ARTIST = _RE_ARTIST.search(_SCH_SONG_TD[5]).group(1)
    _SCH_SONG_IMG = _RE_IMG.search(_SCH_SONG_TD[3]).group(1)
    _SCH_SONG_ALBUM = _RE_ALBUM.search(_SCH_SONG_TD[6]).group(1)
    _SCH_RESULT.append(
        {
            'RANK': _SCH_SONG_RANK,
            'TITLE': _SCH_SONG_TITLE,
            'ARTIST': _SCH_SONG_ARTIST,
            'ALBUM': _SCH_SONG_ALBUM,
            'IMG': _SCH_SONG_IMG
        }
    )

# 출력
for song_info in _SCH_RESULT:
    print(song_info)

