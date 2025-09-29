import json, requests, pandas as pd
from tqdm.auto import tqdm
from concurrent.futures import ThreadPoolExecutor
import os
from dotenv import load_dotenv
load_dotenv()

# initialize SEO API KEY
api_key = os.getenv('SEO_API_KEY')


# configure concurrent workers
MAX_WORKERS = 50

# configure dataforseo API endpoint
url = "https://api.dataforseo.com/v3/serp/google/organic/live/advanced"
headers = {
    'Authorization': api_key,
    'Content-Type': 'application/json'
}

def fetchKeywords(keywords, location_code, language_code):
    # fetch raw results
    def dataforseo(keyword):
        payload = json.dumps([{
            "keyword": keyword,
            "location_code": location_code,
            "language_code": language_code,
            "depth": 10,
            "group_organic_results": True,
            "load_async_ai_overview": True
        }])

        response = requests.request("POST", url, headers=headers, data=payload)
        return response.text

    # get relevant information from raw results
    def process_keyword(keyword):
        data = dataforseo(keyword)
        data = json.loads(data)

        return data['tasks'][0]['result']

    # create json file and download
    api_data = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as ex:
        for result in tqdm(ex.map(process_keyword, keywords),
            total=len(keywords),
            desc="Fetching data for keywords (parallel)"):
            api_data.append(result)

    ## save file
    api_dataframe = pd.DataFrame(api_data)
    file_name = 'api-result.json'
    api_dataframe.to_json(file_name)

    return api_dataframe