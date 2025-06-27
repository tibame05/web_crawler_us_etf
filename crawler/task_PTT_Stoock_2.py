import requests
from bs4 import BeautifulSoup
import time
import csv

from crawler.worker import app
@app.task()
def crawler_finmind(stock_id):   
    sess = requests.Session()
    sess.cookies.set('over18', '1')  # 解锁板

    base = 'https://www.ptt.cc'
    url = base + '/bbs/Stock/index.html'

    all_data = []

    for page in range(10):  # 抓取前10頁
        print(f'🔍 正在抓取第 {page+1} 頁: {url}')
        res = sess.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')

        for entry in soup.select('div.r-ent'):
            date = entry.select_one('div.date').get_text(strip=True)
            title_tag = entry.select_one('div.title a')
            if not title_tag:
                continue  # 被刪除的文章
            title = title_tag.get_text(strip=True)
            link = base + title_tag['href']
            net = entry.select_one('div.nrec').get_text(strip=True)

            try:
                sub = sess.get(link, timeout=5)
                sp2 = BeautifulSoup(sub.text, 'html.parser')
            except:
                continue  # 忽略無法連線的文章

            push = boo = arrow = 0
            for p in sp2.select('div.push'):
                tag_span = p.select_one('span.push-tag')
                if not tag_span:
                    continue  # 沒有找到 push-tag，跳過
                tag = tag_span.get_text(strip=True)
                if tag == '推':
                    push += 1
                elif tag == '噓':
                    boo += 1
                elif tag == '→':
                    arrow += 1

            all_data.append({
                'date': date,
                'title': title,
                'push': push,
                'boo': boo,
                'arrow': arrow,
                'net': net,
                'link': link
            })
            print(date, title, f"推:{push}", f"噓:{boo}", f"箭頭:{arrow}", f"净推:{net}")
            time.sleep(0.05)  # 避免請求過快

        # 找上一頁連結
        paging = soup.select('div.btn-group-paging a')
        prev_url = base + paging[1]['href']
        url = prev_url
        time.sleep(0.5)

    # 輸出 CSV
    with open('Output/ptt_stock_10_pages.csv', 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=['date', 'title', 'push', 'boo', 'arrow', 'net', 'link'])
        writer.writeheader()
        writer.writerows(all_data)

    print(f"✅ 完成，共抓取 {len(all_data)} 篇文章，結果已儲存到 ptt_stock_10_pages.csv")
