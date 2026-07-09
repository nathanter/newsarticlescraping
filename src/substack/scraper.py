import requests
from time import sleep

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36"
}   


def list_all_categories() -> dict[str, int]:
    """
    Get name / id representations of all newsletter categories

    Returns
    -------
    List[Tuple[str, int]]
        List of tuples containing (category_name, category_id)
    """
    endpoint_cat = "https://substack.com/api/v1/categories"
    r = requests.get(endpoint_cat, headers=HEADERS, timeout=30)
    r.raise_for_status()
    categories = dict()
    for i in r.json():
        categories[i["name"]]  = i["id"]
    return categories


def getUsersinCategory(id:int) -> list[str]:
    pages = 5
    url = f"https://substack.com/api/v1/category/public/{id}/all?page="
    #
    allAuthors = []
    for page in range(1, pages + 1):
        finalUrl = url + str(page)
        r = requests.get(finalUrl, headers=HEADERS, timeout=30)
        r.raise_for_status()
        sleep(2)
        resp = r.json()
        newsletters = resp.get("publications", [])
        for pub in newsletters:
            handle = pub.get("author_handle")
            if handle:
                allAuthors.append(handle)
    return allAuthors
