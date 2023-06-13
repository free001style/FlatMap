import requests
from bs4 import BeautifulSoup
from PIL import Image
import pickle
import numpy as np
from helpers import find_substring, find_first_digit
import json
import random
import re

model = None
# Загрузка модели из файла
with open('model.pickle', 'rb') as f:
    model = pickle.load(f)

i = 0


def find_flats_cian(url):
    global i
    flats = []

    cian_html = requests.get(url).text
    soup = BeautifulSoup(cian_html, features="html.parser")

    offers = soup.select("article[data-name='CardComponent']")

    for offer in offers:
        flat_imgs = set()

        flat_imgs.add(offer.find('img')['src'])

        main_img = np.asarray(Image.open(requests.get(
            list(flat_imgs)[0], stream=True).raw).resize((400, 400))).reshape(1, -1)

        model_prediction = model.predict(main_img)

        additional_imgs = offer.select(
            "div[data-name='Gallery']")[0].find_all('img')

        for fa in additional_imgs:
            flat_imgs.add(fa['src'])

        links = offer.find_all('a', {'target': '_blank'})

        title = offer.select(
            "div[data-name='GeneralInfoSectionRowComponent']")[0].text
        description = offer.select("div[data-name='Description']")[0].text

        flat_rooms = "Хорошая"

        if "1-к" in description or "1-комн." in description or "1-комн" in description or "1-к" in title or "1-комн." in title or "1-комн" in title:
            flat_rooms = "1 комнатная"
        if "2-к" in description or "2-комн." in description or "2-комн" in description or "2-к" in title or "2-комн." in title or "2-комн" in title:
            flat_rooms = "2 комнатная"
        if "3-к" in description or "3-комн." in description or "3-комн" in description or "3-к" in title or "3-комн." in title or "3-комн" in title:
            flat_rooms = "3 комнатная"
        if "4-к" in description or "4-комн." in description or "4-комн" in description or "4-к" in title or "4-комн." in title or "4-комн" in title:
            flat_rooms = "4 комнатная"

        flat_floor = "самом тихом"

        floor_text = find_substring(description, "этаж") + " " + find_substring(
            description, "этаже") + " " + find_substring(title, "этаж") + " " + find_substring(title, "этаже")
        find_floor = find_first_digit(floor_text)

        if find_floor:
            flat_floor = find_floor

        flat_space = "самого удобного размера в"
        space_text = find_substring(description, "м²") + " " + find_substring(
            description, "м²") + " " + find_substring(title, "м²") + " " + find_substring(title, "м²")
        find_space = find_first_digit(space_text)

        if find_space:
            flat_space = find_space

        flat_name = f"{flat_rooms} квартира на {flat_floor} этаже с площадью {flat_space} м²"

        flat_price = offer.find("span", {"data-mark": "MainPrice"}).text

        for a in links:
            if 'https://www.cian.ru/rent/flat/' or 'https://www.cian.ru/sale/flat/' in a['href']:
                if '/cat.php?' not in a['href']:
                    flats.append(
                        {
                            "address": '',
                            "photos": list(flat_imgs),
                            "name": flat_name,
                            "price": flat_price,
                            "link": a['href'],
                            "description": description,
                            "floor": flat_floor,
                            "space": flat_space,
                            "rooms": flat_rooms,
                            "model_prediction": model_prediction
                        })
                    break

        for _ in range(len(flats)):
            flats[_]['index'] = i
            i += 1

    return flats


def find_flats(url):
    global i
    script = requests.get(url)
    script = script.text
    data = json.loads(script)
    flats = []
    for offer in data["data"]:
        photos = list(map(lambda x: list(x.values())[0], offer["images"]))
        # main_img = np.asarray(
        #     Image.open(requests.get(list(photos)[0], stream=True).raw).resize((400, 400))).reshape(1, -1)
        # model_prediction = model.predict(main_img)
        flats.append({
            "address": offer['address'], "photos": photos,
            "name": offer['title'],
            "price": re.sub(r'(-?)(\d\d\d)', r'\2 ', str(offer['price'])[::-1])[::-1] + "₽",
            "link": offer['url'],
            "description": offer['description'],
            "floor": offer['params']['Этаж'],
            "space": offer['params']['Площадь'],
            "rooms": offer['params']['Количество комнат'],
            "model_prediction": random.randint(0, 1)
        })

    for _ in range(len(flats)):
        flats[_]['index'] = i
        i += 1

    return flats
