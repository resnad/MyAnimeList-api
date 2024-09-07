import requests
from bs4 import BeautifulSoup
import sqlite3
import time
import random

# Set up SQLite database
conn = sqlite3.connect('top_anime.db')
c = conn.cursor()

# Create table if it doesn't exist
c.execute('''CREATE TABLE IF NOT EXISTS anime
             (rank INTEGER, title TEXT, href TEXT, score REAL, type_episodes TEXT, aired TEXT, members INTEGER)''')

def scrape_page(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    anime_list = []

    for anime in soup.select('tr.ranking-list'):
        rank = int(anime.select_one('td.rank span').text.strip())
        title = anime.select_one('div.di-ib h3 a').text.strip()
        href = anime.select_one('div.di-ib h3 a')['href']
        score = float(anime.select_one('td.score span').text.strip())
        info = anime.select_one('div.information').text.strip().split('\n')
        
        type_episodes = info[0].strip()
        aired = info[1].strip()
        members = int(info[2].strip().replace(',', '').split()[0])
        
        anime_info = (rank, title, href, score, type_episodes, aired, members)
        anime_list.append(anime_info)
    
    return anime_list

def insert_anime(anime_list):
    c.executemany('INSERT OR REPLACE INTO anime VALUES (?,?,?,?,?,?,?)', anime_list)
    conn.commit()

base_url = "https://myanimelist.net/topanime.php"
total_anime = 500
anime_per_page = 50

for offset in range(0, total_anime, anime_per_page):
    url = f"{base_url}?limit={offset}"
    print(f"Scraping page {offset // anime_per_page + 1}")
    
    anime_list = scrape_page(url)
    insert_anime(anime_list)
    
    # Random delay between 3 and 7 seconds
    delay = random.uniform(3, 7)
    print(f"Waiting for {delay:.2f} seconds before next request")
    time.sleep(delay)

print("Scraping completed. Data saved to top_anime.db")

# Close the database connection
conn.close()