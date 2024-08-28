import json
import requests
from database import ProductResponseModel as Product, ProductDetailsResponseModel as ProductDetails, Crawl
from prox import get_proxy
from keys import URL


CHAT_ID = -4125682328
proxies = get_proxy()

def get_data(url, page=1, proxies=proxies):
    url_split = url.split('/')
    slugs = url_split[4].split('--')
    pl = {
        "query": open('query.txt', 'r').read(),
        "variables": {
            "subcategoryProductsFilterInput": {
                "categorySlug": slugs[0],
                "compilationPath": slugs[1:],
                "pagination": {
                    "page": page,
                    "perPage": 48
                },
                "conditions": [],
                "sorting": {
                    "id": "",
                    "direction": "SORT_DIRECTION_DESC"
                },
                "popularitySegmentId": "THREE"
            },
            "categoryFilterInput": {
                "slug": slugs[0]
            },
            "categoryCompilationFilterInput": {
                "slug": slugs[1] if len(slugs) > 1 else ""
            }
        }
    }

    resp = requests.post('https://www.citilink.ru/graphql/', json=pl, proxies=proxies)
    if resp.status_code == 429:
        return get_data(url, page, get_proxy())

    return resp.json()['data']['productsFilter']['record']

def product(url, appid, crawlid, page=1, proxies=proxies):
    js_data = get_data(url, page, proxies=proxies)
    for prod in js_data['products']:
        prod_url = 'https://www.citilink.ru/product/' + prod['slug'] + '-' + prod['id']
        name = prod['name'].replace('  ', ' ')
        if not prod['price']['current']:
            continue
            # if prod['price']['clubPriceViewType'] == 'INVALID':
            #     return product(url, appid, crawlid, page, proxies=get_proxy())

        price = int(prod['price']['current'])

        item = {}
        item['appid'] = appid
        item['crawlid'] = crawlid
        item['url'] = url
        item['statusCode'] = 200
        item["productUrl"] = prod_url
        item["price"] = price
        item["name"] = name

        query: Product = (Product
                .select(Product, Crawl)
                .join(Crawl, on=(Product.crawlid == Crawl.crawlid))
                .where(Product.productUrl == item['productUrl'])
                .order_by(Crawl.created_at.desc())
                .limit(1)).get_or_none()
        if query and query.price and item['price']:
            if query.price > item['price'] + (query.price * 0.2):
                text = (
                    f"<b>Citilink</b>\n\n"
                    f"<b>Наименование:</b> <a href='{item['productUrl']}'>{item['name']}</a>\n"
                    f"<b>Старая цена</b>: {query.price}\n<b>Цена</b>: {item['price']}"
                )
                params = {
                    'chat_id': CHAT_ID,
                    'text': text,
                    'parse_mode': 'HTML'
                }
                try:
                    response = requests.get(URL, params=params, proxies=proxies)
                    result = response.json()
                    if result['ok']:
                        print("Message sent successfully.")
                    else:
                        print("Failed to send message:", result['description'])
                except Exception as e:
                    print(f"Failed to send message error: {e}")

        Product.create(**item)

    if page == 1 and js_data['products']:
        for page in range(2, js_data['pageInfo']['totalPages']+1):
            product(url, appid, crawlid, page)


def detail(url, appid, crawlid, proxies=proxies):
    resp = requests.get(url, proxies=proxies)
    if resp.status_code == 429:
        return detail(url, appid, crawlid, get_proxy())
    
    js_data = resp.content.rsplit(b'__NEXT_DATA__', 1)[1]
    js_data = js_data.split(b'>', 1)[1].split(b'</script>', 1)[0]
    js_data = json.loads(js_data)
    js_data = js_data['props']['initialState']['productPage']
    js_data = js_data['productHeader']['payload']
    if js_data is None: return
    js_data = js_data['productBase']
    
    name = js_data['name'].replace('  ', ' ')
    brand = js_data['brand']['name']
    images = [x['sources'][-1]['url'] for x in js_data['images']]
    details = {x['name']: x['value'] for x in js_data['properties']}

    item = {}
    item['appid'] = appid
    item['crawlid'] = crawlid
    item['url'] = url
    item['statusCode'] = resp.status_code
    item["productUrl"] = url
    item["imageUrls"] = json.dumps(images)
    item["name"] = name
    item["brandName"] = brand
    item["details"] = json.dumps(details)
    
    ProductDetails.create(**item)
