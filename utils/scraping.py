import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# URLs des catégories
URLS = {
    "Véhicules": "https://dakarvente.com/index.php?page=annonces_rubrique&url_categorie_2=vehicules&id=2&sort=&nb={}",
    "Motos": "https://dakarvente.com/index.php?page=annonces_categorie&id=3&sort=&nb={}",
    "Voitures en location": "https://dakarvente.com/index.php?page=annonces_categorie&id=8&sort=&nb={}",
    "Téléphones": "https://dakarvente.com/index.php?page=annonces_categorie&id=32&sort=&nb={}"
}

def scrap_data(base_url, max_pages=10):
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    all_data = []

    for page in range(1, max_pages + 1):
        url = base_url.format(page)
        driver.get(url)
        time.sleep(5)

        try:
            WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, ".item-inner.mv-effect-translate-1.mv-box-shadow-gray-1")))

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)

            containers = driver.find_elements(By.CSS_SELECTOR, ".item-inner.mv-effect-translate-1.mv-box-shadow-gray-1")

            for container in containers:
                try:
                    details = container.find_element(By.CLASS_NAME, 'content-desc').text.strip()
                    prices = container.find_elements(By.CLASS_NAME, 'content-price')
                    price = prices[0].text.replace('FCFA', '').replace(',', '').strip() if prices else "N/A"
                    location = prices[1].text.strip() if len(prices) > 1 else "N/A"
                    image_element = container.find_element(By.CSS_SELECTOR, "h2 a img")
                    image_url = image_element.get_attribute("src").strip()

                    all_data.append({'détails': details, 'prix': price, 'localisation': location, 'image URL': image_url})

                except Exception as e:
                    print("⚠️ Erreur lors de l'extraction d'une annonce :", e)

        except Exception as e:
            print(f"⚠️ Erreur sur la page {page}: {e}")

    driver.quit()
    return all_data