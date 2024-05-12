js_check = """
const last_p = document.querySelector('#TextContent p:last-of-type')
const p_style = window.getComputedStyle(last_p)
const p_font_style = p_style.getPropertyValue('font-family')
if (p_font_style && p_font_style.includes('read')) {
    return true;
}
return false;
"""
if __name__ == '__main__':
    from DrissionPage import ChromiumPage
    from src import ocr_api
    page = ChromiumPage()
    page.set.load_mode.eager()
    url = 'https://www.linovelib.com/novel/3080/226848_2.html'
    resp = page.get(url)
    has_font_obfuscation = page.run_js(js_check)
    if has_font_obfuscation:
        # print('Has font obfuscation.')
        last_p = page.ele('css:#TextContent p:last-of-type')
        # last_p.get_screenshot()
        base64_pic = last_p.get_screenshot(as_base64='png')  # 返回截图二进制文本
        ocr_word = ocr_api.pytesseract_ocr(base64_pic)

