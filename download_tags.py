# Export VocaDB tags as markdown with front matter
#
# Browse and filter with Obsidian:
# https://help.obsidian.md/plugins/search#Search+properties

import time
from getpass import getpass

import diskcache as dc
import requests

# TODO update tag metadata based on activityEntry
# https://vocadb.net/api/activityEntries?entryType=Tag&fields=Entry&maxResults=5

# TODO verify front matter

WEBSITE = "https://vocadb.net"
CACHE_DIR = dc.Cache("cache")
PAGES_DIR = "pages"

TAG_COUNTER = 1  # adjust to prevent rewrites if interrupted often
MIN_DELAY = 0.5  # seconds between API requests
DYNAMIC_DELAY = True  # sleep based on response time
TIMEOUT = 20
PRINT_MARKDOWN_TO_CONSOLE = False

DISPLAY_RELATED_TAGS = True  # Set false for tree-shaped graph
CREATE_PARENTLESS_NODE = True

# global helper variables for console logging
request_count = 1
total_response_time = 0


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
            key = f"{func.__name__}_{args}"
            # print(f"cache key is {key}")
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
    tags_by_category = requests.get(url, timeout=TIMEOUT)
    tags_by_category.raise_for_status()
    all_tag_ids = []
    for category in tags_by_category.json():
        for tag in category["tags"]:
            all_tag_ids.append(tag["id"])
    print(f"Found {len(all_tag_ids)} tag ids")
    return all_tag_ids


@cache_without_expiration()
def get_tag_json(url, delay=MIN_DELAY, session=requests):
    start_time = time.time()
    r = session.get(url, timeout=TIMEOUT)

    r.raise_for_status()
    end_time = time.time()
    response_time = round(1000 * (end_time - start_time))
    global request_count  # noqa: PLW0603
    global total_response_time  # noqa: PLW0603
    total_response_time += response_time
    mean_response_time = round(total_response_time / request_count)
    print(f"Got {url} in {response_time}ms ({mean_response_time}ms on avg)")
    request_count += 1
    if DYNAMIC_DELAY:
        delay = max(delay, round(response_time / 1000, 1))
    print(f"Sleeping for {delay} seconds...")
    time.sleep(delay)
    return r.json()


def json_list_to_yaml(json_list) -> str:
    lines = "\n".join([f"- {item}" for item in json_list])
    return f"\n{lines}"


def tag_json_to_markdown(tag_json) -> tuple[str, str]:
    markdown = ["---"]

    markdown.append(f"url: {WEBSITE}/T/{tag_json['id']}")
    markdown.append(f"name: {tag_json['name']}")

    additional_names = tag_json["additionalNames"].split(", ")
    markdown.append(f"additionalNames: {json_list_to_yaml(additional_names)}")

    if CREATE_PARENTLESS_NODE:
        try:
            markdown.append(f"parent: \"[[{tag_json['parent']['urlSlug']}]]\"")
        except KeyError:
            markdown.append('parent: "[[parentless]]"')

    if DISPLAY_RELATED_TAGS:
        related_tags = [f'"[[{tag["urlSlug"]}]]"' for tag in tag_json["relatedTags"]]
        markdown.append(f"related:{json_list_to_yaml(related_tags)}")

    json_lists = ["mappedNicoTags", "newTargets"]
    for json_list in json_lists:
        markdown.append(f"{json_list}:{json_list_to_yaml(tag_json[json_list])}")

    simple_fields = ["commentCount", "createDate", "status"]
    for field in simple_fields:
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

    description_length = len(tag_json["description"]["original"]) + len(
        tag_json["description"]["english"]
    )
    markdown.append(f"descriptionLength: {description_length}")
    markdown.append("---\n")  # front matter over

    markdown.append(f"#{tag_json['categoryName'].replace(' ', '_')}\n")
    markdown.append(tag_json["description"]["original"].replace(" #", ""))
    markdown.append("\n---\n")  # description separator
    markdown.append(tag_json["description"]["english"].replace(" #", ""))

    filename = tag_json["urlSlug"]
    return filename, "\n".join(markdown)


if __name__ == "__main__":
    # Login to bypass the rate limit
    un, pw = get_credentials_from_console()
    login = {"userName": un, "password": pw}

    with requests.Session() as session:
        login_attempt = session.post(f"{WEBSITE}/api/users/login", json=login)
        login_attempt.raise_for_status()
        all_tag_ids = get_all_tag_ids()

        for tag_id in all_tag_ids[TAG_COUNTER - 1 :]:
            url = f"{WEBSITE}/api/tags/{tag_id}/details"
            tag_json = get_tag_json(url, session=session)  # type: ignore
            filename, markdown = tag_json_to_markdown(tag_json)
            with open(f"{PAGES_DIR}/{filename}.md", "w", encoding="utf-8") as f:
                f.write(markdown)

            if PRINT_MARKDOWN_TO_CONSOLE:
                print(markdown)
                print("-----------------")
            entries_left = len(all_tag_ids) - TAG_COUNTER
            mean_response_time_ms = round(total_response_time / request_count)
            total_response_delay_ms = entries_left * mean_response_time_ms
            total_entry_delay_ms = entries_left * MIN_DELAY * 1000
            time_left = round(
                (total_entry_delay_ms + total_response_delay_ms) / 1000 / 60
            )

            print(
                f"Exported tag {filename} ({TAG_COUNTER}/{len(all_tag_ids)}), {time_left} mins left"
            )
            print("------------------------------------")
            TAG_COUNTER += 1
