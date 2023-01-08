import requests
from fake_headers import Headers
from bs4 import BeautifulSoup
import json
from tqdm import tqdm


# поиск по области 1 - Москва, 2 - СПб, тексту - Python
def hh_params(page):
    params = {
        'area': ['1', '2'],
        'text': 'python',
        'page': page
    }
    return params


# без заголовков hh не работает
def get_headers():
    return Headers(browser="chrome", os="win").generate()


# фильтрация вакансий по словам django и flask в описании на странице вакансии
def match(host):
    response = requests.get(host, headers=get_headers()).text
    soup = BeautifulSoup(response, 'html.parser')
    job_discript = soup.find(attrs={"data-qa": "vacancy-description"}).text
    if "django" in job_discript.lower() or "flask" in job_discript.lower():
        return True


def page_parse(host, pages):
    jobs = []
    for page in range(pages):
        response = requests.get(host, headers=get_headers(), params=hh_params(page)).text
        soup = BeautifulSoup(response, 'html.parser')
        vacancy_info = soup.find_all(class_="vacancy-serp-item-body__main-info")
        # tqdm - статус бар
        for job in tqdm(vacancy_info, desc=f'Просмотрено вакансий на странице {page+1}: '):
            link = job.find(class_='serp-item__title')
            if match(link['href']):
                salary = job.find('span', class_='bloko-header-section-3')
                # \u202f - неразделяемый пробел, нераспознается json, заменяем на пробел
                salary = salary.text.replace('\u202f', ' ') if salary else "не указана"
                city = job.find(attrs={"data-qa": "vacancy-serp__vacancy-address"}, class_='bloko-text')
                if city:
                    # убираем из записи городов станции метро и районы
                    city = city.text.partition(',')[0]
                jobs.append(
                    {'link': link['href'].partition('?')[0],  # ссылка на вакансию, убираем из нее параметры
                     'vacancy': link.text,  # название вакансии
                     'city': city,  # город
                     'salary': salary}  # зарплата
                )
    return jobs


if __name__ == '__main__':
    hh = "https://spb.hh.ru/search/vacancy"
    joblist = page_parse(hh, 2)  # выбираем количество просмотренных страниц

    with open('new_json.json', 'w', encoding='utf-8') as j:
        json.dump(joblist, j, ensure_ascii=False, indent=4)
