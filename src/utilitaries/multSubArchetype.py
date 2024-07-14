import requests
import re

YUGIPEDIA_URL = "https://yugipedia.com/wiki/api.php?action=parse&format=json&page="

def main():
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:127.0) Gecko/20100101 Firefox/127.0',
               'Accept-Encoding': 'gzip, deflate, br, zstd'
               }
    
    with open("allArchs.txt", "r", encoding="utf8") as f:
        for line in f.readlines():
            url = YUGIPEDIA_URL + line.replace(" ", "_").strip()
            res = requests.get(url, headers=headers).json()
            try:
                text = res["parse"]["properties"][1]["*"]
                regex = re.search(r".*sub-archetype.*\".*\".*\".*\".*archetypes", text, re.IGNORECASE)
                if(not regex is None):
                    print(line.strip() + " HAS SUB-ARCHETYPE")
            except:
                print(line.strip() + " BUGGED ")

            url = YUGIPEDIA_URL + line.replace(" ", "_").strip() + "_(archetype)"
            res = requests.get(url, headers=headers).json()
            try:
                text = res["parse"]["properties"][1]["*"]
                regex = re.search(r".*sub-archetype.*\".*\".*\".*\".*archetypes", text, re.IGNORECASE)
                if(not regex is None):
                    print(line.strip() + "_(archetype) HAS SUB-ARCHETYPE")
            except:
                pass

main()