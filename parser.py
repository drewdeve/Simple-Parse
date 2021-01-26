import logging
import collections
import urllib.parse
import csv

import requests
import bs4
import lxml


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wb')

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'name_block',
        'price_block',
        'optprice_block',
        'model_block',
        'available_block',
        'description_block',
        'specific_block',
        'img_block',
        'img2_block',
        'url',
    ),
)

HEADERS = (
    'Название', 
    'Цена', 
    'Оптовая цена', 
    'Модель', 
    'Наличие', 
    'Описание', 
    'Характеристика', 
    'Изображение №1', 
    'Изображение №2', 
    'Ссылка',
)

class Parser:
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
            'Accept-Language': 'ru',
        }
        self.result = []

    def load_page(self, page: int = None):
        params = {}
        if page and page > 1:
            params['page'] = page
    
        url = 'https://domenica.com.ua/odezhda-dlya-doma'
        res = self.session.get(url=url, params=params)
        res.raise_for_status()
        return res.text

    def parse_page(self, text: str):
        for x in range(12):
            logger.debug(f'Status message: page {x}')
            text = self.load_page(page=x)
            soup = bs4.BeautifulSoup(text, "lxml")
            container = soup.select_one('div.d-flex.flex-wrap.justify-content-start.product-wrapper')
            self.parse_block(block=container)

    def parse_block(self, block):
        products = block.find_all('a',{'class':'product-item text-left'})
        if not products:
            logger.error('no products blocks')
            return

        urls = []
        for product in products:
            url = product.get('href')
            urls.append(url)
            if not url:
                logger.error('no href')
                return
 
        for url in urls:
            res = self.session.get(url)
            html = res.text
            soup = bs4.BeautifulSoup(html, "lxml")
            name_block = soup.select_one('h1.title-item').text
            if not name_block:
                logger.error(f'no name_block on {url}')
                return
            price_block = soup.select_one('span.new-price.medium.ml-2').text
            if not price_block:
                logger.error(f'no price_block on {url}')
                return
            optprice_block = soup.select_one('span.optprice').text
            if not optprice_block:
                logger.error(f'no optprice_block on {url}')
                return
            model_block = soup.find('div',{'class':'col-12 p-0 row m-0'}).find_next('span').text
            if not model_block:
                logger.error(f'no model_block on {url}')
                return
            available_block = soup.select_one('div.col-6.text-right.p-0').text
            if not available_block:
                logger.error(f'no available_block on {url}')
                return
            img_block = soup.find('div',{'class':'general-photo-wrap d-block reletive'}).find_next('img')['src']
            if not img_block:
                logger.error(f'no img_block on {url} or dont found src')
                return
            img2_block = soup.find('ul',{'class':'pl-0 d-inline-block mt-2 color-product'}).find_next('img')['src']
            if not img2_block:
                logger.error(f'no img2_block on {url} or dont found src')
                return
            description_block = soup.find('div', {'class':'col-8 pt-4 pl-0 pr-0'}).find_next('p').text
            if not description_block:
                logger.error(f'no description_block on {url}')
                return
            specific_block = str(soup.select_one('table.attribute').text)
            if not specific_block:
                logger.error(f'no specific_block on {url}')
                return

            self.result.append(ParseResult(
                name_block=name_block,
                price_block=price_block,
                optprice_block=optprice_block,
                model_block=model_block,
                available_block=available_block,
                img_block=img_block,
                img2_block=img2_block,
                description_block=description_block,
                specific_block=specific_block,
                url=url,
            ))
    
    def save_result(self):
        path = 'dominic.csv'
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self):
        text = self.load_page()
        self.parse_page(text=text)
        logger.info(f'Получили {len(self.result)} элементов')
        self.save_result()

if __name__ == '__main__':
    parser = Parser()
    parser.run()