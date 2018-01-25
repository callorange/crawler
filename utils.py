from bs4 import BeautifulSoup
import re
import os
import requests

__all__ = [
    'get_top100_list'
]


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
    root_dir = os.path.dirname(os.path.abspath(__name__))
    path_data = os.path.join(root_dir, 'data')
    path_file = os.path.join(path_data, 'melon.html')

    # 저장 폴더 만들기
    # if os.path.exists(path_data) is False:
    #     os.mkdir(path_data)
    os.makedirs(path_data, mode=0o777, exist_ok=True)

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

        song_list.append(
            {
                'RANK': song_rank,
                'TITLE': song_title,
                'ARTIST': song_artist,
                'ALBUM': song_album,
                'IMG': song_img
            }
        )

    return song_list
