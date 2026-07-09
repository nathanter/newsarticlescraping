
import feedparser
from bs4 import BeautifulSoup
import json
import datetime

class SubstackException(Exception):
    pass


# raised only when the feed URL itself is gone (HTTP 404/410), so callers can
# tell a permanently-dead publication apart from a transient block/timeout
class FeedNotFoundException(SubstackException):
    pass


def setupURL(contentCreatorName: str) -> str:
    return(f"https://{contentCreatorName}.substack.com/feed")


# Takes in a list of one stubstack url. Gets the feed response. 
def getFullResponseFromSubStack(feedUrl: str, date=None) -> list[dict]:
    jsonResponse = []
    rss = feedparser.parse(feedUrl)

    # 404/410 means the publication no longer exists at this URL. check this
    # before bozo, since a 404 also trips bozo (the body isn't valid feed XML).
    if rss.get("status") in (404, 410):
        raise FeedNotFoundException(f"Feed '{feedUrl}' does not exist (HTTP {rss.status})")

    # feedparser sets bozo when the feed couldn't be cleanly fetched/parsed
    # (misspelled URL, DNS failure, 403 block, non-XML response, ...).
    if rss.bozo:
        print("bozo failure")
        raise SubstackException(f"Could not parse feed '{feedUrl}': {rss.bozo_exception}")
        

    entries = rss.entries
    if len(entries) == 0:
        print("empty failure")
        raise SubstackException(f"Feed '{feedUrl}' returned no entries")

    author = entries[0].get("author","")

    # a naive cutoff is assumed to be UTC so it can be compared to feed dates
    if date is not None and date.tzinfo is None:
        date = date.replace(tzinfo=datetime.timezone.utc)

    for article in entries:
        # feedparser gives published_parsed as a UTC struct_time, or None when undated
        publishedStruct = article.get("published_parsed")
        publishedDate = (
            datetime.datetime(*publishedStruct[:6], tzinfo=datetime.timezone.utc)
            if publishedStruct else None
        )

        # if date is defined just skip loop if publihed date is < date
        if date is not None and publishedDate is not None and publishedDate < date:
            continue

        jsonEntry = {}
        jsonEntry["title"] = article.get("title", "")
        jsonEntry["author"] = author
        jsonEntry["source"] = article.link
        # ISO-8601 when present, else "" (the original default for undated posts)
        jsonEntry["date"] = publishedDate.isoformat() if publishedDate else ""
        rawHTML = article.get("content",[{}])[0].get("value")
    
        if rawHTML == None: # is paywalled just leave
            continue

        finalText = BeautifulSoup(rawHTML, "html.parser").get_text(separator="\n").strip()
        jsonEntry["text"] = finalText
        jsonResponse.append(jsonEntry)  

    # return the collected articles; callers serialize at the API boundary
    return jsonResponse

    

        


        
    


    


