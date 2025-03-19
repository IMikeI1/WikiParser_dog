import requests
from bs4 import BeautifulSoup
import os
import json


class WikiParser:
    def __init__(self, url):
        self.url = url
        self.breeds_data = []

    def get_html(self):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
        }
        response = requests.get(self.url, headers=headers)
        if response.status_code == 200:
            return response.text
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return None

    def parse_html(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'class': 'wikitable sortable'})

        for row in table.find_all('tr')[1:]:
            columns = row.find_all(['td', 'th'])
            if len(columns) > 3:  # Поскольку нас интересует минимум 4 столбца
                name = columns[0].find('a').text.strip() if columns[0].find('a') else ''
                group = columns[1].text.strip()
                alternative_name = columns[2].text.strip() if len(columns) > 2 else ''
                img_tag = columns[3].find('img')
                photograph = img_tag['src'] if img_tag else ''

                self.breeds_data.append({
                    'name': name,
                    'group': group,
                    'alternative_name': alternative_name,
                    'image_url': photograph
                })

    def download_images(self):
        if not os.path.exists('dog_images'):
            os.makedirs('dog_images')

        for breed in self.breeds_data:
            image_url = breed['image_url']
            if image_url:
                image_filename = os.path.join('dog_images', f"{breed['name'].replace(' ', '_')}.jpg")
                response = requests.get(image_url)
                if response.status_code == 200:
                    with open(image_filename, 'wb') as img_file:
                        img_file.write(response.content)
                else:
                    print(f"Failed to download image for {breed['name']}")

    def write_data(self):
        with open('dog_breeds.json', 'w', encoding='utf-8') as json_file:
            json.dump(self.breeds_data, json_file, ensure_ascii=False, indent=4)

    def run(self):
        html = self.get_html()
        if html:
            self.parse_html(html)
            self.download_images()
            self.write_data()


# Использование
if __name__ == "__main__":
    url = 'https://commons.wikimedia.org/wiki/List_of_dog_breeds'
    parser = WikiParser(url)
    parser.run()