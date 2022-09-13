from setting import *
import requests
from bs4 import BeautifulSoup
import json
from time import sleep
from random import randrange


"""Загружаем страницу"""
def get_html(url=url):
    req = requests.get(url, headers=headers)
    src = req.text
    return src


"""Забираем все ссылки с типов еды"""
def pars_types(src):
    soup = BeautifulSoup(src, "lxml")
    all_products_href = soup.find_all(class_="mzr-tc-group-item-href")
    all_categories_dict = {}
    for i in all_products_href:
        item_text = i.text
        item_href = "http://health-diet.ru" + i.get('href')
        all_categories_dict[item_text] = item_href
    """Сохраняем в JSON"""
    with open("all_categories_dict.json", "w", encoding="utf-8") as file:
        json.dump(all_categories_dict, file, indent=4, ensure_ascii=False)


"""Забираем данные о товарах из JSON"""
def pars_products():
    with open("all_categories_dict.json", encoding="utf-8") as file:
        all_categories = json.load(file)
    iteration_count = int(len(all_categories)) - 1
    count = 0
    print(f"Всего итераций: {iteration_count}")

    """Заходим на новую страницу категории
    Собираем все товары, хим.состав, и запишем все это в файл под именем категории"""
    for category_name, category_href in all_categories.items():
        rep = [",", " ", "-", "'"]  # Список на замену символов

        """Заменяем символы из rep на нижний слеш для лаконичности"""
        for item in rep:
            if item in category_name:
                category_name = category_name.replace(item, "_")

        """Делаем запрос по каждому элементу из JSON"""
        req = requests.get(url=category_href, headers=headers)
        src = req.text

        """Собираем названия колонок таблицы продуктов питания"""
        soup = BeautifulSoup(src, 'lxml')
        """Сначала проверим, есть ли ошибка на странице (они есть, например если страница не содержит данных)"""
        alert_block = soup.find(class_="uk-alert-danger")
        if alert_block is not None:
            continue

        """Если ошибок нет, продолжаем"""
        product_data = soup.find(class_="uk-overflow-container").find("tbody").find_all("tr")
        """Собираем продукты и их ценность"""
        product_info = []  # Для JSON
        for item in product_data:
            product_tds = item.find_all("td")

            title = product_tds[0].text.strip()
            calories = product_tds[1].text.strip()
            proteins = product_tds[2].text.strip()
            fats = product_tds[3].text.strip()
            carbohydrates = product_tds[4].text.strip()
            """ И дозаписываем их в product_info"""
            product_info.append(
                {
                    "Title": title,
                    "Calories": calories,
                    "Proteins": proteins,
                    "Fats": fats,
                    "Cardohydrates": carbohydrates

                }
            )

        """Добавляем в наш JSON"""
        with open(f"Data/{count}_{category_name}.json", "a", encoding="utf-8-sig") as file:
            json.dump(product_info, file, indent=4, ensure_ascii=False)
        count += 1
        print(f"# Итерация: {count}. {category_name} записан...")
        iteration_count -= 1
        if iteration_count == 0:
            print("Работа закончена")
            break
        print(f"Осталось итераций: {iteration_count}.")
        sleep(randrange(2, 4))  # Не будем наглеть, сделаем паузу между запросами


if __name__ == "__main__":
    pars_types(get_html())
    pars_products()
