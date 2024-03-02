from pprint import pprint
from src import api
from tqdm import tqdm

# 网页获取文本(无混淆)
str1 = """"""
# 源码获取文本(有混淆)
str2 = """"""


def generate_dict(str1, str2):
    str1 = str1.replace('\n', '').replace('<p>', '').replace('<br>', '').replace('</p>', '').replace(' ', '')
    str2 = str2.replace('\n', '').replace('<p>', '').replace('<br>', '').replace('</p>', '').replace(' ', '')
    dict1 = {}
    for i in range(len(str1)):
        if str2[i] != str1[i]:
            word1 = str2[i]
            word2 = str1[i]
            if ord(word1) >= 40911:  # 汉字编码范围 19976 - 40911
                if ban_word.get(word1):
                    if word2 != ban_word.get(word1):
                        raise f'{word2}  {ban_word.get(word1)} 有两种含义'
                else:
                    print(f'增加 {word1}:{word2}')
                    ban_word[word1] = word2
                # dict1[word1] = word2
    return dict1


def get_str2(url):
    texts = []
    chapter_names = []
    white_rule = ['：', '，', '？', '（', '）', '！', '～', '＊', '；', 'ｖ', 'ｓ']
    out_words = []
    noval_id = api.get_noval_id(url)
    chapter_info = api.get_noval_chapter(noval_id)
    for name_part in chapter_info['chapter_name']:
        for name in name_part:
            chapter_names.append(name)
    for chapter in chapter_info['chapter_url']:
        for chapter_url in tqdm(chapter):
            chapter_text = api.get_chapter_text(chapter_url, debug=1)[0]
            texts.append(chapter_text)
            for word in chapter_text:
                if ord(word) >= 40911 and word not in white_rule and word not in out_words:
                    out_words.append(word)
    for out_word in out_words:
        if out_word not in ban_word:
            for i, chapter in enumerate(texts):
                if out_word in chapter:
                    print(f'{chapter_names[i]}:{out_word}')
                    # print(texts[i])
                    break


ban_word = {'\ue805': '阴',
            '\ue806': '种',
            '\ue80e': '交',
            '\ue80f': '作',
            '\ue812': '臀',
            '\ue819': '肉',
            '\ue81a': '舔',
            '\ue81b': '样',
            '\ue820': '射',
            '\ue821': '呻',
            '\ue822': '道',
            '\ue824': '乳',
            '\ue828': '胸',
            '\ue82d': '裸',
            '\ue82f': '性',
            '\ue832': '骚',
            '\ue83f': '欲',
            '\ue840': '私',
            '\ue84c': '穴',
            '\ue84d': '淫',
            '\ue857': '想',
            '\ue858': '美',
            '\ue85b': '茎',
            '\ue85c': '脱',
            '\ue85f': '唇',
            '\ue861': '开',
            '\ue862': '液'}
if __name__ == '__main__':
    # 先使用api获取话文字  再在浏览器打开自动复制脚本 手动复制整话进行匹配
    get_str2('https://www.linovelib.com/novel/302.html')
    # a = generate_dict(str1, str2)
    # pprint(ban_word)
