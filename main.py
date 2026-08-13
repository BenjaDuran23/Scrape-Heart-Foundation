import json

from POM_URLS import RecipeScraper
from POM_URL_details import DetailScraper


if __name__ == "__main__":
    try:
        scraper = RecipeScraper()
        detail_scraper = DetailScraper()
        
        urls_recipes = scraper.scrape_all_recipes()
        scraper.close()

        json_recipes = detail_scraper.extract_detailed_data(urls_recipes)

        # Save Data
        with open('data.json', 'w', encoding='utf-8') as file:
            json.dump(json_recipes, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Couldn't scrape all data: {e}")