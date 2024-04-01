from spider_toolbox import file_tools
from src import parser
import config


def init():
    save_dir = config.save_dir
    temp_img_dir = config.temp_img_dir

    if config.save_dir == '' or config.temp_img_dir == '':
        raise '请检查设置!'

    file_tools.mkdir(save_dir)
    file_tools.mkdir(temp_img_dir)


def main():
    while 1:
        init()
        # user_input = input('输入链接>>>')
        parser.main()


if __name__ == '__main__':
    main()
