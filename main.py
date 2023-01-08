import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
import json
from tqdm import tqdm


def hh_params(page):
    params = {
        'area': ['1', '2'],
        'text': 'python',
        'page': page
    }
    return params


def get_headers():
    return Headers(browser="chrome", os="win").generate()


def match(host):
    response = requests.get(host, headers=get_headers()).text
    soup = BeautifulSoup(response, 'html.parser')
    job_discript = soup.find(attrs={"data-qa": "vacancy-description"}).text
    if "django" in job_discript.lower() or "flask" in job_discript.lower():
        return True


def page_parse(host):
    jobs = []
    for page in range(2):
        response = requests.get(host, headers=get_headers(), params=hh_params(page)).text
        soup = BeautifulSoup(response, 'html.parser')
        vacancy_info = soup.find_all(class_="vacancy-serp-item-body__main-info")
        for job in tqdm(vacancy_info, desc=f'Просмотрено вакансий на странице {page+1}: '):
            # for job in vacancy_info:
            link = job.find(class_='serp-item__title')
            if match(link['href']):
                salary = job.find('span', class_='bloko-header-section-3')
                salary = salary.text.replace('\u202f', ' ') if salary else "не указана"
                city = job.find(attrs={"data-qa": "vacancy-serp__vacancy-address"}, class_='bloko-text')
                if city:
                    city = city.text.partition(',')[0]
                jobs.append(
                    {'link': link['href'],
                     'vacancy': link.text,
                     'city': city,
                     'salary': salary}
                )
    return jobs


if __name__ == '__main__':
    hh = "https://spb.hh.ru/search/vacancy"
    joblist = page_parse(hh)

    with open('new_json.json', 'w', encoding='utf-8') as j:
        json.dump(joblist, j, ensure_ascii=False, indent=4)
