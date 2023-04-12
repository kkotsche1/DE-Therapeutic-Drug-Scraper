import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from time import sleep
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


url = "https://www.pharmawiki.ch/wiki/index.php?wiki=Wirkstoffe"
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
soup = BeautifulSoup(requests.get(url).text, "html.parser")
links = soup.find_all("li", class_="general")
list_of_dicts = []
driver.get("https://www.gelbe-liste.de/")
time.sleep(2)
driver.find_element_by_xpath('//*[@id="onetrust-accept-btn-handler"]').click()
timeout = 10
wait = WebDriverWait(driver, timeout)

for _ in links:

    try:
        drug = {}
        drug["name"] = _.text
        link = _.find("a")
        link = f"https://www.pharmawiki.ch/wiki/{link['href']}"

        request = requests.get(link).text
        soup = BeautifulSoup(request, "html.parser")
        print("-----------",_.text)
        abstract = soup.find(class_="sidenote_text").text
        drug["abstract"] = abstract


        paragraphs = soup.find_all("p")
        for paragraph in paragraphs:
            if "synonym:" in paragraph.text:
                drug["synonyme"] = paragraph.text.replace("synonym: ","")
        subtitles = soup.find_all(id="subtitle")


        for title in subtitles:
            if title.text == "siehe auch":
                subtitles.remove(title)
            if title.text == "Literatur":
                subtitles.remove(title)
            if title.text == "Autor":
                subtitles.remove(title)

        for title in subtitles:
            text_title = title.text
            if text_title != "Literatur":

                if text_title == "Struktur und Eigenschaften":
                    text_title = "struktur"

                if " " in text_title:
                    text_title = "unerwuenschte_wirkungen"


                text = title.find_next("p")
                drug[text_title.lower()] = text.text

        try:
            driver.get("https://www.gelbe-liste.de/")
            element_present = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/nav/div[1]/div/div[1]/div/div/form/div[1]/input[1]' )))
            search_bar = driver.find_element_by_xpath("/html/body/nav/div[1]/div/div[1]/div/div/form/div[1]/input[1]")
            search_bar.send_keys(_.text)
            driver.find_element_by_xpath('/html/body/nav/div[1]/div/div[1]/div/div/form/div[1]/span/button/i').click()
            element_present = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'product-list')))
            list = driver.find_element_by_class_name("product-list")
            list = list.find_elements_by_tag_name("h5")
            handelsnamen = ""
            for item in list:
                handelsnamen += f"{item.text}, "
            drug["handelsnamen"] = handelsnamen
        except:
            print("--------------------------Didnt get Handelsnamen--------------------------------")

        list_of_dicts.append(drug)
        print(drug)


    except:
        print(_.text, " Didn't Work")


