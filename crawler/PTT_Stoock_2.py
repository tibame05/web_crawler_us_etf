import requests
from bs4 import BeautifulSoup

sess = requests.Session()
sess.cookies.set('over18', '1')  # 解锁板

base = 'https://www.ptt.cc'
url = base + '/bbs/Stock/index.html'

res = sess.get(url)
soup = BeautifulSoup(res.text, 'html.parser')

for entry in soup.select('div.r-ent'):
    date = entry.select_one('div.date').get_text(strip=True)
    title_tag = entry.select_one('div.title a')
    if not title_tag:
        continue  # 跳过被删文章
    title = title_tag.get_text(strip=True)
    link = base + title_tag['href']

    # 列表上“推噓值”，表示推-噓净值（可能是数字或 '爆'）
    net = entry.select_one('div.nrec').get_text(strip=True)

    # 再访问文章页计算实际推、噓、箭头数
    sub = sess.get(link)
    sp2 = BeautifulSoup(sub.text, 'html.parser')
    push = boo = arrow = 0
    for p in sp2.select('div.push'):
        tag = p.select_one('span.push-tag').get_text(strip=True)
        if tag == '推':
            push += 1
        elif tag == '噓':
            boo += 1
        elif tag == '→':
            arrow += 1

    print(date, title, f"推:{push}", f"噓:{boo}", f"箭頭:{arrow}", f"净推:{net}")