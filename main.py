import requests
from bs4 import BeautifulSoup
import fake_headers
import time
import json
from tqdm import tqdm


# функция получения тегов страницы
def response(link_url):
    headers = fake_headers.Headers(browser='opera', os='linux')
    html = requests.get(link_url, headers=headers.generate()).text
    time.sleep(3)
    html_soup = BeautifulSoup(html, features='lxml')
    return html_soup


# функция получения списка организаций из списка тегов
def organization_func(tags_list):
    organization_list = []
    for org in tags_list:
        organization_1 = org.find('div', class_='info-section--N695JG77kqwzxWAnSePt')
        organization_2 = organization_1.find('span', class_='separate-line-on-xs--mtby5gO4J0ixtqzW38wh')
        organization_3 = organization_2.find('span', class_='bloko-text')
        organization = organization_3.find('span', class_='company-info-text--vgvZouLtf8jwBmaD1xgp')
        organization_list.append(organization.text.strip())
    return organization_list


# функция получения списка городов
def cities_func(tags_list):
    cities = []
    for с in tags_list:
        city_1 = с.find('div', class_='info-section--N695JG77kqwzxWAnSePt')
        city_2 = city_1.find('div', class_='wide-container--lnYNwDTY2HXOzvtbTaHf')
        city_3 = city_2.find('span', class_='bloko-text')
        city = city_3.find('span', class_='fake-magritte-primary-text--Hdw8FvkOzzOcoR4xXWni')
        cities.append(city.text)
    return cities


# функция формирования и вырузки json-файла
def json_dump(link, salary, organization_list, cities, description):
    json_list = []
    zip_list = list(zip(link, salary, organization_list, cities, description))
    substring1 = "Django"
    substring2 = "FLask"
    for el in zip_list:
        if el[4].find(substring1) != -1 or el[4].find(substring2) != -1:
            dict_ = {'link': el[0], 'salary': el[1], 'organization': el[2], 'city': el[3]}
            json_list.append(dict_)
    json_file = json.dumps(json_list, ensure_ascii=False)
    with open('vacancy_info.json', 'w', encoding='utf-8') as f:
        f.write(json_file)
    print("JSON файл с информацией о вакансиях выгружен")


if __name__ == '__main__':
    # вызов функции response(url)
    url = 'https://spb.hh.ru/search/vacancy?text=python&area=1&area=2'
    main_soup = response(url)

    # получение списка тегов
    div_vacancy = main_soup.find('div', id='a11y-main-content')
    tags = div_vacancy.find_all('div', 'vacancy-card--z_UXteNo7bRGzxWVcL7y font-inter')

    # вызов функции organization_func(tags_list)
    organization_list = organization_func(tags)

    # получениe списков ссылок(link), зараплат(salary), описаний вакансий(texts)
    link = []
    salary = []
    description = []
    for i in (pbar := tqdm(tags)):
        pbar.set_description("Идет обработка страниц вакансий")
        h2_tag = i.find('h2')
        a_tag = h2_tag.find('a')
        absolute_link = a_tag['href']
        # print(absolute_link)
        link.append(absolute_link)
        print(absolute_link)

        vacancy_soup = response(absolute_link)

        vacancy = vacancy_soup.find('span', class_='magritte-text___pbpft_3-0-13 magritte-text_style-primary___AQ7MW_3-0-13 magritte-text_typography-label-1-regular___pi3R-_3-0-13')

        salary.append(vacancy.text.strip())

        text = vacancy_soup.find('div', class_='g-user-content').text.strip()
        description.append(text)

    # вызов функции cities_func(tags_list) для получения списка городов
    cities = cities_func(tags)

    # вызов функции  json_dump для формирования и выгрузки json-файла на основе списков link, salary, organization_list, cities, description
    json_dump(link, salary, organization_list, cities, description)
