import requests
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime


# ============================================================
# ARXIV TOOL
# ============================================================

def search_arxiv(topic, max_results=5):

    try:
        query = urllib.parse.quote(
            f"all:{topic}"
        )

        url = (
            "https://export.arxiv.org/api/query"
            f"?search_query={query}"
            f"&start=0"
            f"&max_results={max_results}"
            "&sortBy=submittedDate"
            "&sortOrder=descending"
        )

        response = requests.get(
            url,
            timeout=15,
            headers={
                "User-Agent":
                "ResearchRadar/1.0"
            }
        )

        response.raise_for_status()

        root = ET.fromstring(
            response.text
        )

        namespace = {
            "atom":
            "http://www.w3.org/2005/Atom"
        }

        results = []

        for entry in root.findall(
            "atom:entry",
            namespace
        ):

            title = entry.findtext(
                "atom:title",
                "",
                namespace
            ).strip().replace(
                "\n",
                " "
            )

            summary = entry.findtext(
                "atom:summary",
                "",
                namespace
            ).strip().replace(
                "\n",
                " "
            )

            published = entry.findtext(
                "atom:published",
                "",
                namespace
            )

            authors = []

            for author in entry.findall(
                "atom:author",
                namespace
            ):

                name = author.findtext(
                    "atom:name",
                    "",
                    namespace
                )

                if name:
                    authors.append(name)

            results.append({

                "title": title,

                "summary": summary,

                "source": "arXiv",

                "date": published[:10]
                if published
                else "Unknown",

                "organization":
                ", ".join(authors[:2])
                if authors
                else "Research Community",

                "importance": "High",

                "signal":
                "Recent academic research detected "
                "in the selected technology area."

            })

        return results

    except Exception as e:

        print(
            "arXiv error:",
            e
        )

        return []


# ============================================================
# OPENALEX TOOL
# ============================================================

def search_openalex(topic, max_results=5):

    try:

        encoded_topic = urllib.parse.quote(
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
            timeout=15,
            headers={
                "User-Agent":
                "ResearchRadar/1.0"
            }
        )

        response.raise_for_status()

        data = response.json()

        results = []

        for item in data.get(
            "results",
            []
        ):

            title = item.get(
                "title",
                "Untitled research"
            )

            publication_date = item.get(
                "publication_date",
                "Unknown"
            )

            authorships = item.get(
                "authorships",
                []
            )

            authors = []

            for author_data in authorships[:2]:

                author = author_data.get(
                    "author",
                    {}
                )

                name = author.get(
                    "display_name"
                )

                if name:
                    authors.append(name)

            results.append({

                "title": title,

                "summary":
                "Scholarly work identified "
                "through OpenAlex.",

                "source": "OpenAlex",

                "date": publication_date,

                "organization":
                ", ".join(authors)
                if authors
                else "Research Community",

                "importance": "Medium",

                "signal":
                "Scholarly activity related to "
                "the selected research area."

            })

        return results

    except Exception as e:

        print(
            "OpenAlex error:",
            e
        )

        return []


# ============================================================
# AUTONOMOUS INTELLIGENCE TOOL
# ============================================================

def run_intelligence_tools(
    topic,
    competitors
):

    print(
        "\nResearchRadar Intelligence Agent"
    )

    print(
        "Topic:",
        topic
    )

    print(
        "Competitors:",
        competitors
    )

    selected_tools = [
        "arXiv API",
        "OpenAlex API"
    ]

    print(
        "Selected tools:",
        selected_tools
    )

    # --------------------------------------------------------
    # CALL ARXIV
    # --------------------------------------------------------

    arxiv_results = search_arxiv(
        topic
    )

    print(
        "arXiv findings:",
        len(arxiv_results)
    )

    # --------------------------------------------------------
    # CALL OPENALEX
    # --------------------------------------------------------

    openalex_results = search_openalex(
        topic
    )

    print(
        "OpenAlex findings:",
        len(openalex_results)
    )

    # --------------------------------------------------------
    # COMBINE
    # --------------------------------------------------------

    findings = (
        arxiv_results
        + openalex_results
    )

    # --------------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------------

    unique_findings = []

    seen = set()

    for finding in findings:

        title = finding.get(
            "title",
            ""
        ).strip().lower()

        if not title:
            continue

        if title in seen:
            continue

        seen.add(title)

        unique_findings.append(
            finding
        )

    print(
        "Total findings:",
        len(unique_findings)
    )

    return {

        "selected_tools":
        selected_tools,

        "findings":
        unique_findings,

        "tool_status": [

            {
                "tool": "arXiv API",
                "status":
                "Success"
                if arxiv_results
                else "No results"
            },

            {
                "tool": "OpenAlex API",
                "status":
                "Success"
                if openalex_results
                else "No results"
            }

        ]

    }