import csv
import requests
from bs4 import BeautifulSoup

args = []

for x in range(12):
    url = 'https://domenica.com.ua/odezhda-dlya-doma?page={}'.format(x)

    header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'}

    response = requests.get(url, headers=header)

    html = response.text

    soup = BeautifulSoup(html, 'html.parser')

    container = soup.select_one('div.right-side.p-0')


    products = container.find_all('a',{'class':'product-item text-left'})

    urls = []
    for product in products:
        url = product.get('href')
        urls.append(url)

    for url in urls:
        response = requests.get(url, headers=header)
        html = response.text
        soup = BeautifulSoup(html, 'html.parser')
        name = soup.select_one('h1.title-item').text
        price = soup.select_one('span.new-price.medium.ml-2').text
        optprice = soup.select_one('span.optprice').text
        model = soup.find('div', {'class':'col-12 p-0 row m-0'}).find_next('span').text
        available = soup.select_one('div.col-6.text-right.p-0').text
        img = soup.find('div', {'class':'general-photo-wrap d-block reletive'}).find_next('img')['src']
        img2 = soup.find('ul', {'class':'pl-0 d-inline-block mt-2 color-product'}).find_next('img')['src']
        description = soup.find('div', {'class':'col-8 pt-4 pl-0 pr-0'}).find_next('p').text
        specific = str(soup.select_one('table.attribute').text)
        args.append((name, price, optprice, model, available, description, specific, img, img2, url))

    print('Status message: page = {}'.format(x))

names = ['Название', 'Цена', 'Оптовая цена', 'Модель', 'Наличие', 'Описание', 'Характеристика', 'Изображение №1', 'Изображение №2', 'Ссылка']


with open('data.csv', 'w', newline='') as f:
    writer = csv.writer(f, delimiter=',')
    writer.writerow(names)

    for ar in args:
        writer.writerow(ar)
