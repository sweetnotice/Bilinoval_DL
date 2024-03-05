import re

# text = '''
# <img src="/images/sloading.svg" data-src="https://img3.readpai.com/3/3162/160566/195810.jpg" class="imagecontent lazyload">
# <img src="https://img3.readpai.com/3/3162/160565/189961.jpg" class="imagecontent">
# '''
#
# pattern = '<img[^>]+(src|data-src)="(.*?)" class="imagecontent'
# matches = re.findall(pattern, text)
#
# for match in matches:
#     print(match[1])
import re

html = '''  
<img src="/images/sloading.svg" data-src="temp_img/0.jpg" class="imagecontent lazyload"/>  
<img src="/images/sloading.svg" data-src="temp_img/1.jpg" class="imagecontent lazyload"/>  
<img src="/images/sloading.svg" data-src="temp_img/2.jpg" class="imagecontent lazyload"/>  
<img src="/images/sloading.svg" data-src="temp_img/3.jpg" class="imagecontent lazyload"/>  
<img src="/images/sloading.svg" data-src="temp_img/4.jpg" class="imagecontent lazyload"/>  
<img src="/images/sloading.svg" data-src="temp_img/5.jpg" class="imagecontent lazyload"/>  
<img src="/images/sloading.svg" data-src="temp_img/6.jpg" class="imagecontent lazyload"/>  
<img src="/images/sloading.svg" data-src="temp_img/7.jpg" class="imagecontent lazyload"/>  
'''

# 使用正则表达式查找img标签，并替换src属性的值为data-src属性的值
new_html = re.sub(r'<img src="[^"]*" data-src="([^"]*)"[^>]*>',
                  r'<img src="\1" data-src="\1" class="imagecontent lazyload"/>', html)

print(new_html)
