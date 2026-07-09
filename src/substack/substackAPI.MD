# Introduction

Hopefully TOS compliant Substack Post scraper and Substack Post getter

Substack does not have an official API that can get feeds. The one that exists only returns things having to do with linkedin profiles. Does not return feed items.

Substack does have RSS. From what I understand RSS is a way of shipping/publishing data that platforms with alot of written content use to publish feeds. Different pages have different RSS. Effectively, there is an API endpoint that returns the RSS. 

Note tags and explore tabs do not have RSS. only publications/individual creators have RSS so they have to come from specific writers.
Cannot scrape substack due to TOS. Two possible workarounds
1. Using playwright to open a new browser does not subscribe to the TOS
2. Make a database of well known authors.

There will be an optional scraper. 

# Solution

- have a manutally updated database that stores different creators with tags. These creators will be associated with tags. Tags is specific to another project I'm developing this for so that feature will be toggleable.
- Database can be updated manually or with optional playwright scraper
- Then url is constructed for RSS each RSS feed and returns a json

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

# How is this likely to be used
- When finding new articles first scrape pay attention list. If unavailable scrape the excluded join with specific topics.