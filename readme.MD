Setup of tools made to get good a bunch of substack articles and hackernews posts for model training using substack and hackernews respective RSS. Json is formatted for this project.

each tool returns a json file into a folder in the base directory. 
Json should be formatted as 
```json
[
{
    title: "title",
    tags: ["tag1","tag2"]
    source: "link"
    author: "Author Name"
    date: "date"
    text: "LONG TEXT"
}
]
```


# to run each set of tools

setup venv first:
```
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```
## substack
``` 
python -m newsarticleapi.substack.getTraining setup  
python -m newsarticleapi.substack.getTraining articles

```

## hn 
```
python newsarticleapi/hn/hacknews.py --run
```


## other
note: add wanted news rss to rsss.csv
follow format of link,Tag
```
python newsarticleapi/variousNewsRss/main.py --run
# only keep posts from the last N days (default: 1)
python newsarticleapi/variousNewsRss/main.py --run --days 7
```
