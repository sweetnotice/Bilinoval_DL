from src import api
from datetime import datetime
import pytz

star_noval = {'败给了性格恶劣的天才青梅，初体验全部被夺走这件事': 3984,
              '转生公主与天才千金的魔法革命': 2734,
              }


def get_utc8_time():
    # 获取当前UTC时间
    utc_now = datetime.utcnow()

    # 转换为UTC+8时区（亚洲/上海，例如）
    beijing_tz = pytz.timezone('Asia/Shanghai')
    utc_plus_8_time = utc_now.astimezone(beijing_tz)

    # 格式化为'2024-02-21'
    formatted_date = utc_plus_8_time.strftime('%Y-%m-%d')

    # print(formatted_date)
    return formatted_date


def get_last_update(noval_id):
    noval_info = api.get_noval_info(noval_id)
    noval_name = noval_info['book_name']
    last_update_date = noval_info['last_update_time'].split(' ')[0]
    last_chapter_name = noval_info['last_chapter_name']
    # print(last_update_date, last_chapter_name)
    if last_update_date == get_utc8_time():
        message = f'{noval_name} 今天更新了!'
        print(message)


def main():
    for noval_id in star_noval.values():
        get_last_update(noval_id)


if __name__ == '__main__':
    main()
