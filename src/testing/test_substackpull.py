from src.substack.substack import getFullResponseFromSubStack
from src.substack.substack import setupURL
import json

def test_getRss():
    l = "natinyarn"
    #https://natinyarn.substack.com/feed is the target feed
    response = getFullResponseFromSubStack(setupURL(l))
    responseDict = json.loads(response)[0]
    # print(responseDict) # visual confirmation if needed
    assert responseDict["Author"] == "Natin Yarn"
    assert responseDict["text"]



