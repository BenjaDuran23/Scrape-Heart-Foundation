from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import os
import tempfile
import time

BASE_URL = "https://www.heartfoundation.org.au"

class RecipeScraper:
    def __init__(self):
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        # Sandbox de Chrome: requiere privilegios que el contenedor no concede.
        # El aislamiento lo da el contenedor + el usuario sin privilegios.
        chrome_options.add_argument("--no-sandbox")
        # Perfil efímero y propio de cada ejecución
        self._profile_dir = tempfile.mkdtemp(prefix="chrome-profile-")
        chrome_options.add_argument(f"--user-data-dir={self._profile_dir}")

        # En el contenedor el driver está fijado en build time (ver Dockerfile).
        # Fuera de él, Selenium Manager lo resuelve solo.
        driver_path = os.environ.get("CHROMEDRIVER")
        service = Service(executable_path=driver_path) if driver_path else Service()
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def navigate_to_recipes(self):
        """Navegate to main page"""
        self.driver.get(f"{BASE_URL}/recipes")
        time.sleep(5)

    def extract_recipe_urls(self):
        """Extracts visbile urls at the actual page"""
        try:
            recipe_links = WebDriverWait(self.driver, 10).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/recipes/']")))
            urls = set()

            for link in recipe_links:
                href = link.get_attribute('href')
                if href and '/recipes/' in href:
                    if not href.startswith('http'):
                        href = f"{BASE_URL}{href}"
                    urls.add(href)

        except Exception as e:
            print(f"Error extracting URLs: {e}")
        return urls

    def scroll_to_element(self, element):
        """Desplaza la página para que el elemento sea visible"""
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        time.sleep(1)

    def go_next_page(self):
        next_page_button = self.driver.find_element(By.XPATH, "//*[@aria-label='Go to next page']")

        if next_page_button:
            try:
                self.scroll_to_element(next_page_button)
                if next_page_button.is_enabled():
                    next_page_button.click()
                    return True
                else:
                    return False
            except Exception as e:
                print(f"Error trying to click next page button: {e}")
                return False
        return False

    def scrape_all_recipes(self):
        self.navigate_to_recipes()
        all_urls = set()

        while True:
            actual_page_urls = self.extract_recipe_urls()
            all_urls.update(actual_page_urls)
            if not self.go_next_page():
                break
        return all_urls

    def close(self):
        """Close chromedriver"""
        self.driver.quit()
