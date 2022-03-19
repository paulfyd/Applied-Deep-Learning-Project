from bs4 import BeautifulSoup
from random import randint
import requests
import urllib.request
import time
import pandas as pd
import os
import splitfolders

brands = ['chevrolet', 'renault', 'toyota', 'mazda', 'ford', 'kia', 'nissan', 'volkswagen', 'mercedes-benz', 'bmw']


class AppURLopener(urllib.request.FancyURLopener):
    version = "Mozilla/5.0"


def get_attr(li, attr):
    list_attr = [ele[attr] for ele in li]
    return list_attr


def get_data(url):
    opener = AppURLopener()
    try:
        html = opener.open(url)
        soup = BeautifulSoup(html, 'html.parser')
        return soup, True
    except:
        randSleep = randint(60, 120)
        print(f'Access to the site denied, waiting {randSleep} seconds.')
        time.sleep(randSleep)
        return None, False


def image_link_scraping(brands):
    for brand in brands:
        list_ads = []
        success = False
        for idx in range(1, 500, 48): # Each page has 48 ads of cars
            while not(success):
                soup_page, success = get_data(f'https://carros.tucarro.com.co/{brand}/_Desde_{idx}_NoIndex_True')
            link_ads = soup_page.find_all('a', class_='ui-search-result__content ui-search-link')
            if link_ads != []:
                list_ads += get_attr(link_ads, 'href')
            success = False
        print(f'list of ads for {brand} created.')
        n = len(list_ads)
        data_vehic = []
        success = False
        i = 0
        c = 0
        while i < n:
            # Wait until we have access to the site
            while not(success):
                soup_annonce, success = get_data(list_ads[i]) 
            try:
                # We store 2 images of the same car
                img_1 = soup_annonce.find_all('figure', class_='ui-pdp-gallery__figure')[0].img['data-zoom']
                img_2 = soup_annonce.find_all('figure', class_='ui-pdp-gallery__figure')[randint(1,2)].img['data-zoom']
                data_vehic.append(img_1)
                data_vehic.append(img_2)
                # caract = soup_annonce.find_all('span', class_='andes-table__column--value')
                # We store the brand of the car
                # marque = caract[0].text
                # We store the type of the car
                # type = caract[-2].text
                #data_vehic.append((marque, type, img_1))
                #data_vehic.append((marque, type, img_2))
                if (c  % 2 == 0):
                    print(f'{c} links of ads have been scraped of {brand}.')
                c += 2
                i += 1
            except:
                i += 1
            success = False
        df = pd.DataFrame(data_vehic, columns=['img_url'])
        df.to_csv(f'./links-brand/{brand}.csv', sep=';', index=False)
        print(f'csv for {brand} has been created.')


def download_imgs(brands):
    try:
        os.mkdir('./imgs-brand')
    except:
        pass
    for brand in brands:
        df = pd.read_csv(f'./links-brand/{brand}.csv', sep=';')
        urls = df['img_url']
        try:
            os.mkdir(f'./imgs-brand/{brand}')
        except:
            pass
        counter = 0
        for url in urls:
            try:
                file_name = f'./imgs-brand/{brand}/{brand}' + str(counter) + '.jpg'
                response = requests.get(url)
                file = open(file_name, 'wb')
                file.write(response.content)
                file.close()
                counter += 1
            except:
                pass
        print(f'{counter} images have successfully been downloaded for {brand}.')


def test_train_val(ratio=(.8, .1, .1)):
    '''
    separate images of ./data in 3 folders, test, train and val
    '''
    try:
        os.mkdir('./data')
    except:
        pass
    splitfolders.ratio(
        './imgs-brand/',
        output='./data',
        ratio=ratio)

if __name__ == "__main__":

    image_link_scraping(brands)
    download_imgs(brands)
    test_train_val()