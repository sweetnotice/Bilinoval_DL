from src import api, write_epub
import time
from spider_toolbox import file_tools
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm


def down_img(url, name):
    img = api.get_img_content(url)
    file_tools.mkdir('temp')
    with open(f'temp/{name}.jpg', 'wb') as f:
        f.write(img)
    # print(f'temp/{name}.jpg')


def parser(chapter_info):
    chapter_part_chapter_text = {}
    img_id = 0
    # with ThreadPoolExecutor(2) as f:
    for i, part in enumerate(chapter_info['part']):
        chapter_name_text = []
        pbar = tqdm(total=len(chapter_info['chapter_name'][i]), desc=part)
        for chapter_name, chapter_url in zip(chapter_info['chapter_name'][i], chapter_info['chapter_url'][i]):
            if chapter_name == '插图':
                print('跳过插图话')
                pbar.update()
                continue
            text, img_urls = api.get_chapter_text(chapter_url)  # 一话所有的文本和图片链接
            for img_url in img_urls:
                text = text.replace(img_url, f'temp/{img_id}.jpg')
                down_img(img_url, img_id)
                img_id += 1
            chapter_name_text.append([chapter_name, text])
            pbar.update()
        chapter_part_chapter_text[part] = chapter_name_text
    # print(chapter_part_chapter_text)
    return chapter_part_chapter_text


def choose_down_chapter(chapter_info):
    for i, part_name in enumerate(chapter_info['part'], start=1):
        print(f'{i}\t{part_name}')
    start_ = input('输入开始序号>>>')
    end_ = input('输入结束序号>>>')
    if start_.isdigit() and end_.isdigit():
        if start_ > end_:
            raise '请输入正确数字'
        start_, end_ = int(start_), int(end_)
        choose_chapter_info = {'part': chapter_info['part'][start_ - 1:end_],
                               'chapter_name': chapter_info['chapter_name'][start_ - 1:end_],
                               'chapter_url': chapter_info['chapter_url'][start_ - 1:end_]}
        return (start_, end_), choose_chapter_info

    else:
        raise '请输入正确数字'


def main(url):
    noval_id = api.get_noval_id(url)
    noval_info = api.get_noval_info(noval_id)  # 名称 封面 描述
    print(noval_info['book_name'])
    chapter_info = api.get_noval_chapter(noval_id)
    (start, end), choose_chapter_info = choose_down_chapter(chapter_info)

    epub_text = parser(choose_chapter_info)
    title = noval_info['book_name']
    author = noval_info['author']
    cover_content = api.get_img_content(noval_info['cover_url'])
    description = noval_info['description']
    write_epub.write_epub(title, author, epub_text, description, 'cover', cover_content, 'temp')
    file_tools.del_dir('temp', mode=2)


if __name__ == '__main__':
    # url = 'https://www.linovelib.com/novel/3805.html'
    url = 'https://www.linovelib.com/novel/2582.html'
    # url = 'https://www.linovelib.com/novel/2914.html'
    main(url)
