import re
import os
from src import api, write_epub
import time
import json
from tqdm import tqdm
import config
from DownloadKit import DownloadKit
from spider_toolbox import file_tools

temp_img_dir = config.temp_img_dir
epub_save_dir = config.save_dir
total_word = 0


def parser_local_chapter_info():
    base_path = 'choose_chapter_info.json'
    local_path = r'D:\pythoncode\代码\爬\Bilinoval_DL\choose_chapter_info.json'
    with open(local_path, 'r', encoding='utf-8') as f:
        file_read = f.read()
        chapter_info = json.loads(file_read)
    return chapter_info


def down_img(img_url, name):
    # img = api.get_img_content(url)
    down_kit = DownloadKit()
    headers_ = {
        'authority': 'img3.readpai.com',
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.linovelib.com/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    down_kit.add(file_url=img_url,
                 goal_path=temp_img_dir,
                 rename=f'{name}',
                 suffix='jpg',
                 headers=headers_)
    # with open(f'{temp_img_dir}/{name}.jpg', 'wb') as f:
    #     f.write(img)
    # print(f'temp/{name}.jpg')


def format_number_with_units(number: int):
    if number < 1000:
        return str(number)
    elif number < 10000:
        return f"{number / 1000:.1f}千"
    else:
        return f"{number / 10000:.1f}万"


def parser(chapter_info):
    global total_word
    chapter_part_chapter_text = {}
    img_id = 0
    for i, part in enumerate(chapter_info['part']):
        chapter_name_text = []
        pbar = tqdm(total=len(chapter_info['chapter_name'][i]), desc=part)
        for chapter_name, chapter_url in zip(chapter_info['chapter_name'][i], chapter_info['chapter_url'][i]):
            pbar.update()
            if chapter_name.split('-')[-1] == '插图':
                continue
            text, img_urls = api.dp_get_chapter_text(chapter_url)  # 一话所有的文本和图片链接
            for img_url in img_urls:
                text = text.replace(img_url, f'{temp_img_dir}/{img_id}.jpg')
                down_img(img_url, img_id)
                if '/images/sloading.svg' in text:
                    text = re.sub(r'<img src="[^"]*" data-src="([^"]*)"[^>]*>',
                                  r'<img src="\1" data-src="\1" class="imagecontent lazyload"/>', text)
                img_id += 1
                time.sleep(0.5)
            chapter_name_text.append([chapter_name, text])
            total_word += len(text)
        time.sleep(3)
        chapter_part_chapter_text[part] = chapter_name_text
    # print(chapter_part_chapter_text)
    return chapter_part_chapter_text


def choose_down_chapter(chapter_info):
    for i, part_name in enumerate(chapter_info['part'], start=1):
        print(f'{i}\t{part_name}')
    start_ = input('输入开始序号(0为全部)>>>')
    if start_.isdigit():
        start_ = int(start_)
    if start_ != 0:
        end_ = input('输入结束序号>>>')
        if end_.isdigit():
            start_, end_ = int(start_), int(end_)
            choose_chapter_info = {'part': chapter_info['part'][start_ - 1:end_],
                                   'chapter_name': chapter_info['chapter_name'][start_ - 1:end_],
                                   'chapter_url': chapter_info['chapter_url'][start_ - 1:end_]}
        else:
            raise '请输入正确数字'
    elif start_ == 0:
        start_, end_ = 0, -1
        choose_chapter_info = chapter_info
    else:
        raise '请输入正确数字'
    return (start_, end_), choose_chapter_info


def set_start_end(debug: bool = False):
    start_chapter_url = input('输入开始>>>')
    end_chapter_url = input('输入结束(回车全下)>>>')
    if end_chapter_url.replace(' ', '') == '':
        end_chapter_url = False

    noval_id = api.get_noval_id(start_chapter_url)
    noval_info = api.get_noval_info(noval_id)
    print(noval_info['book_name'])
    if debug:
        down_chapter_info = parser_local_chapter_info()
    else:
        down_chapter_info = api.while_get_chapter_name_url(start_url=start_chapter_url, end_url=end_chapter_url)
    return (start_chapter_url, end_chapter_url), noval_info, down_chapter_info


def main():
    (start, end), noval_info, choose_chapter_info = set_start_end(debug=False)

    with open('choose_chapter_info.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(choose_chapter_info, ensure_ascii=False))

    api.init_chrome()
    epub_text = parser(choose_chapter_info)

    title = noval_info['book_name']
    author = noval_info['author']
    cover_content = api.get_img_content(noval_info['cover_url'])
    description = noval_info['description']
    write_epub.write_epub(title,
                          author,
                          epub_text,
                          description,
                          'cover',
                          cover_content,
                          temp_img_dir,
                          epub_save_dir)
    file_tools.del_dir(temp_img_dir, mode=2)

    print(f'\n字数:{format_number_with_units(total_word)}\n')


if __name__ == '__main__':
    # url = 'https://www.linovelib.com/novel/3805.html'
    url = 'https://www.linovelib.com/novel/3080.html'
    # url = 'https://www.linovelib.com/novel/2914.html'
    main()
