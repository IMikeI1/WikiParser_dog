import requests
from bs4 import BeautifulSoup
from typing import List, Tuple
import re


class WikiMovieParser:
    def __init__(self, url: str):
        self.url = url
        self.soup = None
        self.categories = []

    def fetch_page(self) -> None:
        response = requests.get(self.url)
        response.raise_for_status()
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def parse_categories(self) -> List[Tuple[str, str]]:
        if not self.soup:
            self.fetch_page()

        by_topic_section = None
        for heading in self.soup.find_all(['h2', 'h3']):
            if heading.get_text().strip() == 'By topic':
                by_topic_section = heading
                break

        if not by_topic_section:
            raise ValueError("Не удалось найти раздел 'By topic'")

        # Get all list items after the "By topic" section
        current = by_topic_section.find_next('ul')
        while current and current.name == 'ul':
            for item in current.find_all('li'):
                link = item.find('a')
                if link and link.get('href'):
                    category_name = link.get_text().strip()
                    href = link.get('href')
                    if not href.startswith('http'):
                        href = f"https://en.wikipedia.org{href}"
                    self.categories.append((category_name, href))
            current = current.find_next('ul')

    def save_to_file(self, filename: str = 'movie_categories.txt') -> None:
        if not self.categories:
            self.parse_categories()

        with open(filename, 'w', encoding='utf-8') as f:
            for category, url in self.categories:
                f.write(f"{category} - {url}\n")


def main():
    # URL of the Wikipedia page
    url = "https://en.wikipedia.org/wiki/Lists_of_films"

    parser = WikiMovieParser(url)

    try:
        parser.parse_categories()
        parser.save_to_file()
        print(" категории сохранить в файл 'movie_categories.txt'")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()