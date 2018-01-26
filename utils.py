from bs4 import BeautifulSoup, NavigableString
import re
import os
import requests

__all__ = [
    'get_top100_list',
    'get_song_detail'
]

PATH_MODULE = os.path.abspath(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(PATH_MODULE)
PATH_DATA = os.path.join(ROOT_DIR, 'data')

def get_top100_list(top=100, refresh=False):
    """멜론 차트 100위까지 리스트 반환

    Args:
        top (int): 뽑아올 순위. 기본 100. 1~100
        refresh (bool): 멜론 차트를 새로 저장 함. 기본 False

    Returns:
        list: 멜론 차트 정보 리스트. 각 아이템은 딕셔너리

    Example:
        >>> get_top100_list()
        [{
            'RANK': song_rank,
            'TITLE': song_title,
            'ARTIST': song_artist,
            'ALBUM': song_album,
            'IMG': song_img
        }...]
    """

    # top 변수 체크
    if top < 1:
        top = 1
    elif top > 100:
        top = 100

    # 경로 설정
    path_file = os.path.join(PATH_DATA, 'melon.html')

    # 저장 폴더 만들기
    # if os.path.exists(path_data) is False:
    #     os.mkdir(path_data)
    os.makedirs(PATH_DATA, mode=0o777, exist_ok=True)

    # 파일 저장 - 파일이 없거나 refresh가 True 일때
    if os.path.exists(path_file) is False or refresh:
        response = requests.get('https://www.melon.com/chart/index.htm')
        with open(path_file, 'wt', encoding='utf-8') as f:
            f.write(response.text)

    # 파일 불러오기
    source = open(path_file, 'rt', encoding='utf-8').read()

    # 파싱
    soup = BeautifulSoup(source, 'lxml')

    # 리스트 만들기
    song_list = []
    for tr in soup.find_all('tr', class_=['lst50', 'lst100'], limit=top):
        song_rank = tr.find('span', class_='rank').text
        song_title = tr.find('div', class_='rank01').find('a').text
        song_artist = tr.find('div', class_='rank02').find('a').text
        song_album = tr.find('div', class_='rank03').find('a').text
        # song_img = tr.find('a', class_='image_typeAll').find('img').get('src')
        song_img = re.search(r"(.*?)/melon/resize", str(tr.find('a', class_='image_typeAll').find('img').get('src')), re.DOTALL).group(1)
        song_id = tr.get('data-song-no')

        song_list.append(
            {
                'RANK': song_rank,
                'TITLE': song_title,
                'ARTIST': song_artist,
                'ALBUM': song_album,
                'IMG': song_img,
                'ID': song_id
            }
        )

    return song_list


def get_song_detail(song_id, refresh=False):
    """멜론에서 곡 상세정보를 가져온다

    Args:
        song_id (str): 노래 ID
        refresh (bool): 노래 정보를 새로 가져 옴. 기본 False

    Returns:
        dict: 노래 정보 딕셔너리

    Example:
        >>> get_song_detail('333333')
        {...}
    """
    # song_id 체크
    if type(song_id) is not str:
        print('id is not string')
        return {}

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
        melon_headers = {'user-agent': 'my-app/0.0.1'}
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

    song_detail.update({
        'title': song_info_area.find('div', class_='song_name').strong.next_sibling.strip(),
        'singer': song_info_area.find('div', class_='artist').text.strip(),
        'lyric': "\n".join([item.strip() for item in song_info_area.find('div', class_='lyric', id='d_video_summary').contents if type(item) is NavigableString])
    })

    song_album_info = song_info_area.find('div', class_='meta').find('dl', class_='list')
    song_album_key = song_album_info.find_all('dt')
    song_album_value = song_album_info.find_all('dd')

    for album_key, album_value in list(zip(song_album_key, song_album_value)):
        song_detail[album_key.text.strip()] = album_value.text.strip()

    # song_detail.update({
    #     'album_title': song_album_info[0].text.strip(),
    #     'album_date': song_album_info[1].text.strip(),
    #     'album_genre': song_album_info[2].text.strip(),
    #     'alubm_bitrate': song_album_info[3].text.strip()
    # })

    song_artist_info = song_info_area.find('ul', class_='list_person').find_all('li')
    song_detail_producer = {}
    for item in song_artist_info:
        song_artist = item.get_text(',', strip=True).split(',')
        if song_artist[1] in song_detail_producer:
            song_detail_producer[song_artist[1]] = song_detail_producer[song_artist[1]] + [song_artist[0]]
        else:
            song_detail_producer[song_artist[1]] = [song_artist[0]]

    song_detail['producer'] = song_detail_producer
    return song_detail


