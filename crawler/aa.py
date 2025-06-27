import requests
from bs4 import BeautifulSoup

url = 'https://www.ptt.cc/bbs/Stock/M.1751031048.A.EAE.html'
cookies = {'over18': '1'}
headers = {'User-Agent': 'Mozilla/5.0'}

res = requests.get(url, cookies=cookies, headers=headers)
soup = BeautifulSoup(res.text, 'html.parser')

push_count = 0
boo_count = 0

pushes = soup.find_all("div", class_="push")
print(f"總共抓到 {len(pushes)} 則留言")

for push in pushes:
    tag = push.select_one('span.push-tag')
    if tag:
        tag_text = tag.text.strip()
        if tag_text == '推':
            push_count += 1
        elif tag_text == '噓':
            boo_count += 1

print(f"推文數: {push_count}")
print(f"噓文數: {boo_count}")
