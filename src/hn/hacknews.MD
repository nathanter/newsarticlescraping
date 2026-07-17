# Introduction
scrape RSS. put into json. Good. This literally just looks at the rss and gets it into the form I want it.


# To run
python src/hn/hacknews.py --run

Make sure a directory called "hnposts" exists in the path where you are running it.


Json for each post will be structured as the below

tags will be preset
title will be the same as text
author name will be none
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