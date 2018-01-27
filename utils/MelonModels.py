import os
import requests
import re
from bs4 import BeautifulSoup, NavigableString

__all__ = [
    'Song',
    'Artist'
]

_PATH_MODULE = os.path.abspath(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(os.path.dirname(_PATH_MODULE))
_PATH_DATA = os.path.join(_ROOT_DIR, 'data')


class Artist:
    """가수 정보 클래스"""

    def __init__(self, artist_id='', name='', country='', sex='', act_type='', genre=[]):
        """가수 정보를 생성한다

        Args:
            artist_id(str): 고유번호
            name(str): 이름
            country(str): 소속국가
            sex(str): 성별
            act_type(str): 활동유형(그룹/솔로)
            genre(list): 활동장르
        """
        self.artist_id = artist_id
        self.name = name
        self.country = country
        self.sex = sex
        self.act_type = act_type
        self.genre = genre

        self._member = ''
        self._debut = ''
        self._debut_title = ''
        self._agency = ''
        self._awards = ''
        self._intro = ''
        self._songs = ''

    def __str__(self):
        return f'{self.name} ( 활동:{self.country}/{self.sex}/{self.act_type} 장르:{self.genre} )'

    def refresh(self):
        """아티스트 정보 업데이트"""
        self.get_artist_detail(self.artist_id,True)

    def get_artist_detail(self, artist_id, refresh=False):
        """멜론에서 아티스트 상세정보를 가져온다

        Args:
            artist_id (str): 아티스트 ID
            refresh (bool): 아티스트 정보를 새로 가져 옴. 기본 False

        Returns:
            dict: 아티스트 정보 딕셔너리

        Example:
            >>> Artist.get_artist_detail('333333')
            {...}
        """

        # 경로 설정
        path_file = os.path.join(_PATH_DATA, f'Artist_{artist_id}.html')
        path_file_song = os.path.join(_PATH_DATA, f'Artist_{artist_id}_Songs.html')

        # 저장 폴더 만들기
        # if os.path.exists(path_data) is False:
        #     os.mkdir(path_data)
        os.makedirs(_PATH_DATA, mode=0o777, exist_ok=True)

        # 파일 저장 - 파일이 없거나 refresh가 True 일때
        if os.path.exists(path_file) is False or refresh:
            melon_url = 'http://www.melon.com/artist/detail.htm'
            melon_param = {'artistId': artist_id}
            melon_headers = {'user-agent': 'my-app/0.0.2'}
            response = requests.get(melon_url, params=melon_param, headers=melon_headers)
            if len(response.text) > 10:
                with open(path_file, 'wt', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                print('서버의 응답내용이 잘못되었습니다.')
                return None

        if os.path.exists(path_file_song) is False or refresh:
            melon_url = 'http://www.melon.com/artist/song.htm'
            melon_param = {'artistId': artist_id}
            melon_headers = {'user-agent': 'my-app/0.0.2'}
            response = requests.get(melon_url, params=melon_param, headers=melon_headers)
            if len(response.text) > 10:
                with open(path_file_song, 'wt', encoding='utf-8') as f:
                    f.write(response.text)
            else:
                print('서버의 응답내용이 잘못되었습니다.')
                return None

        # 파일 불러오기
        source = open(path_file, 'rt', encoding='utf-8').read()
        source_song = open(path_file_song, 'rt', encoding='utf-8').read()

        # 파싱
        soup = BeautifulSoup(source, 'lxml')
        soup_song = BeautifulSoup(source_song, 'lxml')

        # 아티스트 기본 정보
        info01 = soup.find('div', id='d_artist_award')
        info01 = info01.find_all('dd')
        a_awards = []
        if info01 and len(info01) > 0:
            a_awards_list = [ award.get_text(strip=True).split('|') for award in info01 ]
            for a_awards_item in a_awards_list:
                a_awards.append({'award_title':a_awards_item[0], 'award_content':a_awards_item[1]})

        info02 = soup.find('div', id='d_artist_intro')
        if info02:
            a_intro = "\n".join(
                [item.strip() for item in info02.contents if type(item) is NavigableString])
        else:
            a_intro = ''

        info03 = soup.find('div', class_='section_atistinfo03').find('dl', class_='list_define')
        info03_key = info03.find_all('dt')
        info03_value = info03.find_all('dd')
        info03_dict = {}
        for key, value in zip(info03_key, info03_value):
            info03_dict[key.text.strip()] = value.text.strip()

        info04 = soup.find('div', class_='debutsong_info').a
        debut_title_id = re.search( r"Detail\(\'(.*?)\'\)", info04["href"].strip() ).group(1)
        debut_title_name = info04["title"].strip()

        info05 = soup.find('ul', class_='d_artist_list').find_all('a', class_='thumb')

        info06 = soup.find('div', class_='section_atistinfo04').find('dt').text.strip()

        a_song_list = []
        songs = soup_song.find('form', id='frm').tbody.find_all('tr')
        for song in songs:
            song_info = song.find_all('td')

            song_id = song_info[0].find('input')['value']
            # song_rank = song_info[1].text.strip()
            song_title = song_info[2].find('a', class_='fc_gray').text.strip()
            song_artists = song_info[3].find('div', id='artistName').find(class_='checkEllipsis')
            if len(song_artists.find_all('a')) > 1:
                song_artists = [ artist.text for artist in song_artists.find_all('a')]
            else:
                song_artists = [song_artists.text]
            song_album = song_info[4].text.strip()

            a_song_list.append( Song(song_id, song_title, song_artists, song_album) )

        self.country = info06
        self.sex = info03_dict["유형"].split('|')[1].strip()
        self.act_type = info03_dict["유형"].split('|')[0].strip()
        self.genre = [ g.strip() for g in info03_dict["장르"].split(',') ]

        self._member = [mem['title'].strip() for mem in info05]
        self._debut = info03_dict["데뷔"]
        self._debut_title = Song(debut_title_id, debut_title_name, self.name, '' )
        self._debut_title.refresh()
        self._agency = info03_dict["소속사명"]
        self._awards = a_awards
        self._intro = a_intro
        self._songs = a_song_list

    @property
    def member(self):
        if self._member:
            return self._member
        else:
            self.get_artist_detail(self.artist_id)
            return self._member

    @property
    def debut(self):
        if self._debut:
            return self._debut
        else:
            self.get_artist_detail(self.artist_id)
            return self._debut

    @property
    def debut_title(self):
        if self._debut_title:
            return self._debut_title
        else:
            self.get_artist_detail(self.artist_id)
            return self._debut_title

    @property
    def agency(self):
        if self._agency:
            return self._agency
        else:
            self.get_artist_detail(self.artist_id)
            return self._agency

    @property
    def awards(self):
        if self._awards:
            return self._awards
        else:
            self.get_artist_detail(self.artist_id)
            return self._awards

    @property
    def intro(self):
        if self._intro:
            return self._intro
        else:
            self.get_artist_detail(self.artist_id)
            return self._intro

    @property
    def songs(self):
        if self._songs:
            return self._songs
        else:
            self.get_artist_detail(self.artist_id)
            return self._songs

class Song:
    """곡 정보 클래스"""

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

    def refresh(self):
        """곡 정보 업데이트"""
        self.get_song_detail(self.song_id,True)

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
        path_file = os.path.join(_PATH_DATA, f'Song_{song_id}.html')

        # 저장 폴더 만들기
        # if os.path.exists(path_data) is False:
        #     os.mkdir(path_data)
        os.makedirs(_PATH_DATA, mode=0o777, exist_ok=True)

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
        song_info_area = soup.find('div', id='conts_section')
        s_title = song_info_area.find('div', class_='song_name').strong.next_sibling.strip()
        s_artist = song_info_area.find('div', class_='artist').text.strip(),

        if song_info_area.find('div', class_='lyric', id='d_video_summary'):
            s_lyrics = "\n".join(
                [item.strip() for item in song_info_area.find('div', class_='lyric', id='d_video_summary').contents if
                 type(item) is NavigableString])
        else:
            s_lyrics = ''


        song_album_info = song_info_area.find('div', class_='meta').find('dl', class_='list')
        song_album_key = song_album_info.find_all('dt')
        song_album_value = song_album_info.find_all('dd')

        song_detail = {}
        for album_key, album_value in list(zip(song_album_key, song_album_value)):
            song_detail[album_key.text.strip()] = album_value.text.strip()
        s_release_date = song_detail['발매일']
        s_genre = song_detail['장르']
        s_album = song_detail['앨범']
        # {'앨범': '빨간 맛', '발매일': '2017.07.20', '장르': 'New Age', 'FLAC': 'Flac 16bit'}
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
        self.title = s_title
        self.artist = s_artist
        self.album = s_album

        self._release_date = s_release_date
        self._lyrics = s_lyrics
        self._genre = s_genre
        self._producers = song_detail_producer

    @property
    def release_date(self):
        if self._release_date:
            return self._release_date
        else:
            self.get_song_detail(self.song_id)
            return self._release_date

    @property
    def lyrics(self):
        if self._lyrics:
            return self._lyrics
        else:
            self.get_song_detail(self.song_id)
            return self._lyrics

    @property
    def genre(self):
        if self._genre:
            return self._genre
        else:
            self.get_song_detail(self.song_id)
            return self._genre

    @property
    def producers(self):
        if self._producers:
            return self._producers
        else:
            self.get_song_detail(self.song_id)
            return self._producers