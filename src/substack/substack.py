
import feedparser
from bs4 import BeautifulSoup
import json



class SubstackException(Exception):
    pass


def setupURL(contentCreatorName: str) -> str:
    return(f"https://{contentCreatorName}.substack.com/feed")


# Takes in a list of one stubstack url. Gets the feed response. 
def getFullResponseFromSubStack(feedUrl:str) -> json:
    jsonResponse = []
    rss = feedparser.parse(feedUrl)

    # feedparser sets bozo when the feed couldn't be cleanly fetched/parsed
    # (misspelled URL, DNS failure, 403 block, non-XML response, ...).
    if rss.bozo:
        raise SubstackException(f"Could not parse feed '{feedUrl}': {rss.bozo_exception}")

    entries = rss.entries
    if len(entries) == 0:
        raise SubstackException(f"Feed '{feedUrl}' returned no entries")

    author = entries[0].author


    for article in entries:
        jsonEntry = {}
        jsonEntry["Author"] = author
        jsonEntry["source"] = article.link
        jsonEntry["date"] = article.get("published", "")
        rawHTML = article.get("content",[{}])[0].get("value")
    
        if rawHTML == None:
            raise SubstackException(f"failed on {jsonEntry["source"]}")

        finalText = BeautifulSoup(rawHTML, "html.parser").get_text(separator="\n").strip()
        jsonEntry["text"] = finalText
        jsonResponse.append(jsonEntry)  

    # serialize the list of dicts into a JSON-formatted string and return it
    return json.dumps(jsonResponse)

    

        


        
    


    


