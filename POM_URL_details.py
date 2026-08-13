import re

import requests
from bs4 import BeautifulSoup

class DetailScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })


    def extract_recipe_details(self, url, html):
        try:
            soup = BeautifulSoup(html, 'html.parser')

            recipe = {
                'recipe_title': self._extract_title(soup),
                'recipe_ingredients': self._extract_ingredients(soup),
                'recipe_steps': self._extract_steps(soup),
                'recipe_tips': self._extract_tips(soup)
            }

            print(recipe)

            return recipe
        except Exception as e:
            print(f"Error extracting details from {url}: {e}")
            return None

    def _extract_title(self, soup) -> str:
        title = "No title"
        try:
            title_element = soup.find('h1')
            title = title_element.get_text(strip=True)
        except Exception as e:
            print(f"Error extracting title: {e}")
        return title

    def _extract_ingredients(self, soup) -> list:
        ingredients = []
        try:
            ingredient_title = soup.find('h4', string='Ingredients')

            if ingredient_title:
                father_container = ingredient_title.find_parent('div')
                ingredients = [li.get_text(strip=True) for li in father_container.find_all('li')]
                if not ingredients:
                    ingredients = [p.get_text(strip=True) for p in father_container.find_all('p')]
        except Exception as e:
            print(f"Error extracting ingredients: {e}")
        return ingredients

    def _extract_steps(self, soup):
        steps = []
        try:
            step_title = soup.find('h4', string='Method')

            if step_title:
                father_container = step_title.find_parent('div')
                steps = [p.get_text(strip=True) for p in father_container.find_all('p')]
        except Exception as e:
            print(f"Error extracting steps: {e}")
        return steps

    def _extract_tips(self, soup):
        tips = []
        try:
            tip_title = soup.find('h4', string=re.compile(r'^\s*Tips?\s*$', re.IGNORECASE))

            if tip_title:
                father_container = tip_title.find_parent('div')

            tips = [li.get_text(strip=True) for li in father_container.find_all('li')]
        except Exception as e:
            print(f"Error extracting tips: {e}")
        return tips

    def fetch_and_extract(self, url):
        """Obtiene una receta y extrae sus detalles"""
        try:
            print(f"Processing: {url}")
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            recipe = self.extract_recipe_details(url, response.text)
            return recipe
        except Exception as e:
            print(f"Error processing {url}: {e}")
            return {}

    def extract_detailed_data(self, urls_recipes):
        json_recipes = {}
        failed_recipes = []

        for url in urls_recipes:
            recipe = self.fetch_and_extract(url)

            if recipe:
                json_recipes[url] = recipe
            else:
                failed_recipes.append(recipe)

        if failed_recipes:
            print(f"The following recipes failed: {failed_recipes}")

        return json_recipes


