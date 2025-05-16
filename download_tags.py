# Download VocaDB tags as markdown with frontmatter

# Browse and filter with https://obsidian.md/

import time
from getpass import getpass

import diskcache as dc
import requests

WEBSITE = "https://vocadb.net"
CACHE_DIR = dc.Cache("cache")
PAGES_DIR = "pages"
DELAY = 2


def get_credentials_from_console() -> tuple[str, str]:
    """Prompt the user for credentials."""
    print("Please enter your credentials:")
    account_name = input("Account name: ").strip()
    password = getpass("Password: ").strip()

    if not account_name or not password:
        print("Credentials cannot be empty.")
        return get_credentials_from_console()

    return account_name, password


def cache_without_expiration():
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Module + Function name for uniqueness
            key = f"{func.__name__}_{args}"
            print(f"cache key is {key}")
            if key in CACHE_DIR:
                return CACHE_DIR[key]
            result = func(*args, **kwargs)
            CACHE_DIR.set(key, result, expire=None)
            return result

        return wrapper

    return decorator


@cache_without_expiration()
def get_all_tag_ids() -> list[int]:
    url = f"{WEBSITE}/api/tags/by-categories"
    tags_by_category = requests.get(url, timeout=10)
    tags_by_category.raise_for_status()
    all_tag_ids = []
    for category in tags_by_category.json():
        for tag in category["tags"]:
            all_tag_ids.append(tag["id"])
    print(f"Found {len(all_tag_ids)} tag ids")
    return all_tag_ids


@cache_without_expiration()
def get_tag_json(url, delay=DELAY, session=requests):
    r = session.get(url, timeout=10)
    r.raise_for_status()
    time.sleep(delay)
    return r.json()


def json_list_to_yaml(json_list) -> str:
    lines = "\n".join([f"- {item}" for item in json_list])
    return f"\n{lines}"


def tag_json_to_markdown(tag_json) -> tuple[str, str]:
    filename = tag_json["urlSlug"]
    markdown = ["---"]
    markdown.append(f"url: {WEBSITE}/T/{tag_json['id']}")
    markdown.append(f"name: {tag_json['name']}")
    additional_names = tag_json["additionalNames"].split(", ")
    markdown.append(f"additionalNames: {json_list_to_yaml(additional_names)}")

    try:
        markdown.append(f"parent: \"[[{tag_json['parent']['urlSlug']}]]\"")
    except KeyError:
        markdown.append('parent: "[[parentless]]"')

    related_tags = [f'"[[{tag["urlSlug"]}]]"' for tag in tag_json["relatedTags"]]
    markdown.append(f"related:{json_list_to_yaml(related_tags)}")

    json_lists = ["mappedNicoTags", "newTargets"]
    for json_list in json_lists:
        markdown.append(f"{json_list}:{json_list_to_yaml(tag_json[json_list])}")

    fields = ["commentCount", "createDate", "status"]
    for field in fields:
        markdown.append(f"{field}: {tag_json[field]}")

    stats = [
        "albumCount",
        "artistCount",
        "eventCount",
        "eventSeriesCount",
        "followerCount",
        "songListCount",
        "songCount",
    ]
    for stat in stats:
        markdown.append(f"{stat}: {tag_json['stats'][stat]}")

    links = [f"{link['url']}" for link in tag_json["webLinks"]]
    markdown.append(f"links: {json_list_to_yaml(links)}")

    picture_exists = "true" if "mainPicture" in tag_json else "false"
    markdown.append(f"picture: {picture_exists}")

    markdown.append("---\n")
    markdown.append(f"#{tag_json['categoryName'].replace(' ', '_')}\n")
    markdown.append(tag_json["description"]["original"])
    markdown.append("\n---\n")
    markdown.append(tag_json["description"]["english"])
    return filename, "\n".join(markdown)


if __name__ == "__main__":
    # Login to bypass the rate limit
    un, pw = get_credentials_from_console()
    login = {"userName": un, "password": pw}

    with requests.Session() as session:
        login_attempt = session.post("https://vocadb.net/api/users/login", json=login)
        login_attempt.raise_for_status()
        all_tag_ids = get_all_tag_ids()
        counter = 1

        for tag_id in all_tag_ids:
            url = f"{WEBSITE}/api/tags/{tag_id}/details"
            tag_json = get_tag_json(url, session=session)  # type: ignore
            filename, markdown = tag_json_to_markdown(tag_json)
            with open(f"{PAGES_DIR}/{filename}.md", "w", encoding="utf-8") as f:
                f.write(markdown)
            #print(markdown)
            #print("-----------------")
            print(f"Created {filename}: ({counter}/{len(all_tag_ids)})")
            print("\n------------------------------------")
            counter += 1
