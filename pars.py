from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
import json
import psycopg2
import random
from config1 import host, user, password, db_name


def get_all():
    try:
        connection = psycopg2.connect(
            host=host,
            user=user,
            password=password,
            database=db_name
        )
        cur = connection.cursor()
        connection.autocommit = True

        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT version();"
            )

            print(f"Server version: {cursor.fetchone()}")
            print(connection.get_dsn_parameters(), "\n")

        with connection.cursor() as cursor:
            cursor.execute(
                """CREATE TABLE game(
                    id serial PRIMARY KEY,
                    cost varchar(1000) NOT NULL,
                    name varchar(1000) NOT NULL,
                    description text,
                    minimum_requirements text,
                    recommended_requirements text,
                    url varchar(500)
                );"""
            )

    except Exception as ex:
        print("[INFO] Error while working with PostgreSQL", ex)
        return

    start = 1
    while True:
        url = (
            f"https://store.steampowered.com/search/?page={start}"
        )

        headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0 (Edition Yx GX)',
        }

        r = requests.get(url=url, headers=headers)
        src = r.text
        soup = BeautifulSoup(src, 'lxml')
        game_blocks = soup.find_all('a', {'class': 'search_result_row'})
        if not game_blocks:
            break

        for block in game_blocks:
            name = block.find("span", {"class": "title"}).text.strip()
            cost = block.find("div", {"class": "search_price_discount_combined"}).text.strip()
            url = block.get("href")

            # Parse additional details for the game
            game_url = urljoin("https://store.steampowered.com/", url)
            game_page = requests.get(game_url, headers=headers)
            game_soup = BeautifulSoup(game_page.content, 'html.parser')

            # Description
            description = game_soup.find('div', {'class': 'game_description_snippet'})
            description_text = description.text.strip() if description else ""

            # Minimum Requirements
            minimum_requirements = ""
            min_req_block = game_soup.find('div', {'class': 'sysreq_contents'})
            if min_req_block:
                minimum_requirements = min_req_block.text.strip()

            # Recommended Requirements
            recommended_requirements = ""
            rec_req_block = game_soup.find('div', {'class': 'game_area_sys_req_full'})
            if rec_req_block:
                recommended_requirements = rec_req_block.text.strip()

            cur.execute("INSERT INTO game (name, cost, description, minimum_requirements, recommended_requirements, url) VALUES (%s, %s, %s, %s, %s, %s)",
                        (name, cost, description_text, minimum_requirements, recommended_requirements, url))
            connection.commit()

        start += 1

    cur.close()
    connection.close()
    print("[INFO] PostgreSQL was successfully closed")

# def check_new():
#     with open("news_dict.json") as file:
#         new_dict = json.load(file)
    
#     url = "https://store.steampowered.com/search/results"

#     headers = {
#         "accept": "*/*",
#         "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36 OPR/93.0.0.0 (Edition Yx GX)"
#     }

#     r = requests.get(url, headers=headers)
    
#     soup = BeautifulSoup(r.text, 'lxml')
#     all = soup.find_all("a", class_="responsive_search_name_combined")

#     for item in all:
#         item_url = item.get("href")

#         if item_url in new_dict:
#             continue
#         else:
#             # item_text = item.text.strip()
#             item_title = item.find("span", class_='title').text.strip()
#             item_other = item.find(class_='responsive_secondrow').text.strip()
#             item_price = item.find("div", class_='search_price').text.strip()
#             item_url = item["href"]
#             # print(f"{item_text}") 


#             new_dict[item_title] = {
#                 "item_other": item_other,
#                 "item_price": item_price,
#                 "item_url": item_url
#             }
#     with open("news_dict.json", "w") as file:
#         json.dump(new_dict, file, indent=4, ensure_ascii=False)
    
#     return new_dict

def main():
    get_all()


if __name__ == '__main__':
    main()