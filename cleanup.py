import os
import json

directory = r'diseases'
keys = []
for filename in os.listdir(directory):
    with open(rf"diseases/{filename}", "r") as file:
        dict = json.load(file)
        for disease in dict:

            for key in list(disease.keys()):
                if key.lower() not in keys:
                    keys.append(key.lower())


for key in keys:
    print(key)







