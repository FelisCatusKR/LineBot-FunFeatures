import json
import re

import requests


class ImageNotProcessedError(Exception):
    pass


def duckduckgo_image_search(keywords: str) -> (str, str):
    url = "https://duckduckgo.com/"
    params = {"q": keywords}

    #   First make a request to above URL, and parse out the 'vqd'
    #   This is a special token, which should be used in the subsequent request
    res = requests.post(url, data=params)
    searchObj = re.search(r"vqd=([\d-]+)&", res.text, re.M | re.I)

    headers = {
        "accept": "application/javascript, */*; q=0.01",
        "accept-encoding": "*",
        "accept-language": "ko,en-US;q=0.7,en;q=0.3",
        "authority": "duckduckgo.com",
        "dnt": "1",
        "host": "duckduckgo.com",
        "referer": "https://duckduckgo.com/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0",
        "x-requested-with": "XMLHttpRequest",
    }
    params = (
        ("l", "wt-wt"),
        ("o", "json"),
        ("q", keywords),
        ("vqd", searchObj.group(1)),
        ("f", ",,,"),
        ("p", "-2"),
    )
    requestUrl = url + "i.js"

    try:
        res = requests.get(requestUrl, headers=headers, params=params)
        print(res.text)
        data = json.loads(res.text)
        obj = data["results"][0]
        thumb_link = obj["thumbnail"]
        img_link = obj["image"]
    except ValueError as e:
        raise ImageNotProcessedError
    else:
        return (img_link, thumb_link)
