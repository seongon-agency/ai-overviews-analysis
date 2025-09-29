import json
import pandas as pd

def loadAPI():
    with open('api-result.json', 'r', encoding='utf-8', errors='replace') as file:
        data = json.load(file) 
    api_dataframe = pd.DataFrame(data)
    return api_dataframe

loadAPI()