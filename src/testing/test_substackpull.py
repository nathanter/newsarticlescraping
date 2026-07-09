from src.substack.substack import getFullResponseFromSubStack
from src.substack.substack import setupURL
import json

def test_getRss():
    l = "natinyarn"
    #https://natinyarn.substack.com/feed is the target feed
    response = getFullResponseFromSubStack(setupURL(l))
    responseDict = response[0]
    # print(responseDict) # visual confirmation if needed
    assert responseDict["author"] == "Natin Yarn"
    assert responseDict["text"]



