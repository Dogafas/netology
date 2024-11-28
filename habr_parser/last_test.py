import requests
from bs4 import BeautifulSoup
from typing import List, Optional
import logging
import headers
from headers import user_agent_list
from variables import articleUrl, base_url, KEYWORDS
import re
from tqdm import tqdm

# Настройка логгирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class BaseWebScraper:
    def __init__(self, headers: dict):
        self.headers = headers
        # logging.info(f"Web scraper initialized with headers: {self.headers}")

    def fetch_page(self, url: str) -> Optional[str]:
        """Загружает страницу по заданному URL и возвращает её содержимое."""
        # logging.debug(f"Fetching page: {url}")
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            # logging.info(f"Successfully fetched page: {url}")
            return response.text
        except requests.RequestException as e:
            logging.error(f"Error fetching {url}: {e}")
            return None

    def url_extractor(self, content: str) -> List[str]:
        """Извлекает URL всех статей из содержимого страницы"""
        # logging.debug("Extracting URLs from content")
        soup = BeautifulSoup(content, 'html.parser')
        urls = [articleUrl + a['href'] for a in soup.find_all('a', class_='tm-title__link')]
        # logging.info(f"Extracted {len(urls)} URLs matching the pattern")
        return urls

    def check_keywords_in_article(self, url: str) -> Optional[str]:
        """Проверка совпадений с ключевыми словами"""
        # logging.debug(f"Checking keywords in article: {url}")
        response = requests.get(url)
        soup = BeautifulSoup(response.text, features='lxml')
        article_body = soup.find('div', class_='tm-article-presenter__body')
        if not article_body:
            # logging.error(f'Не удалось найти тело статьи на странице {url}')
            return None
        time_tag = (article_body.select_one('time')['datetime']).split('T')[0]
        header = soup.find('h1', class_='tm-title tm-title_h1').text

        found_keywords = []
        for keyword in KEYWORDS:
            if re.search(r'\b' + re.escape(keyword) + r'\b', article_body.text, re.IGNORECASE):
                found_keywords.append(keyword)

        if found_keywords:
            # logging.info(f'Найдено {"совпадение" if len(found_keywords)==1 else "несколько совпадений"} с ключевым{"ими" if len(found_keywords)!=1 else ""} слов{"" if len(found_keywords)==1 else "ами"}: {", ".join(found_keywords)} в статье {header} - {time_tag} - {url}')
            return f'{time_tag} - {header} - {url}'
        else:
            # logging.info(f'Совпадений не найдено в статье {url}')
            return None


def main():
    # logging.info("Starting the web scraper")
    scraper = BaseWebScraper(headers.get_random_headers(user_agent_list))
    content = scraper.fetch_page(base_url)
    if content:
        urls = scraper.url_extractor(content)
        results = []
        for url in tqdm(urls, desc="Ищем совпадения", bar_format="{l_bar}\033[32m{bar}\033[0m {n_fmt}/{total_fmt} \033[34m{percentage}%\033[0m"):
            result = scraper.check_keywords_in_article(url)
            if result:
                results.append(result)
        # После обработки всех статей, выводим результаты
        for result in results:
            print(result)

if __name__ == "__main__":
    main()