import requests
import time
from collections import Counter
import json
import re
url = 'https://hh.ru/search/vacancy'
params = {
    'text': 'python',
    'area': 1,
}
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}
response = requests.get(url, params=params, headers=headers, timeout=30)
match = re.search(r'<template[^>]*id="HH-Lux-InitialState"[^>]*>(.*?)</template>', response.text)
json_str = match.group(1).replace('&#34;', '"')
data = json.loads(json_str)
result = data['vacancySearchResult']
vacancies = result['vacancies']
with open('vacancies.json', 'w', encoding='utf-8') as f:
    json.dump(vacancies, f, ensure_ascii=False, indent=4)
print('Сохранено в vacancies.json')
with open('vacancies.json', 'r', encoding='utf-8') as f:
    vacancies = json.load(f)
print(f'Всего вакансий: {len(vacancies)}')
with_salary = 0
salaries = []
for v in vacancies:
    comp = v.get('compensation')
    if comp and comp.get('from'):
        salaries.append(comp['from'])
print(f'Вакансий с зарплатой: {len(salaries)}')
print(f'Средняя зарплата: {sum(salaries)/len(salaries):.0f}')
print(f'Максимум: {max(salaries)}')
print(f'Минимум: {min(salaries)}')
v = vacancies[0]
vacancy_id = v['vacancyId']
url = f'https://hh.ru/vacancy/{vacancy_id}'
response = requests.get(url, headers=headers, timeout=30)
match = re.search(r'<template[^>]*id="HH-Lux-InitialState"[^>]*>(.*?)</template>', response.text)
if match:
    json_str = match.group(1).replace('&#34;', '"')
    data_vacancy = json.loads(json_str)
else:
    print('JSON не нашли')
all_skills = []
failed = 0
for i, v in enumerate(vacancies):
    vacancy_id = v['vacancyId']
    url = f'https://hh.ru/vacancy/{vacancy_id}'
    try:
        response = requests.get(url, headers=headers, timeout=30)
        match = re.search(r'<template[^>]*id="HH-Lux-InitialState"[^>]*>(.*?)</template>', response.text)
        if not match:
            failed += 1
            continue
        json_str = match.group(1).replace('&#34;', '"')
        data_vacancy = json.loads(json_str)
        vacancy = data_vacancy['vacancyView']['vacancyFull']['vacancy']
        if 'keySkills' in vacancy:
            all_skills.extend(vacancy['keySkills'])
            time.sleep(1)
    except Exception as e:
        failed += 1
        time.sleep(1)
        continue
print(f'Готово! Собрано навыков: {len(all_skills)}')
print(f'Ошибок: {failed}')
with open('skills.json', 'w', encoding='utf-8') as f:
    json.dump(all_skills, f, ensure_ascii=False, indent=4)
print('Сохранено в skills.json')
counter = Counter(all_skills)
top = dict(counter.most_common(15))
with open('top_skills.json', 'w', encoding='utf-8') as f:
    json.dump(top, f, ensure_ascii=False, indent=4)
print('Топ-15 сохранен в top_skills.json')