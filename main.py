import csv
import requests
from bs4 import BeautifulSoup


URL = 'https://zakup.kbtu.kz/zakupki/sposobom-zaprosa-cenovyh-predlozheniy'
URL_BASE = 'https://zakup.kbtu.kz'
HEADERS = {
    'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36',
    'Accept':'*',
    "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8,de;q=0.7"
}


def save_csv(data: dict, file_name='Веб-портал закупок KBTU'):
    """Функция принимает Лист из словарей и наименование файла(без расширения). Затем записывает в csv файл данные из каждого словаря"""
    field_names = list(data[0].keys())
    with open(file_name+'.csv', 'w', encoding='windows-1251') as file:
        writer = csv.DictWriter(file, field_names)
        writer.writeheader()
        for row in data:
            writer.writerow(row)


def parse_card(path: str):
    """Функция принимает строку с путем карточки, по ней составляет URL карточки и парсит информацию оттуда"""
    r = requests.get(URL_BASE+path, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'lxml')

    card_data = {}
    # Див с информацией о карточке
    card = soup.find('div', attrs={
        'style': 'margin-top:0px;margin-bottom:0px;'
    })

    # Параграфы, чтобы позже достать Объявление и Дополнительную информацию
    paragraphs = card.find('div', class_='col').find_all('p')

    # Название Заявки / Закупки
    title = card.find('h4', 'card-title').text.strip() if card.find('h4', 'card-title') else 'Не указано'
    card_data['Наименование'] = title

    # Ссылка на карточку
    card_link = URL_BASE+path
    card_data['Ссылка'] = card_link

    # Объявление
    application = paragraphs[0].text.strip()
    card_data['Объявление'] = application if application else "Не указано"

    #Дополнительные документы
    additional_info = []
    for p in paragraphs[-3:]:
        additional_info.append(p.text.strip())

    card_data['Дополнительные документы'] = ''.join(additional_info)

    # Таблица с основной информацией(Организатор, Начало, Окончание, Статус)
    table_data = card.find('table')
    tds = table_data.find_all('td')
    for i in range(0, len(tds), 2):
        key = tds[i].text.split(':')[0].strip()
        value = tds[i+1].text.strip()
        card_data[key] = value

    return card_data


def main():
    r = requests.get(URL, headers=HEADERS)
    soup = BeautifulSoup(r.text, 'lxml')
    # Находим общее количество страниц, которые нужно спарсить
    last_page = soup.find_all('a', class_='btn btn-light')[-1].text.strip()
    last_page = int(last_page)+1
    cards= []
    for page in range(1, last_page):

        # Отправляем get запрос только если нужно следующую страниуц спарсить, так как первую мы уже получили до цикла
        if page != 1:
            r = requests.get(URL, headers=HEADERS,params={'page': page})
            soup = BeautifulSoup(r.text, 'lxml')
        
        print("Собирается информация со страницы с URL: ", r.url)
        
        # Собираем все ссылки на карточки-объявления
        card_links = soup.find_all('div', class_='card-body')
        for card_link in card_links:
            card_link = card_link.a['href']
            card = parse_card(card_link) # Парсим информацию и помещаем вернувшийся словарь в лист
            cards.append(card)

    save_csv(cards)


if __name__ == '__main__':
    main()


