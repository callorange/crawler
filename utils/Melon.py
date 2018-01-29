import requests
from bs4 import BeautifulSoup
from utils.MelonModels import *

__all__ = [
    'MelonCrawler'
]


class MelonCrawler:
    """멜론에서 음악/가수 검색 결과를 크롤링 한다."""

    def _get_melon_artist_search(self, search_string=''):
        """멜론에서 가수 검색 결과 html text를 반환한다.

        검색 단어가 잘못되었거나 응답내용에 오류가 있을경우 빈 문자열 반환

        Args:
            search_string (str): 검색할 문자열

        Returns:
            str: 검색결과 html text. 오류가 있을경우 ''
        """
        # search_string 체크
        if type(search_string) is not str or search_string == '':
            print('검색단어가 잘못 되었습니다.')
            return ''

        melon_url = 'http://www.melon.com/search/artist/index.htm'
        melon_param = {'q': search_string}
        melon_headers = {'user-agent': 'my-app/0.0.1'}
        response = requests.get(melon_url, params=melon_param, headers=melon_headers)

        if len(response.text) < 10 or response.status_code != 200:
            print('서버의 응답내용이 잘못되었습니다.')
            return ''

        return response.text

    def get_artist_search(self, search_string=''):
        """가수 검색 결과를 파싱하여 Artist 클래스의 리스트를 반환한다.

        Args:
            search_string (str): 검색할 곡명

        Returns:
             list: Artist 클래스 객체를 담은 리스트
        """
        # 검색 결과 받기
        search_result = self._get_melon_artist_search(search_string)
        if search_result == '':
            return []

        # BeautifulSoup 파싱
        soup = BeautifulSoup(search_result, 'lxml')

        # 가수목록
        artist_list = soup.find('div', id='pageList').find_all('li')

        info_list = []
        for artist in artist_list:
            artist_id = artist.select_one('input[name="artistId"]')['value']
            artist_name = artist.find('dt').a.text
            artist_gubun = artist.find('dd', class_='gubun').text.strip().split('/')
            if len(artist_gubun) == 3:
                artist_country = artist_gubun[0]
                artist_sex = artist_gubun[1]
                artist_act_type = artist_gubun[2]
            else:
                artist_country = ''
                artist_sex = ''
                artist_act_type = ''
            artist_genre = artist.find('dd', class_='gnr').div.text.strip().split(',')
            # artist_title_song = artist.find('dd', class_='btn_play').find('span', class_='songname12').text.strip()

            # print(f'{artist_name}')
            # print(f'{artist_gubun}') # ['대한민국', '여성', '그룹']
            # print(f'{artist_genre}')
            # print(f'{artist_title_song}')
            info_list.append(Artist(artist_id, artist_name, artist_country, artist_sex, artist_act_type, artist_genre))

        return info_list

    def _get_melon_song_search(self, search_string=''):
        """멜론에서 노래 검색 결과 html text를 반환한다.

        검색 단어가 잘 못 되었거나 응답내용에 오류가 있을경우 빈 문자열 반환

        Args:
            search_string (str): 검색할 문자열

        Returns:
            str: 검색결과 텍스트. 검색단어 및 오류 발생시 빈 문자열
        """
        # search_string 체크
        if type(search_string) is not str or search_string == '':
            print('검색단어가 잘못 되었습니다.')
            return ''

        melon_url = 'http://www.melon.com/search/song/index.htm'
        melon_param = {'q': search_string}
        melon_headers = {'user-agent': 'my-app/0.0.1'}
        response = requests.get(melon_url, params=melon_param, headers=melon_headers)

        if len(response.text) < 10 or response.status_code != 200:
            print('서버의 응답내용이 잘못되었습니다.')
            return ''

        return response.text

    def get_song_search(self, search_string=''):
        """노래 검색 결과를 파싱하여 Song 클래스의 리스트를 반환한다.

        Args:
            search_string (str): 검색할 곡명

        Returns:
             list: Song 클래스 객체를 담은 리스트
        """
        # 검색 결과 받기
        search_result = self._get_melon_song_search(search_string)
        if search_result == '':
            return []

        # BeautifulSoup 파싱
        soup = BeautifulSoup(search_result, 'lxml')

        songs = soup.find('form', id='frm_defaultList').tbody.find_all('tr')

        info_list = []
        for song in songs:
            song_info = song.find_all('td')

            song_id = song_info[0].find('input')['value']
            # song_rank = song_info[1].text.strip()
            song_title = song_info[2].find('a', class_='fc_gray').text.strip()
            song_artists = song_info[3].find('div', id='artistName').find(class_='checkEllipsisSongdefaultList')
            if len(song_artists.find_all('a')) > 1:
                song_artists = [artist.text for artist in song_artists.find_all('a')]
            else:
                song_artists = [song_artists.text]
            song_album = song_info[4].text.strip()

            info_list.append(Song(song_id, song_title, song_artists, song_album))

        return info_list
