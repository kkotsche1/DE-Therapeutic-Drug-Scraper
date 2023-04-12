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
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't',
            'u', 'v', 'w', 'x', 'y', 'z']
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

for letter in alphabet:
    letter_list = []
    link = f"https://www.orpha.net/consor4.01/www/cgi-bin/Disease_Search_List.php?lng=DE&TAG={letter.upper()}"
    soup = BeautifulSoup(session.get(link).text, "html.parser")
    div = soup.find(id="result-box")
    links = div.find_all("a")

    for link in links[1:]:
        try:
            disease = {}
            soup = BeautifulSoup(session.get(f"https://www.orpha.net/consor4.01/www/cgi-bin/{link['href']}").text, "html.parser")
            disease["name"] = link.text
            if soup.find_all("h2")[2].text != link.text:
                disease["sub_name"] = soup.find_all("h2")[2].text


            # --------------------------- Accessing English Description if there is not a german one ----------------- #

            div = soup.find(class_="articleInfo")
            if div.find(class_="ad-alerte"):

                try:
                    disease["german_description"] = div.find("p").text
                except:
                    pass
                disease["english"] = 1
                link = f"https://www.orpha.net/consor4.01/www/cgi-bin/{div.find('a')['href']}"
                soup = BeautifulSoup(session.get(link).text, "html.parser")

                if soup.find(class_="title-h3"):
                    try:
                        div = soup.find(class_="title-h3")
                        disease["defenition"] = div.find_next("p").text
                    except:
                        pass




                if soup.find(class_="idData"):
                    try:
                        data=soup.find(class_="idData")
                        synonym_list = data.find("ul")
                        synonym_list_ = synonym_list.find_all("li")
                        synonyms = ""
                        for item in synonym_list_:
                            synonyms += f"{item.text}, "
                        disease["synonyms"] = synonyms
                    except:
                        pass


                    try:
                        for item in data.find_all("li"):
                            if ":" in item.text:
                                item = item.text.split(": ")
                                if item[0] == "ICD-10":
                                    item[0] = "icd_10"
                                if item[0].lower() != "synonym(s)":
                                    if item[1] != "-":
                                        disease[item[0].lower().replace(' ', '_')] = item[1]

                    except:
                        pass



                if soup.find(class_="articleInfo"):
                    try:
                        div = soup.find(class_="articleInfo")
                        if div.find("h3"):
                            entries = div.find_all("h3")

                            for entry in entries:

                                disease[f"{entry.text.lower().replace(' ', '_').strip()}"] = entry.find_next("p").text
                        else:

                            disease["summary"] = div.find("p").text
                    except:
                        pass


            else:
                disease["english"] = 0
                if soup.find(class_="title-h3"):
                    try:
                        div = soup.find(class_="title-h3")
                        disease["defenition"] = div.find_next("p").text
                    except:
                        pass



                if soup.find(class_="idData"):
                    try:
                        data=soup.find(class_="idData")
                        synonym_list = data.find("ul")
                        synonym_list_ = synonym_list.find_all("li")
                        synonyms = ""
                        for item in synonym_list_:
                            synonyms += f"{item.text}, "
                        disease["synonyms"] = synonyms
                    except:
                        pass


                    try:
                        for item in data.find_all("li"):
                            if ":" in item.text:
                                item = item.text.split(": ")
                                if item[0].lower() != "synonym(e)":
                                    if "valenz" in item[0]:
                                        item[0] = "prevalence"
                                    if "synonym" in item[0]:
                                        item[0] = "synonym(s)"
                                    if item[0] == "Erbgang" or item[0] == "Erbgang\n":
                                        item[0] = "inheritance"
                                    if item[0] == "Manifestationsalter" or item[0] == "Manifestationsalter\n":
                                        item[0] = "age_of_onset"
                                    if item[1] != "-":
                                        disease[item[0]] = item[1]
                    except:
                        pass

                if soup.find(class_="articleInfo"):
                    try:
                        div = soup.find(class_="articleInfo")
                        if div.find("h3"):
                            entries = div.find_all("h3")

                            for entry in entries:

                                title = entry.text

                                if title =="Klinische Beschreibung\n" or title =="Klinische Beschreibung":
                                    title = "clinical_description"
                                elif title == "Epidemiologie\n" or  title =="Epidemiologie":
                                    title = "epidemiology"
                                elif "tiologie" in title:
                                    title = "etiology"
                                elif title == "Differentialdiagnose\n" or title == "Differentialdiagnose":
                                    title="differential_diagnosis"
                                elif title == "Genetische Beratung\n" or title =="Genetische Beratung":
                                    title = "genetic_counseling"
                                elif title == "Management und Behandlung\n" or title =="Management und Behandlung":
                                    title = "management_and_treatment"
                                elif title == "Prognose\n" or title =="Prognose":
                                    title = "prognosis"
                                elif title == "Pränataldiagnostik\n" or title =="Pränataldiagnostik":
                                    title = "prenatal_diagnostic"
                                elif title == "Diagnostische Verfahren\n" or title =="Diagnostische Verfahren":
                                    title = "diagnostic_methods"



                                disease[title] = entry.find_next("p").text
                    except:
                        pass

                    else:
                        try:
                            disease["summary"] = div.find("p").text
                        except:
                            pass
            print(disease)
            letter_list.append(disease)
        except:
            pass

    import json

    with open(f'diseases_{letter}', 'w') as fout:
        json.dump(letter_list, fout)