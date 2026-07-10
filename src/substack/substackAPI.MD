# Introduction

Hopefully TOS compliant Substack Post scraper and Substack Post getter

The purpose of this project is to get training data for another model, it will be designed as such.

Substack does not have an official API that can get feeds. The one that exists only returns things having to do with linkedin profiles. Does not return feed items.

Substack does have RSS. From what I understand RSS is a way of shipping/publishing data that platforms with alot of written content use to publish feeds. Different pages have different RSS. Effectively, there is an API endpoint that returns the RSS. 

Note tags and explore tabs do not have RSS. only publications/individual creators have RSS so they have to come from specific writers.
Cannot scrape substack due to TOS. Two thigns to work around this
1. Make a database of well known authors. Query this independently
2. query public API endpoints to get list of authors and update the databse manually.



# Solution

- have a manutally updated database that stores different creators with tags. These creators will be associated with tags. Tags is specific to another project I'm developing this for so that feature will be toggleable.
- Database can be updated manually 
- Databse can also be updated by querying the public substack endpoint. This queries what seems to be an internal list of most popular creators by subscription statistics etc.
- Then url is constructed for RSS each RSS feed and returns a json. Before returning json filter for language, size of publications etc.

have a name and tags -> enter into database -> construct link -> input to database -> query and use each function to get data

Json for each post will be structured as the below
```json
[
{
    title: "title",
    tags: ["tag1","tag2"],
    source: "link"
    author: "Author Name"
    date: "date"
    text: "LONG TEXT"
}
]
```



# Database.
3 tables in the database. all are strings

| handle | Url |

| handle | tag |

| handle | (This table is used for subscribed authors and prioritization)

There needs to be an insert function.
there needs to be a function that constructs from a stored config file of sorts that has a list of subscribed authors

possible tags 
Art & Illustration, Business, Climate & Environment, Comics, Crypto, Culture, Design, Education, Faith & Spirituality, Fashion & Beauty, Fiction, Film & TV, Finance, Food & Drink, Health & Wellness, Health Politics, History, Home & Garden, Humor, International, Literature, Music, News, Parenting, Philosophy, Podcasts, Science, Sports, Technology, Travel, U.S. Politics, World Politics


# Quick notes on working with substack endpoints
- if you are building your own version of this project, be aware that often times parsing a substack will return a 302. This causes an error but can be solved by using the "subdomain" instead of the author handle. This occurs because substack allows you to have custom urls which means your rss has to be retrieved from there.

- Also there just seems to be empty/private substacks on the most popular. This is not build to handle them.

On my most recent run. These were the errors

bozo failure: https://authordeejames.substack.com/feed:400
bozo failure: https://brianklaas.substack.com/feed:301
bozo failure: https://businessofbrandspost.substack.com/feed:200
bozo failure: https://firesidenewsemail.substack.com/feed:400
bozo failure: https://ghsnark.substack.com/feed:200
bozo failure: https://joobaguitar.substack.com/feed:400

just bad requests. You can choose to remove them. For me there's so little and they might be added on future runs when I resetup the databse anyways.
# Usage
This is built with cli. You can also download and import the files and use them directly. Replace "python" in commands with the configuration you have.

## Setup Databse
```
python -m src.substack.getTraining setup # populate database with popular authors
```

## database info 
```
python -m src.substack.getTraining count
```

```
python -m src.substack.getTraining categories
```

## get articles
```
python -m src.substack.getTraining articles --tag "Technology" -o tech.json
```
to run without a specific tag, remove the -- tag and tag name.