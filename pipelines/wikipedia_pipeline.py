import requests
import pandas as pd
import json

from bs4 import BeautifulSoup


NO_IMAGE = 'https://upload.wikimedia.org/wikipedia/commons/thumb/0/0a/No-image-available.png/480px-No-image-available.png'

def get_wikipedia_page(url):
   
    if url is None:
        raise ValueError("URL content is None.")
    print( "Getting wikipedia page...",url)

    try:
        response = requests.get(url, timeout=50)
        response.raise_for_status()# check if the request is successful or not.

        return response.text
    except requests.RequestException as e:
        print(f"A error ocurred: {e}")
        return None
        

def get_wikipedia_data(html):

    if html is None:

        raise ValueError("HTML content is None.")

    soup = BeautifulSoup(html, "html.parser")
   
    table = soup.find_all("table", {"class": "wikitable"})[1]
    
    if not table:
        raise ValueError("Nenhuma tabela encontrada na página da Wikipedia com a classe especificada.")
    
    table_rows = table.find_all('tr')  # Using the first table found


    return table_rows


def clean_text(text):

    text = str(text).strip()
    text = text.replace('&nbsp', '')

    if not text:
        return "Text esta vazio"  # or any default value you consider appropriate
    
    # Return the first element
    else:
        if text.find(' ♦'):
            text = text.split()[0]

        if text.find('[') != -1:
            text = text.split('[')[0]

        if text.find(' (formerly)') != -1:
            text = text.split(' (formerly)')[0]

        return text.replace('\n', '')


def extract_wikipedia_data(**kwargs):
    
    url = kwargs['url']

    html = get_wikipedia_page(url)

    rows = get_wikipedia_data(html)

    data = []

    for i in range(1, len(rows)):

        tds = rows[i].find_all('td')

        values = {
            'rank' : i,
            'stadium' : clean_text(tds[0].text),
            'capacity': clean_text(tds[1].text),
            'region': clean_text(tds[2].text),
            'country': clean_text(tds[3].text),
            'city': clean_text(tds[4].text),
            'images': 'https://' + tds[5].find('img').get('src').split("//")[1] if tds[5].find('img') else "NO_IMAGE",
            'home_team': clean_text(tds[6].text),
        }
        data.append(values)
    
    json_rows = json.dumps(data)
    kwargs['ti'].xcom_push(key='rows', value=json_rows)

    return "OK"

def transform_wikipedia_data(**kwarqs):
    data = kwarqs['ti'].xcom_pull(key='rows', task_ids='extract_data_from_wikipedia')

    data = json.loads(data)

    stadium_df = pd.DataFrame(data)

    stadium_df['images'] = stadium_df['images'].apply(lambda x: x if x not in ['NO_IMAGE', '', None] else NO_IMAGE)


