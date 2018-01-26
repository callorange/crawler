import requests
import os
from bs4 import BeautifulSoup, NavigableString

__all__ = [
    'MelonCrawler',
    'Song'
]


__PATH_MODULE = os.path.abspath(os.path.abspath(__file__))
__ROOT_DIR = os.path.dirname(os.path.dirname(__PATH_MODULE))
__PATH_DATA = os.path.join(__ROOT_DIR, 'data')

class MelonCrawler:

    def get_song_search(self, search_string=''):

        # search_string 체크
        if type(search_string) is not str or search_string == '':
            print('id is not string or empty')
            return None

        # 검색 결과 받기
        # http://www.melon.com/search/song/index.htm?q=up&section=&searchGnbYn=Y&kkoSpl=N&kkoDpType=&ipath=srch_form
        melon_url = 'http://www.melon.com/search/song/index.htm'
        melon_param = {'q': search_string}
        melon_headers = {'user-agent': 'my-app/0.0.1'}
        response = requests.get(melon_url, params=melon_param, headers=melon_headers)
        if len(response.text) < 10:
            print('서버의 응답내용이 잘못되었습니다.')
            return None

        # 파싱
        soup = BeautifulSoup(response.text, 'lxml')

        songs = soup.find('form', id='frm_defaultList').tbody.find_all('tr')

        info_list = []
        for song in songs:
            song_info = song.find_all('td')

            song_id = song_info[0].find('input')['value']
            song_rank = song_info[1].text.strip()
            song_title = song_info[2].find('a', class_='fc_gray').text.strip()
            song_artists = song_info[3].find('div', id='artistName').find_all(['a'], recursive=False)
            song_artist = []
            for artist in song_artists:
                if artist:
                    song_artist.append(artist.text.strip())
            if len(artist) == 0:
                song_artist.append('Various Artist')
            song_album = song_info[4].text.strip()

            s = Song(song_id, song_title, song_artist, song_album)
            info_list.append(s)

        return info_list


class Song:
    def __init__(self, song_id, title='', artist='', album=''):
        self.song_id = song_id
        self.title = title
        self.artist = artist
        self.album = album

        self._release_date = None
        self._lyrics = None
        self._genre = None
        self._producers = None

    def __str__(self):
        return f'{self.title} (아티스트: {self.artist}, 앨범: {self.album})'

    def get_song_detail(self, song_id, refresh=False):
        """멜론에서 곡 상세정보를 가져온다

        Args:
            song_id (str): 노래 ID
            refresh (bool): 노래 정보를 새로 가져 옴. 기본 False

        Returns:
            dict: 노래 정보 딕셔너리

        Example:
            >>> self.get_song_detail('333333')
            {...}
        """

        # 경로 설정
        path_file = os.path.join(PATH_DATA, f'{song_id}.html')

        # 저장 폴더 만들기
        # if os.path.exists(path_data) is False:
        #     os.mkdir(path_data)
        os.makedirs(PATH_DATA, mode=0o777, exist_ok=True)

        # 파일 저장 - 파일이 없거나 refresh가 True 일때
        if os.path.exists(path_file) is False or refresh:
            melon_url = 'http://www.melon.com/song/detail.htm'
            melon_param = {'songId': song_id}
            melon_headers = {'user-agent': 'my-app/0.0.2'}
            response = requests.get(melon_url, params=melon_param, headers=melon_headers)
            if len(response.text) > 10:
                with open(path_file, 'wt', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                print('서버의 응답내용이 잘못되었습니다.')
                return None

        # 파일 불러오기
        source = open(path_file, 'rt', encoding='utf-8').read()

        # 파싱
        soup = BeautifulSoup(source, 'lxml')

        # 곡정보 가져오기
        song_detail = {}

        song_info_area = soup.find('div', id='conts_section')
        self.title = song_info_area.find('div', class_='song_name').strong.next_sibling.strip()
        self.artist = song_info_area.find('div', class_='artist').text.strip(),

        if song_info_area.find('div', class_='lyric', id='d_video_summary'):
            self._lyrics = "\n".join(
                [item.strip() for item in song_info_area.find('div', class_='lyric', id='d_video_summary').contents if
                 type(item) is NavigableString])
        else:
            self._lyrics = ''


        song_album_info = song_info_area.find('div', class_='meta').find('dl', class_='list')
        song_album_key = song_album_info.find_all('dt')
        song_album_value = song_album_info.find_all('dd')

        for album_key, album_value in list(zip(song_album_key, song_album_value)):
            song_detail[album_key.text.strip()] = album_value.text.strip()
        # {'앨범': '빨간 맛', '발매일': '2017.07.20', '장르': 'New Age', 'FLAC': 'Flac 16bit'}

        self.album = song_detail['앨범']
        self._release_date = song_detail['발매일']
        self._genre = song_detail['장르']
        # song_detail.update({
        #     'album_title': song_album_info[0].text.strip(),
        #     'album_date': song_album_info[1].text.strip(),
        #     'album_genre': song_album_info[2].text.strip(),
        #     'alubm_bitrate': song_album_info[3].text.strip()
        # })

        song_artist_info = song_info_area.find('ul', class_='list_person')
        song_detail_producer = {}
        if song_artist_info:
            for item in song_artist_info.find_all('li'):
                song_artist = item.get_text(',', strip=True).split(',')
                if song_artist[1] in song_detail_producer:
                    song_detail_producer[song_artist[1]] = song_detail_producer[song_artist[1]] + [song_artist[0]]
                else:
                    song_detail_producer[song_artist[1]] = [song_artist[0]]
        # {'작사': ['kenzie'], '작곡': ['Daniel Caesar', 'Ludwig Lindell'], '편곡': ['Caesar & Loui']}
        # print(song_detail_producer)
        self._producers = song_detail_producer

    @property
    def lyrics(self):
        if self._lyrics:
            return self._lyrics
        else:
            self.get_song_detail(self.song_id)
            return self._lyrics