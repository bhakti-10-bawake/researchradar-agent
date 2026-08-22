import requests
import feedparser
from urllib.parse import quote
from datetime import datetime


# ============================================================
# GOOGLE NEWS RSS
# ============================================================

def search_google_news(topic, competitors="", max_results=8):

    results = []

    queries = [
        f"{topic} latest developments",
        f"{topic} industry news",
        f"{topic} technology"
    ]

    competitor_list = [
        c.strip()
        for c in competitors.split(",")
        if c.strip()
    ]

    for competitor in competitor_list:
        queries.append(
            f"{competitor} {topic}"
        )

    seen_titles = set()

    for query in queries:

        try:

            encoded_query = quote(query)

            url = (
                "https://news.google.com/rss/search?"
                f"q={encoded_query}"
                "&hl=en-IN"
                "&gl=IN"
                "&ceid=IN:en"
            )

            feed = feedparser.parse(url)

            for entry in feed.entries:

                if len(results) >= max_results:
                    break

                title = entry.get(
                    "title",
                    "Untitled"
                ).strip()

                title_key = title.lower()

                if title_key in seen_titles:
                    continue

                seen_titles.add(title_key)

                summary = entry.get(
                    "summary",
                    ""
                )

                published = entry.get(
                    "published",
                    "Recent"
                )

                link = entry.get(
                    "link",
                    ""
                )

                source_name = "Google News"

                if hasattr(entry, "source"):

                    source_name = entry.source.get(
                        "title",
                        "Google News"
                    )

                organization = "Industry"

                for competitor in competitor_list:

                    if competitor.lower() in title.lower():

                        organization = competitor

                        break

                important_words = [
                    "launch",
                    "acquisition",
                    "investment",
                    "funding",
                    "patent",
                    "breakthrough",
                    "partnership",
                    "expansion",
                    "research",
                    "regulation",
                    "technology"
                ]

                text = (
                    title + " " + summary
                ).lower()

                importance = "High"

                if not any(
                    word in text
                    for word in important_words
                ):

                    importance = "Medium"

                results.append({

                    "tool": "Google News",

                    "type": "Industry Intelligence",

                    "topic": topic,

                    "title": title,

                    "summary": summary,

                    "organization": organization,

                    "importance": importance,

                    "source": source_name,

                    "date": published,

                    "url": link,

                    "signal":
                        f"Industry development detected in {topic}"

                })

        except Exception:
            continue

    return results


# ============================================================
# ARXIV API
# ============================================================

def search_arxiv(topic, max_results=5):

    results = []

    try:

        encoded_topic = quote(
            topic
        )

        url = (
            "https://export.arxiv.org/api/query?"
            f"search_query=all:{encoded_topic}"
            f"&start=0"
            f"&max_results={max_results}"
            f"&sortBy=submittedDate"
            f"&sortOrder=descending"
        )

        feed = feedparser.parse(url)

        for entry in feed.entries:

            title = entry.get(
                "title",
                "Untitled"
            ).replace(
                "\n",
                " "
            ).strip()

            summary = entry.get(
                "summary",
                "No abstract available."
            ).replace(
                "\n",
                " "
            ).strip()

            authors = [
                author.name
                for author in entry.get(
                    "authors",
                    []
                )
            ]

            published = entry.get(
                "published",
                "Unknown"
            )

            arxiv_url = entry.get(
                "id",
                ""
            )

            results.append({

                "tool": "arXiv",

                "type": "Academic Research",

                "topic": topic,

                "title": title,

                "summary": summary,

                "organization":
                    "Academic Research",

                "importance": "High",

                "source": "arXiv",

                "date": published,

                "url": arxiv_url,

                "authors": authors,

                "signal":
                    f"Academic research activity detected in {topic}"

            })

    except Exception:
        return []

    return results


# ============================================================
# OPENALEX API
# ============================================================

def search_openalex(topic, max_results=5):

    results = []

    try:

        encoded_topic = quote(
            topic
        )

        url = (
            "https://api.openalex.org/works"
            f"?search={encoded_topic}"
            f"&per-page={max_results}"
            "&sort=publication_date:desc"
        )

        response = requests.get(
            url,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        for work in data.get(
            "results",
            []
        ):

            title = work.get(
                "title",
                "Untitled"
            )

            abstract = (
                "Abstract not available."
            )

            abstract_data = work.get(
                "abstract_inverted_index"
            )

            if abstract_data:

                words = []

                for word, positions in (
                    abstract_data.items()
                ):

                    for position in positions:

                        words.append(
                            (
                                position,
                                word
                            )
                        )

                words.sort(
                    key=lambda x: x[0]
                )

                abstract = " ".join(
                    word
                    for _, word in words
                )

            publication_date = work.get(
                "publication_date",
                "Unknown"
            )

            work_url = work.get(
                "doi"
            )

            if not work_url:

                work_url = work.get(
                    "id",
                    ""
                )

            authorships = work.get(
                "authorships",
                []
            )

            authors = []

            for author_data in authorships:

                author = author_data.get(
                    "author",
                    {}
                )

                name = author.get(
                    "display_name"
                )

                if name:
                    authors.append(name)

            institutions = []

            for author_data in authorships:

                for institution in author_data.get(
                    "institutions",
                    []
                ):

                    name = institution.get(
                        "display_name"
                    )

                    if name and name not in institutions:

                        institutions.append(
                            name
                        )

            results.append({

                "tool": "OpenAlex",

                "type": "Scholarly Research",

                "topic": topic,

                "title": title,

                "summary": abstract,

                "organization":
                    ", ".join(institutions)
                    if institutions
                    else "Academic Research",

                "importance": "Medium",

                "source": "OpenAlex",

                "date": publication_date,

                "url": work_url,

                "authors": authors,

                "institutions": institutions,

                "signal":
                    f"Scholarly research activity detected in {topic}"

            })

    except Exception:
        return []

    return results


# ============================================================
# AUTONOMOUS TOOL SELECTION
# ============================================================

def select_tools(topic, competitors=""):

    topic_lower = topic.lower()

    tools = []

    # --------------------------------------------------------
    # News is useful for almost every competitive-intelligence
    # investigation.
    # --------------------------------------------------------

    tools.append("Google News")

    # --------------------------------------------------------
    # Research-heavy topics should use academic sources.
    # --------------------------------------------------------

    research_keywords = [

        "research",
        "science",
        "scientific",
        "paper",
        "papers",
        "study",
        "academic",
        "algorithm",
        "machine learning",
        "artificial intelligence",
        "quantum",
        "robotics",
        "biotechnology",
        "nanotechnology",
        "physics",
        "chemistry",
        "medicine",
        "computer vision",
        "natural language",
        "deep learning"

    ]

    if any(
        keyword in topic_lower
        for keyword in research_keywords
    ):

        tools.append("arXiv")

        tools.append("OpenAlex")

    # --------------------------------------------------------
    # If no research-specific keyword is detected, still use
    # OpenAlex for broader scholarly discovery when useful.
    # --------------------------------------------------------

    elif len(topic.split()) >= 2:

        tools.append("OpenAlex")

    # --------------------------------------------------------
    # Remove duplicates while preserving order.
    # --------------------------------------------------------

    return list(
        dict.fromkeys(tools)
    )


# ============================================================
# RUN ALL SELECTED TOOLS
# ============================================================

def run_intelligence_tools(
    topic,
    competitors=""
):

    selected_tools = select_tools(
        topic,
        competitors
    )

    all_results = []

    tool_status = []

    # --------------------------------------------------------
    # GOOGLE NEWS
    # --------------------------------------------------------

    if "Google News" in selected_tools:

        news_results = search_google_news(
            topic,
            competitors
        )

        all_results.extend(
            news_results
        )

        tool_status.append({

            "tool": "Google News",

            "selected": True,

            "reason":
                "Current industry and competitor activity"

        })

    # --------------------------------------------------------
    # ARXIV
    # --------------------------------------------------------

    if "arXiv" in selected_tools:

        arxiv_results = search_arxiv(
            topic
        )

        all_results.extend(
            arxiv_results
        )

        tool_status.append({

            "tool": "arXiv",

            "selected": True,

            "reason":
                "Academic research detected as relevant"

        })

    # --------------------------------------------------------
    # OPENALEX
    # --------------------------------------------------------

    if "OpenAlex" in selected_tools:

        openalex_results = search_openalex(
            topic
        )

        all_results.extend(
            openalex_results
        )

        tool_status.append({

            "tool": "OpenAlex",

            "selected": True,

            "reason":
                "Broader scholarly research landscape"

        })

    # --------------------------------------------------------
    # Remove duplicate titles
    # --------------------------------------------------------

    unique_results = []

    seen = set()

    for item in all_results:

        title = item.get(
            "title",
            ""
        ).strip().lower()

        if not title:
            continue

        if title in seen:
            continue

        seen.add(title)

        unique_results.append(
            item
        )

    return {

        "selected_tools":
            selected_tools,

        "tool_status":
            tool_status,

        "findings":
            unique_results

    }