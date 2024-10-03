import requests
from bs4 import BeautifulSoup
import re
import clipboard
import json
from colorama import Fore, init


deckname = "karaika"
tag = ["日本語"]

# model name. like 'Basic'
modelname = "基础"
# front name. like 'Front'
frontname = "正面"
# back name. like 'Back'
backname = "背面"

do_get_img = False


init()
print()

while True:
    try:
        wd = input(Fore.YELLOW
                   + "enter the word you want search"
                   "(use clipboard as input if there is no input):"+Fore.RESET)
    except:
        print("canceled")
        exit()

    # use clipboard if no input
    if len(wd) == 0:
        wd = clipboard.paste()

    url = "https://www.weblio.jp/content/"+wd+"?dictCode=SGKDJ"
    select = 0

    # request
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    res = res.text

    # get div data
    soup = BeautifulSoup(res, "html.parser")
    data = soup.find_all("div", attrs={"class": "Sgkdj"})
    if len(data) < 1:
        print("nothing found.")
        continue

    # list all options. let user choose
    if len(data) > 1:
        meaning = ""

        for i in range(len(data)):
            ps = data[i].find_all("p")
            meaning = ""
            for p in ps:
                if p.text.find("読み方") == 0:
                    pns = p.text[4:]
                    continue
                meaning = meaning + p.text
            print("\ni=", i, ": ["+pns+"]"+meaning+"\n")

        i = int(input("enter the number you want:"))
    else:
        i = 0

    # get the data user chose
    data = data[i].find_all("p")
    pns = data[0].text[4:]+"<br/>" if data[0].text.find("読み方") == 0 else ""

    meaning = []
    for p in data:
        if p.text.find("読み方") == 0:
            continue
        meaning.append(p.text)
    meaning = "<br/>".join(meaning)

    # print("wd=", wd, "\npns=", pns, "\nmeaning=", meaning)

    # get the first picture in bing search
    if do_get_img:
        url = "https://cn.bing.com/images/search?q="+wd

        # request
        res = requests.get(url)
        res.encoding = res.apparent_encoding
        soup = BeautifulSoup(res.text, "html.parser")
        data = soup.find("div", attrs={"class": "img_cont hoff"})
        img = data.img["src"]

        filetype = soup.find("div", attrs={"class": "img_info hon"})
        filetype = re.match(r'^.*\s(.*?)$', filetype.span.text).group(1)
        # print("filetype=", filetype)

    # invoke anki
    end_str = "<br/>" if do_get_img else ""
    back = pns + meaning + end_str
    anki_url = "http://localhost:8765"

    # send anki query to gui add cards
    if do_get_img:
        anki_query_data = {
            "action": "guiAddCards",
            "version": 6,
            "params": {
                "note": {
                    "deckName": deckname,
                    "modelName": modelname,
                    "fields": {
                        frontname: wd,
                        backname: back,
                    },
                    "tags": tag,
                    "picture": [{
                        "url": img,
                        "filename": wd+"."+filetype,
                        "fields": [
                            backname
                        ]
                    }]
                }
            }
        }
    else:
        anki_query_data = {
                "action": "guiAddCards",
                "version": 6,
                "params": {
                    "note": {
                        "deckName": deckname,
                        "modelName": modelname,
                        "fields": {
                            frontname: wd,
                            backname: back,
                        },
                        "tags": tag,
                    }
                }
        }

    print(json.dumps(anki_query_data, indent=4, ensure_ascii=False))
    res = requests.post(anki_url, json=anki_query_data)
    res.encoding = res.apparent_encoding
    res = res.text
    print(res)
