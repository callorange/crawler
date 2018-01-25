import re
import requests

__all__ = (
    'get_tag_attr',
    'get_tag',
    'get_tag_cont',
)

def save_melon_chart(file_name='melon.txt'):
    # response = requests.get('http://www.melon.com/chart/index.htm')
    # print(response.text)

    # response = requests.get('http://www.melon.com/chart/index.htm', headers={'user-agent': 'my-app/0.0.1'})
    # print(response.text)

    response = requests.get('https://www.melon.com/chart/index.htm',)
    h_body = response.text

    with open(file_name, 'wt', encoding='utf-8') as f:
        f.write(h_body)

def get_tag_attr(attr,tag,search_string):
    exp = re.compile(r"<"+tag+".*?"+attr+"=\"(.*?)\".*?>", re.DOTALL)
    result = exp.search(search_string)
    if result is not None:
        return result.group(1)
    return ''


def get_tag(tag, search_string, class_=None):
    exp = re.compile(r".*?(<{tag}.*?{class_}.*?>.*?</{tag}>)".format(
        tag=tag,
        class_=f'class=".*{class_}.*?"' if class_ else ''
    ), re.DOTALL)
    result = exp.search(search_string)
    if result:
        return result.group(1)
    return ''


def get_tag_cont(search_string):
    exp = re.compile(r"<.*?>(.*?)</.*?>", re.DOTALL)
    result = exp.search(search_string)
    if result:
        result.group(1)
        return get_tag_cont(result.group(1))
    elif re.search(r"[<>]", search_string, re.DOTALL):
        return ''
    return search_string