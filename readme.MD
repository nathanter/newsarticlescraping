Setup of tools made to get good a bunch of substack articles and hackernews posts for model training using substack and hackernews respective RSS.

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