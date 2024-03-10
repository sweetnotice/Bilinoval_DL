# Bilinoval_DL

## 哔哩轻小说下载器

是一个[哔哩轻小说](https://www.linovelib.com/)的小说下载器

- 可自行选择卷下载

- 自动打包为epub

- 可视化进度条

## How to use?

自行构建环境  打开src中的parser 修改其中的url链接  运行

### TODO

- [x] 完善字体混淆码

- [ ] 小说进度跟踪(目前没有账号)

- [ ] 优化epub章节显示

### Q&A

- Q: 为什么运行速度慢
  
  A: 因为网站有一秒访问限制 无解

### 更新日志

#### 0310#3

- 修改用户交互为输入开始章与结束章地址

- 增加api方法

- 增加异常捕获

#### 0305#2

- 优化文件存放位置
- 修改获取章名与章链接方式为每章获取 (因为catalog界面会出现章名打码和链接为JavaScript)
- 用户选章下载 输入0 全卷下载
- 增加对第一话为插图页的优化
