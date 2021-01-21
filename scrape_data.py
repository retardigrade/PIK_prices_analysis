import time

import requests
from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.common.keys import Keys

import pandas as pd


project_list_url = 'https://www.pik.ru/projects'
flat_url_base = 'https://www.pik.ru/search'
webdriver_path = 'C:\\Users\\petr\\Desktop\\dev\\_PROJECTS\\pik_flats\\web_driver\\chromedriver.exe'
data_path = '.\\data\\'


def get_project_list():
    project_page = requests.get(project_list_url)
    project_soup = BeautifulSoup(project_page.content, 'lxml')
    project_body = project_soup.body
    project_list = list()

    for a in project_body.find_all('a', attrs={'target': '_self'}):
        try:
            href = a['href']
            address = a.find('h6').text
            metro_name = a.find('span', attrs={'type': 'subTitleTwo'}).text
            try:
                metro_type = a.contents[2].div.div.contents[1].div.div.div.div.div.div['type']
            except AttributeError:
                metro_type = a.contents[2].div.div.contents[1].div.contents[0].div.div['type']
            metro_time = a.contents[2].div.div.contents[1].div.span.text
            project_list.append([href, address, metro_name, metro_type, metro_time])
        except AttributeError:
            pass

    return project_list  # python list of all projects data


def get_flat_list(project_flat_url):
    flat_url = flat_url_base + project_flat_url

    driver = webdriver.Chrome(executable_path=webdriver_path)
    driver.get(flat_url)

    try:
        time.sleep(5)
        html = driver.find_element_by_tag_name('html')
        html.send_keys(Keys.END)
        time.sleep(20)
    finally:
        page = driver.page_source
        driver.quit()
        flat_list_page = BeautifulSoup(page, 'lxml')
        flat_tags = flat_list_page.body.find_all('a', {'class': 'sc-erNlkL PtqKj'})

    return flat_tags


def get_flat_data(flat_list):
    flat_data = list()

    for flat in flat_list:

        # get main features
        url = flat['href']
        location = flat.find('span', {'class': 'sc-bdVaJa eXgwJJ Typography'}).text
        location_list = location.split(', ')
        section = location_list[-2]
        floor = location_list[-1]
        if len(location_list) == 3:
            building = location_list[0]
        elif len(location_list) > 3:
            building = ', '.join(location_list[:-2])
        else:
            section, floor, building = ('-', '-', '-')

        rooms, area, _ = flat.find('h6', {'class': 'sc-bdVaJa lbeMBz Typography'}).text.split(' ')
        move_in = flat.find('span', {'class': 'sc-bdVaJa bDJwwA Typography'}).text

        # get finish and offer features
        try:
            finish = flat.find('span', {'class': 'sc-bdVaJa eMLNis Typography'}).text
        except AttributeError:
            finish = '-'

        try:
            no_finish = flat.find('span', {'class': 'sc-bdVaJa gYqfvK Typography'}).text
        except AttributeError:
            no_finish = '-'

        try:
            low_mortgage = flat.find('span', {'class': 'sc-bdVaJa kygNff Typography'}).text
        except AttributeError:
            low_mortgage = '-'

        try:
            old_price = flat.find('span', {'class': 'sc-bdVaJa fdtYeV Typography'}).text
        except AttributeError:
            old_price = '-'

        # get price
        price = flat.find('span', {'type': 'subTitleOne'}).text

        flat_data.append([url, location, building, section, floor, rooms, area,
                          move_in, finish, no_finish, low_mortgage, old_price, price])

    return flat_data


if __name__ == '__main__':
    projects = get_project_list()
    project_links = [project[0] for project in projects]

    all_flat_data = pd.DataFrame([], columns=['url', 'location', 'building', 'section',
                                              'floor', 'rooms', 'area', 'move_in', 'finish',
                                              'no_finish', 'low_mortgage', 'old_price', 'price'])

    for link in project_links:
        flat_list = get_flat_list(link)
        flat_data = pd.DataFrame(get_flat_data(flat_list),
                                 columns=['url', 'location', 'building', 'section',
                                          'floor', 'rooms', 'area', 'move_in', 'finish',
                                          'no_finish', 'low_mortgage', 'old_price', 'price'])

        all_flat_data = pd.concat([all_flat_data, flat_data])
        print(link, len(flat_data), len(all_flat_data))

        all_flat_data.to_csv('flats.csv')

        project_data = pd.DataFrame(projects, columns=['project', 'address', 'metro_name', 'metro_type', 'metro_time'])
        project_data.to_csv('projects.csv')
