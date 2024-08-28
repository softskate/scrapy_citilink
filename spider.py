from datetime import datetime, timedelta
import json
import time
from database import ParsingItem, App, Crawl, db, ProductResponseModel, ProductDetailsResponseModel
from peewee import JOIN
import parse


def run_command(spider_name, urls):
    try: urls.extend(json.loads(open(f'tasks_{spider_name}.json', 'rb').read()))
    except FileNotFoundError: pass
    urls = list(set(urls))
    app = App.create(
        name = 'Citilink',
        start_url = urls[0]
    )
    appid = app.get_id()
    crawl = Crawl.create()
    crawlid = crawl.get_id()
    open(f'tasks_{spider_name}.json', 'w', -1, 'utf8').write(json.dumps(urls))

    while urls:
        scrape_url = urls.pop()
        while True:
            try:
                print(f'Scraping url: {scrape_url}')
                if spider_name == 'product':
                    parse.product(scrape_url, appid, crawlid)
                elif spider_name == 'detail':
                    parse.detail(scrape_url, appid, crawlid)
                break
            except Exception as e:
                print(f'Error occurred while scraping: {e}')
                time.sleep(5)

        open(f'tasks_{spider_name}.json', 'w', -1, 'utf8').write(json.dumps(urls))
    time.sleep(60)

def run_spider():
    while True:
        db.connect()
        old_crawlers = Crawl.select().where(Crawl.created_at < (datetime.now() - timedelta(days=3)))
        dq = (ProductResponseModel
            .delete()
            .where(ProductResponseModel.crawlid.in_(old_crawlers)))
        dq.execute()

        parse_deails = []
        parse_products = []
    
        query = (ProductResponseModel
            .select()
            .join(ProductDetailsResponseModel, JOIN.LEFT_OUTER,
                  on=(ProductResponseModel.productUrl == ProductDetailsResponseModel.productUrl))
            .where(ProductDetailsResponseModel.productUrl.is_null(True)))

        print('Need to parse details', query.count())

        for item in query:
            parse_deails.append(item.productUrl)

        for item in ParsingItem.select():
            if item.item_type == 'product':
                parse_deails.append(item.link)
            else:
                parse_products.append(item.link)

        if parse_products:
            run_command('product', parse_products)
        if parse_deails:
            run_command('detail', list(set(parse_deails)))
        
        db.close()
        time.sleep(60*60)


if __name__ == '__main__':
    run_spider()
