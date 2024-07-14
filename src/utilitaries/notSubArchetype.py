import requests

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
                text = res["parse"]["text"]["*"]
                if("not a sub-archetype" in text):
                    print(line.strip() + " IS NOT SUB-ARCHETYPE")
            except:
                print(line.strip() + " BUGGED ")

            url = YUGIPEDIA_URL + line.replace(" ", "_").strip() + "_(archetype)"
            res = requests.get(url, headers=headers).json()
            try:
                text = res["parse"]["text"]["*"]
                if("not a sub-archetype" in text):
                    print(line.strip() + " IS NOT SUB-ARCHETYPE")
            except:
                pass

main()