import requests
from bs4 import BeautifulSoup
import time

PTT_URL = 'https://www.ptt.cc'
BOARD = 'Stock'

def get_articles_from_index(url):
    cookies = {'over18': '1'}  # 同意滿18
    res = requests.get(url, cookies=cookies)
    soup = BeautifulSoup(res.text, 'html.parser')

    articles = []
    for entry in soup.select('div.r-ent'):
        link = entry.select_one('div.title a')
        if link:
            articles.append({
                'title': link.text.strip(),
                'url': PTT_URL + link['href'],
                'date': entry.select_one('div.date').text.strip()
            })
    
    # 找上一頁連結
    prev_link = soup.select('div.btn-group-paging a')[1]['href']
    return articles, PTT_URL + prev_link

def parse_article(url):
    res = requests.get(url, cookies={'over18': '1'})
    soup = BeautifulSoup(res.text, 'html.parser')
    main = soup.select_one('#main-content')

    # 移除 meta、推文
    for tag in main.select('div.article-metaline, div.article-metaline-right, div.push'):
        tag.extract()

    content = main.text.strip()

    # 取發文時間
    try:
        time_tag = soup.select('div.article-metaline span.article-meta-value')[3]
        post_time = time_tag.text.strip()
    except:
        post_time = ''

    # 推噓數
    pushes = soup.select('div.push')
    push_count = 0
    boo_count = 0
    for push in pushes:
        tag = push.select_one('span.push-tag').text.strip()
        if tag == '推':
            push_count += 1
        elif tag == '噓':
            boo_count += 1

    return {
        'content': content,
        'time': post_time,
        'push': push_count,
        'boo': boo_count
    }

if __name__ == '__main__':
    index_url = f'{PTT_URL}/bbs/{BOARD}/index.html'
    all_data = []
    for page in range(3):  # 改這裡控制頁數
        articles, index_url = get_articles_from_index(index_url)
        for article in articles:
            data = parse_article(article['url'])
            all_data.append({
                'title': article['title'],
                'date': article['date'],
                'time': data['time'],
                'content': data['content'],
                'push': data['push'],
                'boo': data['boo']
            })
            print(f"✓ {article['title']} ({data['push']}推/{data['boo']}噓)")
        time.sleep(0.5)  # 降低爬蟲頻率

    # 可選：輸出 JSON 檔
    # import json
    # with open('ptt_stock.json', 'w', encoding='utf-8') as f:
    #     json.dump(all_data, f, ensure_ascii=False, indent=2)
