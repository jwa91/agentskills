#!/usr/bin/env python3
# /// script
# dependencies = ["certifi"]
# ///
"""Search YouTube for educational videos relevant to a lesson topic.

NOTE: This script scrapes YouTube HTML (ytInitialData). YouTube changes
their HTML structure frequently — if this breaks, the fallback is to
ask the user to search YouTube manually and paste the URL.

Usage:
    uv run .agents/skills/interactive-learner/scripts/find-videos.py "kubernetes pods explained" [--max 5]

Returns JSON array of video results that Claude can evaluate for inclusion.
This script uses YouTube's search page (no API key needed).
"""

import argparse
import json
import re
import ssl
import urllib.parse
import urllib.request

import certifi


def search_youtube(query, max_results=5):
    """Search YouTube and extract video info from the page."""
    encoded = urllib.parse.quote(query)
    url = f"https://www.youtube.com/results?search_query={encoded}"

    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )

    ctx = ssl.create_default_context(cafile=certifi.where())

    try:
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            html = resp.read().decode("utf-8")
    except Exception as e:
        return {"error": f"Failed to fetch: {e}"}

    # Extract video data from ytInitialData JSON
    match = re.search(r"var ytInitialData = ({.*?});</script>", html)
    if not match:
        return {"error": "Could not parse YouTube results"}

    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError:
        return {"error": "JSON parse failed"}

    results = []
    try:
        contents = data["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"][
            "sectionListRenderer"
        ]["contents"][0]["itemSectionRenderer"]["contents"]
    except (KeyError, IndexError):
        return {"error": "Could not find video results in page"}

    for item in contents:
        vid = item.get("videoRenderer")
        if not vid:
            continue

        video_id = vid.get("videoId", "")
        title = ""
        try:
            title = vid["title"]["runs"][0]["text"]
        except (KeyError, IndexError):
            pass

        channel = ""
        try:
            channel = vid["ownerText"]["runs"][0]["text"]
        except (KeyError, IndexError):
            pass

        duration = ""
        try:
            duration = vid["lengthText"]["simpleText"]
        except KeyError:
            pass

        views = ""
        try:
            views = vid["viewCountText"]["simpleText"]
        except KeyError:
            pass

        published = ""
        try:
            published = vid["publishedTimeText"]["simpleText"]
        except KeyError:
            pass

        description = ""
        try:
            snippets = vid["detailedMetadataSnippets"][0]["snippetText"]["runs"]
            description = "".join(s["text"] for s in snippets)
        except (KeyError, IndexError):
            pass

        results.append(
            {
                "video_id": video_id,
                "title": title,
                "channel": channel,
                "duration": duration,
                "views": views,
                "published": published,
                "description": description,
                "url": f"https://www.youtube.com/watch?v={video_id}",
                "embed_url": f"https://www.youtube.com/embed/{video_id}",
            }
        )

        if len(results) >= max_results:
            break

    return results


def main():
    parser = argparse.ArgumentParser(description="Search YouTube for educational videos")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--max", type=int, default=5, help="Max results")
    args = parser.parse_args()

    results = search_youtube(args.query, args.max)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
