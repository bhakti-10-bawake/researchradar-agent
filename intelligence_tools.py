import re
import html
import requests
import urllib.parse
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime


# ============================================================
# RESEARCHRADAR INTELLIGENCE TOOLS
# ============================================================
#
# External intelligence sources:
#
# 1. arXiv
# 2. OpenAlex
# 3. Crossref
# 4. Semantic Scholar
# 5. Google News RSS
# 6. GDELT
#
# Main public interface used by app.py:
#
# - select_tools()
# - build_research_query()
# - build_research_queries()
# - run_intelligence_tools()
#
# ============================================================


# ============================================================
# CONFIGURATION
# ============================================================

HEADERS = {
    "User-Agent": (
        "ResearchRadar/1.0 "
        "(University Hackathon; "
        "Team TriX)"
    )
}

ARXIV_URL = (
    "https://export.arxiv.org/api/query"
)

OPENALEX_URL = (
    "https://api.openalex.org/works"
)

CROSSREF_URL = (
    "https://api.crossref.org/works"
)

SEMANTIC_SCHOLAR_URL = (
    "https://api.semanticscholar.org/"
    "graph/v1/paper/search"
)

GOOGLE_NEWS_RSS_URL = (
    "https://news.google.com/rss/search"
)

GDELT_URL = (
    "https://api.gdeltproject.org/api/v2/doc/doc"
)


# ============================================================
# COMMON TEXT CLEANING
# ============================================================

def clean_text(value):
    """
    Convert API text into clean human-readable text.

    Important for Google News RSS because RSS descriptions
    can contain raw HTML such as <a href="...">.
    """

    if value is None:
        return ""

    text = str(value)

    # Decode HTML entities.
    text = html.unescape(text)

    # Remove HTML tags.
    text = re.sub(
        r"<[^>]+>",
        " ",
        text
    )

    # Remove escaped HTML tags that may survive decoding.
    text = re.sub(
        r"&lt;[^&]*&gt;",
        " ",
        text
    )

    # Remove common leftover entities.
    text = text.replace(
        "&nbsp;",
        " "
    )

    text = text.replace(
        "&amp;",
        "&"
    )

    text = text.replace(
        "&quot;",
        '"'
    )

    text = text.replace(
        "&#39;",
        "'"
    )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    return text.strip()


# ============================================================
# REQUEST HELPER
# ============================================================

def safe_get(
    url,
    params=None,
    timeout=15
):
    """
    Safe HTTP GET wrapper.

    One API failing should not crash the entire
    ResearchRadar scan.
    """

    try:

        response = requests.get(
            url,
            params=params,
            timeout=timeout,
            headers=HEADERS
        )

        response.raise_for_status()

        return response

    except Exception as error:

        print(
            f"API request failed: "
            f"{url} -> {error}"
        )

        return None


# ============================================================
# WORD PROCESSING
# ============================================================

GENERIC_WORDS = {
    "the",
    "and",
    "for",
    "with",
    "from",
    "into",
    "this",
    "that",
    "these",
    "those",
    "are",
    "is",
    "was",
    "were",
    "will",
    "would",
    "could",
    "should",
    "can",
    "may",
    "using",
    "use",
    "used",
    "based",
    "develop",
    "developing",
    "development",
    "identify",
    "finding",
    "find",
    "explore",
    "exploring",
    "research",
    "researching",
    "analysis",
    "analyze",
    "understand",
    "investigate",
    "investigating",
    "study",
    "studying",
    "major",
    "emerging",
    "emerge",
    "directions",
    "direction",
    "recent",
    "latest",
    "current",
    "technology",
    "technologies",
    "area",
    "objective",
    "system",
    "systems",
    "information",
    "intelligence",
    "potential",
    "opportunities",
    "opportunity",
    "impact",
    "important",
    "important"
}


def normalize_words(text):
    """
    Extract meaningful alphanumeric words.
    """

    return re.findall(
        r"[a-zA-Z0-9]+",
        clean_text(text).lower()
    )


def meaningful_words(text):
    """
    Remove generic words so that relevance scoring
    focuses on actual concepts.
    """

    words = normalize_words(text)

    result = []

    for word in words:

        if len(word) < 3:
            continue

        if word in GENERIC_WORDS:
            continue

        if word not in result:
            result.append(word)

    return result


# ============================================================
# QUERY GENERATION
# ============================================================

def build_research_queries(
    topic,
    objective="",
    competitors=""
):
    """
    Build several focused research queries from:

    - topic
    - objective
    - competitors

    The system does not assume a specific domain.
    """

    topic = clean_text(topic)
    objective = clean_text(objective)
    competitors = clean_text(competitors)

    if not topic:
        return []

    topic_concepts = meaningful_words(
        topic
    )

    objective_concepts = meaningful_words(
        objective
    )

    queries = []

    # --------------------------------------------------------
    # QUERY 1
    # Exact user topic.
    # --------------------------------------------------------

    queries.append(
        f'"{topic}"'
    )

    # --------------------------------------------------------
    # QUERY 2
    # Topic + objective concepts.
    # --------------------------------------------------------

    if objective_concepts:

        objective_terms = " ".join(
            objective_concepts[:10]
        )

        queries.append(
            f'"{topic}" {objective_terms}'
        )

    # --------------------------------------------------------
    # QUERY 3
    # Topic + competitor context.
    # --------------------------------------------------------

    if competitors:

        competitor_terms = " ".join(
            meaningful_words(
                competitors
            )[:8]
        )

        if competitor_terms:

            queries.append(
                f'"{topic}" {competitor_terms}'
            )

    # --------------------------------------------------------
    # Fallback concept query.
    # --------------------------------------------------------

    if (
        len(queries) < 2
        and topic_concepts
    ):

        queries.append(
            " ".join(
                topic_concepts[:10]
            )
        )

    # --------------------------------------------------------
    # Remove duplicates.
    # --------------------------------------------------------

    final_queries = []

    for query in queries:

        query = clean_text(query)

        if (
            query
            and query not in final_queries
        ):

            final_queries.append(
                query
            )

    return final_queries[:3]


def build_research_query(
    topic,
    objective="",
    competitors=""
):
    """
    Return the strongest combined query.
    """

    queries = build_research_queries(
        topic,
        objective,
        competitors
    )

    if queries:
        return queries[0]

    return clean_text(topic)


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(
    topic,
    objective="",
    competitors=""
):
    """
    Determine the user's intelligence objective.

    This is deliberately domain-independent.
    """

    combined = clean_text(
        f"{topic} "
        f"{objective} "
        f"{competitors}"
    ).lower()

    intents = []

    # --------------------------------------------------------
    # Research intent
    # --------------------------------------------------------

    research_terms = [
        "research",
        "paper",
        "papers",
        "academic",
        "scholarly",
        "publication",
        "literature",
        "study",
        "studies",
        "scientific",
        "experiment",
        "methodology"
    ]

    if any(
        term in combined
        for term in research_terms
    ):

        intents.append(
            "research"
        )

    # --------------------------------------------------------
    # Trend / recent intelligence
    # --------------------------------------------------------

    trend_terms = [
        "trend",
        "trends",
        "emerging",
        "emerge",
        "latest",
        "recent",
        "current",
        "new",
        "news",
        "development",
        "developments",
        "update",
        "updates",
        "future"
    ]

    if any(
        term in combined
        for term in trend_terms
    ):

        intents.append(
            "trends"
        )

    # --------------------------------------------------------
    # Competitive intelligence
    # --------------------------------------------------------

    competitive_terms = [
        "competitor",
        "competitors",
        "competitive",
        "competition",
        "market",
        "industry",
        "company",
        "companies",
        "startup",
        "startups",
        "organization",
        "organizations",
        "strategy",
        "strategies"
    ]

    if (
        competitors.strip()
        or any(
            term in combined
            for term in competitive_terms
        )
    ):

        intents.append(
            "competitive"
        )

    # --------------------------------------------------------
    # Patent intent
    # --------------------------------------------------------

    patent_terms = [
        "patent",
        "patents",
        "intellectual property",
        "ip landscape",
        "prior art"
    ]

    if any(
        term in combined
        for term in patent_terms
    ):

        intents.append(
            "patent"
        )

    # --------------------------------------------------------
    # Default
    # --------------------------------------------------------

    if not intents:

        intents.append(
            "research"
        )

    return list(
        dict.fromkeys(
            intents
        )
    )


# ============================================================
# DYNAMIC TOOL SELECTION
# ============================================================

def select_tools(
    topic,
    objective="",
    competitors=""
):
    """
    Dynamically determine which external tools
    are relevant to the user's request.
    """

    topic = clean_text(topic)
    objective = clean_text(objective)
    competitors = clean_text(competitors)

    combined = (
        f"{topic} "
        f"{objective} "
        f"{competitors}"
    ).lower()

    intents = detect_intent(
        topic,
        objective,
        competitors
    )

    selected = []

    # --------------------------------------------------------
    # ALWAYS use core scholarly discovery.
    #
    # ResearchRadar's core problem is research/
    # technology intelligence.
    # --------------------------------------------------------

    selected.append(
        "OpenAlex API"
    )

    selected.append(
        "Crossref API"
    )

    # --------------------------------------------------------
    # arXiv
    #
    # Useful when the subject/objective contains
    # computational, scientific or technical research.
    # --------------------------------------------------------

    technical_terms = [
        "ai",
        "artificial intelligence",
        "machine learning",
        "deep learning",
        "llm",
        "large language model",
        "generative ai",
        "neural",
        "robot",
        "robotics",
        "computer vision",
        "natural language",
        "nlp",
        "quantum",
        "algorithm",
        "software",
        "computing",
        "cybersecurity",
        "cyber security",
        "data science",
        "data",
        "computer",
        "autonomous"
    ]

    technical_match = any(
        term in combined
        for term in technical_terms
    )

    if technical_match:

        selected.append(
            "arXiv API"
        )

        selected.append(
            "Semantic Scholar API"
        )

    # --------------------------------------------------------
    # News sources
    # --------------------------------------------------------

    news_needed = (
        "trends" in intents
        or "competitive" in intents
        or "patent" in intents
        or "news" in combined
        or "latest" in combined
        or "recent" in combined
        or "current" in combined
        or "emerging" in combined
        or bool(competitors.strip())
    )

    if news_needed:

        selected.append(
            "Google News RSS"
        )

        selected.append(
            "GDELT API"
        )

    # --------------------------------------------------------
    # If no technical match and the user explicitly
    # wants academic research, Semantic Scholar is useful.
    # --------------------------------------------------------

    if (
        "research" in intents
        and not technical_match
    ):

        selected.append(
            "Semantic Scholar API"
        )

    return list(
        dict.fromkeys(
            selected
        )
    )


# ============================================================
# RESULT NORMALIZATION
# ============================================================

def normalize_finding(
    title="",
    summary="",
    source="",
    date="Unknown",
    authors="",
    organization="",
    url="",
    importance="Medium",
    signal="",
    tool="",
    **extra
):
    """
    Force every external API result into the
    same ResearchRadar structure.
    """

    finding = {

        "title":
            clean_text(title),

        "summary":
            clean_text(summary),

        "source":
            clean_text(source),

        "date":
            clean_text(date)
            or "Unknown",

        "authors":
            clean_text(authors),

        "organization":
            clean_text(
                organization
            )
            or "Research Community",

        "url":
            clean_text(url),

        "importance":
            clean_text(
                importance
            )
            or "Medium",

        "signal":
            clean_text(signal),

        "tool":
            clean_text(tool)

    }

    # Preserve additional useful metadata.
    for key, value in extra.items():

        if value is not None:

            finding[key] = value

    return finding


# ============================================================
# RELEVANCE SCORING
# ============================================================

def relevance_score(
    finding,
    topic,
    objective=""
):
    """
    Score how strongly a finding matches
    the user's actual topic and objective.

    Higher score = more relevant.
    """

    title = clean_text(
        finding.get(
            "title",
            ""
        )
    ).lower()

    summary = clean_text(
        finding.get(
            "summary",
            ""
        )
    ).lower()

    organization = clean_text(
        finding.get(
            "organization",
            ""
        )
    ).lower()

    text = (
        f"{title} "
        f"{summary} "
        f"{organization}"
    )

    topic_words = meaningful_words(
        topic
    )

    objective_words = meaningful_words(
        objective
    )

    score = 0

    # --------------------------------------------------------
    # Topic matching
    # --------------------------------------------------------

    for word in topic_words:

        if word in title:

            score += 8

        elif word in text:

            score += 4

    # --------------------------------------------------------
    # Objective matching
    # --------------------------------------------------------

    for word in objective_words:

        if word in title:

            score += 4

        elif word in text:

            score += 2

    # --------------------------------------------------------
    # Exact topic phrase
    # --------------------------------------------------------

    normalized_topic = (
        clean_text(topic)
        .lower()
    )

    if (
        normalized_topic
        and normalized_topic in text
    ):

        score += 10

    # --------------------------------------------------------
    # Exact objective phrase fragments
    # --------------------------------------------------------

    objective_clean = (
        clean_text(objective)
        .lower()
    )

    if (
        len(objective_clean) >= 12
        and objective_clean in text
    ):

        score += 8

    return score


# ============================================================
# RANKING + DEDUPLICATION
# ============================================================

def normalize_title(title):
    """
    Normalize a title for duplicate detection.
    """

    title = clean_text(
        title
    ).lower()

    title = re.sub(
        r"[^a-z0-9]+",
        " ",
        title
    )

    return re.sub(
        r"\s+",
        " ",
        title
    ).strip()


def duplicate_key(finding):
    """
    Prefer DOI/URL, otherwise normalized title.
    """

    doi = clean_text(
        finding.get(
            "doi",
            ""
        )
    ).lower()

    if doi:
        return (
            "doi:",
            doi
        )

    url = clean_text(
        finding.get(
            "url",
            ""
        )
    ).lower()

    if url:
        return (
            "url:",
            url
        )

    title = normalize_title(
        finding.get(
            "title",
            ""
        )
    )

    return (
        "title:",
        title
    )


def rank_findings(
    findings,
    topic,
    objective="",
    limit=20
):
    """
    Clean, score, deduplicate and rank findings.
    """

    unique = {}

    for raw_finding in findings:

        title = clean_text(
            raw_finding.get(
                "title",
                ""
            )
        )

        if not title:
            continue

        finding = normalize_finding(
            **raw_finding
        )

        score = relevance_score(
            finding,
            topic,
            objective
        )

        finding[
            "relevance_score"
        ] = score

        key = duplicate_key(
            finding
        )

        # Keep the stronger version of duplicates.
        if key not in unique:

            unique[key] = finding

        else:

            old_score = unique[key].get(
                "relevance_score",
                0
            )

            if score > old_score:

                unique[key] = finding

    ranked = list(
        unique.values()
    )

    ranked.sort(
        key=lambda item: (
            item.get(
                "relevance_score",
                0
            ),
            item.get(
                "importance",
                ""
            ).lower() == "high"
        ),
        reverse=True
    )

    return ranked[:limit]


# ============================================================
# 1. ARXIV TOOL
# ============================================================

def search_arxiv(
    topic,
    objective="",
    max_results=5
):
    """
    Search arXiv using the actual topic + objective.
    """

    results = []

    queries = build_research_queries(
        topic,
        objective
    )

    try:

        for query in queries:

            search_query = (
                f'all:"{query}"'
            )

            params = {

                "search_query":
                    search_query,

                "start":
                    0,

                "max_results":
                    max_results,

                "sortBy":
                    "relevance",

                "sortOrder":
                    "descending"

            }

            response = safe_get(
                ARXIV_URL,
                params
            )

            if not response:
                continue

            root = ET.fromstring(
                response.text
            )

            namespace = {
                "atom":
                "http://www.w3.org/2005/Atom"
            }

            entries = root.findall(
                "atom:entry",
                namespace
            )

            for entry in entries:

                title = entry.findtext(
                    "atom:title",
                    "",
                    namespace
                )

                summary = entry.findtext(
                    "atom:summary",
                    "",
                    namespace
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

                        authors.append(
                            clean_text(name)
                        )

                source_url = ""

                for link in entry.findall(
                    "atom:link",
                    namespace
                ):

                    href = link.attrib.get(
                        "href",
                        ""
                    )

                    if href:

                        source_url = href

                        if (
                            link.attrib.get(
                                "type",
                                ""
                            )
                            == "text/html"
                        ):
                            break

                results.append(
                    normalize_finding(

                        title=title,

                        summary=summary,

                        source="arXiv",

                        date=(
                            published[:10]
                            if published
                            else "Unknown"
                        ),

                        authors=", ".join(
                            authors
                        ),

                        organization=(
                            ", ".join(
                                authors[:2]
                            )
                            if authors
                            else "Research Community"
                        ),

                        url=source_url,

                        importance="High",

                        signal=(
                            "Academic research "
                            "activity detected."
                        ),

                        tool="arXiv API"

                    )
                )

    except Exception as error:

        print(
            "arXiv error:",
            error
        )

    return rank_findings(
        results,
        topic,
        objective,
        max_results
    )


# ============================================================
# OPENALEX ABSTRACT RECONSTRUCTION
# ============================================================

def reconstruct_abstract(
    inverted_index
):
    """
    Reconstruct OpenAlex abstracts from their
    inverted index representation.
    """

    if not inverted_index:
        return ""

    positions = []

    for word, indexes in (
        inverted_index.items()
    ):

        for index in indexes:

            positions.append(
                (
                    index,
                    word
                )
            )

    positions.sort(
        key=lambda item: item[0]
    )

    return " ".join(
        word
        for _, word in positions
    )


# ============================================================
# 2. OPENALEX TOOL
# ============================================================

def search_openalex(
    topic,
    objective="",
    max_results=5
):
    """
    Search OpenAlex for scholarly works.
    """

    results = []

    queries = build_research_queries(
        topic,
        objective
    )

    try:

        for query in queries:

            params = {

                "search":
                    query,

                "per-page":
                    max_results,

                "sort":
                    "relevance_score:desc"

            }

            response = safe_get(
                OPENALEX_URL,
                params
            )

            if not response:
                continue

            data = response.json()

            for item in data.get(
                "results",
                []
            ):

                authors = []

                for authorship in (
                    item.get(
                        "authorships",
                        []
                    )[:3]
                ):

                    author = authorship.get(
                        "author",
                        {}
                    )

                    name = author.get(
                        "display_name",
                        ""
                    )

                    if name:

                        authors.append(
                            clean_text(name)
                        )

                abstract = reconstruct_abstract(
                    item.get(
                        "abstract_inverted_index"
                    )
                )

                primary_location = (
                    item.get(
                        "primary_location",
                        {}
                    )
                    or {}
                )

                source = (
                    primary_location.get(
                        "source",
                        {}
                    )
                    or {}
                )

                organization = source.get(
                    "display_name",
                    ""
                )

                results.append(
                    normalize_finding(

                        title=item.get(
                            "title",
                            "Untitled research"
                        ),

                        summary=(
                            abstract
                            or
                            "Scholarly work "
                            "identified through "
                            "OpenAlex."
                        ),

                        source="OpenAlex",

                        date=item.get(
                            "publication_date",
                            "Unknown"
                        ),

                        authors=", ".join(
                            authors
                        ),

                        organization=(
                            organization
                            or
                            (
                                ", ".join(
                                    authors[:2]
                                )
                                if authors
                                else
                                "Research Community"
                            )
                        ),

                        url=(
                            primary_location.get(
                                "landing_page_url",
                                ""
                            )
                            or
                            item.get(
                                "doi",
                                ""
                            )
                        ),

                        importance="High",

                        signal=(
                            "Scholarly activity "
                            "related to the "
                            "research objective."
                        ),

                        tool="OpenAlex API",

                        citations=item.get(
                            "cited_by_count",
                            0
                        )

                    )
                )

    except Exception as error:

        print(
            "OpenAlex error:",
            error
        )

    return rank_findings(
        results,
        topic,
        objective,
        max_results
    )


# ============================================================
# 3. CROSSREF TOOL
# ============================================================

def search_crossref(
    topic,
    objective="",
    max_results=5
):
    """
    Search Crossref scholarly metadata.
    """

    results = []

    try:

        query = build_research_query(
            topic,
            objective
        )

        params = {

            "query.bibliographic":
                query,

            "rows":
                max_results,

            "select": (
                "DOI,title,author,"
                "published,published-print,"
                "published-online,URL,"
                "type,container-title"
            )

        }

        response = safe_get(
            CROSSREF_URL,
            params
        )

        if not response:
            return []

        data = response.json()

        items = (
            data.get(
                "message",
                {}
            ).get(
                "items",
                []
            )
        )

        for item in items:

            titles = item.get(
                "title",
                []
            )

            title = (
                titles[0]
                if titles
                else
                "Untitled publication"
            )

            authors = []

            for author in item.get(
                "author",
                []
            )[:3]:

                given = clean_text(
                    author.get(
                        "given",
                        ""
                    )
                )

                family = clean_text(
                    author.get(
                        "family",
                        ""
                    )
                )

                name = (
                    f"{given} {family}"
                ).strip()

                if name:

                    authors.append(
                        name
                    )

            publication_date = (
                item.get(
                    "published-online"
                )
                or
                item.get(
                    "published-print"
                )
                or
                item.get(
                    "published"
                )
            )

            date = "Unknown"

            if publication_date:

                date_parts = (
                    publication_date.get(
                        "date-parts",
                        []
                    )
                )

                if (
                    date_parts
                    and date_parts[0]
                ):

                    date = "-".join(
                        str(value)
                        for value
                        in date_parts[0]
                    )

            doi = clean_text(
                item.get(
                    "DOI",
                    ""
                )
            )

            url = clean_text(
                item.get(
                    "URL",
                    ""
                )
            )

            if (
                not url
                and doi
            ):

                url = (
                    "https://doi.org/"
                    + doi
                )

            journal = ""

            container_titles = (
                item.get(
                    "container-title",
                    []
                )
            )

            if container_titles:

                journal = clean_text(
                    container_titles[0]
                )

            summary = (
                "Scholarly publication "
                "metadata identified "
                "through Crossref."
            )

            if journal:

                summary += (
                    f" Published in "
                    f"{journal}."
                )

            results.append(
                normalize_finding(

                    title=title,

                    summary=summary,

                    source="Crossref",

                    date=date,

                    authors=", ".join(
                        authors
                    ),

                    organization=(
                        journal
                        or
                        "Research Community"
                    ),

                    url=url,

                    importance="Medium",

                    signal=(
                        "Scholarly publication "
                        "identified."
                    ),

                    tool="Crossref API",

                    doi=doi

                )
            )

    except Exception as error:

        print(
            "Crossref error:",
            error
        )

    return rank_findings(
        results,
        topic,
        objective,
        max_results
    )


# ============================================================
# 4. SEMANTIC SCHOLAR
# ============================================================

def search_semantic_scholar(
    topic,
    objective="",
    max_results=5
):
    """
    Search Semantic Scholar for relevant papers.
    """

    results = []

    try:

        query = build_research_query(
            topic,
            objective
        )

        params = {

            "query":
                query,

            "limit":
                max_results,

            "fields": (
                "title,abstract,"
                "authors,year,url,"
                "publicationDate,"
                "citationCount"
            )

        }

        response = safe_get(
            SEMANTIC_SCHOLAR_URL,
            params
        )

        if not response:
            return []

        data = response.json()

        for item in data.get(
            "data",
            []
        ):

            authors = []

            for author in item.get(
                "authors",
                []
            )[:3]:

                name = clean_text(
                    author.get(
                        "name",
                        ""
                    )
                )

                if name:

                    authors.append(
                        name
                    )

            results.append(
                normalize_finding(

                    title=item.get(
                        "title",
                        "Untitled paper"
                    ),

                    summary=(
                        item.get(
                            "abstract",
                            ""
                        )
                        or
                        "Paper indexed by "
                        "Semantic Scholar."
                    ),

                    source="Semantic Scholar",

                    date=(
                        item.get(
                            "publicationDate"
                        )
                        or
                        str(
                            item.get(
                                "year",
                                "Unknown"
                            )
                        )
                    ),

                    authors=", ".join(
                        authors
                    ),

                    organization=(
                        ", ".join(
                            authors[:2]
                        )
                        if authors
                        else
                        "Research Community"
                    ),

                    url=item.get(
                        "url",
                        ""
                    ),

                    importance="High",

                    signal=(
                        "Relevant scholarly "
                        "research identified."
                    ),

                    tool="Semantic Scholar API",

                    citations=item.get(
                        "citationCount",
                        0
                    )

                )
            )

    except Exception as error:

        print(
            "Semantic Scholar error:",
            error
        )

    return rank_findings(
        results,
        topic,
        objective,
        max_results
    )


# ============================================================
# 5. GOOGLE NEWS RSS
# ============================================================

def search_google_news(
    topic,
    objective="",
    competitors="",
    max_results=6
):
    """
    Search Google News through its public RSS feed.

    The RSS HTML is explicitly cleaned so raw <a href>
    markup never reaches the Streamlit UI.
    """

    results = []

    try:

        # Use the actual topic as the primary news query.
        # Add important objective concepts without making
        # the query excessively long.

        topic_clean = clean_text(
            topic
        )

        objective_words = meaningful_words(
            objective
        )

        query_parts = [
            topic_clean
        ]

        if objective_words:

            query_parts.extend(
                objective_words[:6]
            )

        if competitors.strip():

            competitor_words = meaningful_words(
                competitors
            )

            query_parts.extend(
                competitor_words[:5]
            )

        query = " ".join(
            part
            for part in query_parts
            if part
        )

        params = {

            "q":
                query,

            "hl":
                "en-IN",

            "gl":
                "IN",

            "ceid":
                "IN:en"

        }

        response = safe_get(
            GOOGLE_NEWS_RSS_URL,
            params
        )

        if not response:
            return []

        root = ET.fromstring(
            response.text
        )

        items = root.findall(
            ".//item"
        )

        for item in items[
            :max_results
        ]:

            raw_title = item.findtext(
                "title",
                ""
            )

            raw_description = (
                item.findtext(
                    "description",
                    ""
                )
            )

            raw_link = item.findtext(
                "link",
                ""
            )

            raw_date = item.findtext(
                "pubDate",
                ""
            )

            # Clean everything BEFORE putting it
            # into the finding.
            title = clean_text(
                raw_title
            )

            description = clean_text(
                raw_description
            )

            link = clean_text(
                raw_link
            )

            # Google News sometimes places the
            # publisher after a separator in title.
            organization = "News"

            if " - " in title:

                title_parts = title.rsplit(
                    " - ",
                    1
                )

                if len(title_parts) == 2:

                    possible_source = (
                        clean_text(
                            title_parts[1]
                        )
                    )

                    if (
                        possible_source
                        and len(
                            possible_source
                        ) < 100
                    ):

                        organization = (
                            possible_source
                        )

            date = "Unknown"

            if raw_date:

                try:

                    date = (
                        parsedate_to_datetime(
                            raw_date
                        ).strftime(
                            "%Y-%m-%d"
                        )
                    )

                except Exception:

                    date = clean_text(
                        raw_date
                    )

            results.append(
                normalize_finding(

                    title=title,

                    summary=(
                        description
                        or
                        "Recent news coverage "
                        "related to the selected "
                        "intelligence topic."
                    ),

                    source="Google News RSS",

                    date=date,

                    authors="",

                    organization=organization,

                    url=link,

                    importance="Medium",

                    signal=(
                        "Recent information "
                        "activity detected."
                    ),

                    tool="Google News RSS"

                )
            )

    except Exception as error:

        print(
            "Google News RSS error:",
            error
        )

    return rank_findings(
        results,
        topic,
        objective,
        max_results
    )


# ============================================================
# 6. GDELT
# ============================================================

def search_gdelt(
    topic,
    objective="",
    max_results=6
):
    """
    Search GDELT for recent global news coverage.
    """

    results = []

    try:

        query = build_research_query(
            topic,
            objective
        )

        params = {

            "query":
                query,

            "mode":
                "artlist",

            "maxrecords":
                max_results,

            "format":
                "json",

            "sort":
                "datedesc"

        }

        response = safe_get(
            GDELT_URL,
            params
        )

        if not response:
            return []

        data = response.json()

        articles = data.get(
            "articles",
            []
        )

        for article in articles[
            :max_results
        ]:

            domain = clean_text(
                article.get(
                    "domain",
                    ""
                )
            )

            results.append(
                normalize_finding(

                    title=article.get(
                        "title",
                        "Untitled news"
                    ),

                    summary=(
                        f"Recent coverage from "
                        f"{domain or 'news source'}."
                    ),

                    source="GDELT",

                    date=clean_text(
                        article.get(
                            "seendate",
                            "Unknown"
                        )
                    ),

                    authors="",

                    organization=(
                        domain
                        or
                        "News"
                    ),

                    url=article.get(
                        "url",
                        ""
                    ),

                    importance="Medium",

                    signal=(
                        "Recent news activity "
                        "detected."
                    ),

                    tool="GDELT API"

                )
            )

    except Exception as error:

        print(
            "GDELT error:",
            error
        )

    return rank_findings(
        results,
        topic,
        objective,
        max_results
    )


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOL_FUNCTIONS = {

    "arXiv API":
        search_arxiv,

    "OpenAlex API":
        search_openalex,

    "Crossref API":
        search_crossref,

    "Semantic Scholar API":
        search_semantic_scholar,

    "Google News RSS":
        search_google_news,

    "GDELT API":
        search_gdelt

}


# ============================================================
# AUTONOMOUS INTELLIGENCE TOOL RUNNER
# ============================================================

def run_intelligence_tools(
    topic,
    objective="",
    competitors=""
):
    """
    Main intelligence orchestration function.

    Flow:

        User Input
             ↓
        Intent Detection
             ↓
        Dynamic Tool Selection
             ↓
        Topic + Objective Queries
             ↓
        External APIs
             ↓
        Normalize
             ↓
        Relevance Scoring
             ↓
        Deduplication
             ↓
        Ranked Findings
    """

    topic = clean_text(
        topic
    )

    objective = clean_text(
        objective
    )

    competitors = clean_text(
        competitors
    )

    # --------------------------------------------------------
    # Dynamic tool selection
    # --------------------------------------------------------

    selected_tools = select_tools(
        topic,
        objective,
        competitors
    )

    # --------------------------------------------------------
    # Research queries
    # --------------------------------------------------------

    research_queries = (
        build_research_queries(
            topic,
            objective,
            competitors
        )
    )

    primary_query = (
        research_queries[0]
        if research_queries
        else topic
    )

    print()
    print(
        "=========================================="
    )
    print(
        "ResearchRadar Intelligence Agent"
    )
    print(
        "=========================================="
    )
    print(
        "Topic:",
        topic
    )
    print(
        "Objective:",
        objective
    )
    print(
        "Competitors:",
        competitors
    )
    print(
        "Selected tools:",
        selected_tools
    )
    print(
        "Queries:",
        research_queries
    )
    print(
        "=========================================="
    )

    findings = []

    tool_status = []

    # --------------------------------------------------------
    # Execute selected tools
    # --------------------------------------------------------

    for tool_name in selected_tools:

        tool_function = TOOL_FUNCTIONS.get(
            tool_name
        )

        if not tool_function:

            tool_status.append({

                "tool":
                    tool_name,

                "status":
                    "Unavailable"

            })

            continue

        try:

            # Google News requires competitors
            # as an additional argument.

            if tool_name == (
                "Google News RSS"
            ):

                results = tool_function(
                    topic,
                    objective,
                    competitors
                )

            else:

                results = tool_function(
                    topic,
                    objective
                )

            if results:

                findings.extend(
                    results
                )

                tool_status.append({

                    "tool":
                        tool_name,

                    "status":
                        "Success",

                    "count":
                        len(results)

                })

            else:

                tool_status.append({

                    "tool":
                        tool_name,

                    "status":
                        "No results",

                    "count":
                        0

                })

        except Exception as error:

            print(
                f"{tool_name} execution error:",
                error
            )

            tool_status.append({

                "tool":
                    tool_name,

                "status":
                    "Error",

                "count":
                    0

            })

    # --------------------------------------------------------
    # Final ranking and deduplication
    # --------------------------------------------------------

    final_findings = rank_findings(
        findings,
        topic,
        objective,
        limit=20
    )

    # --------------------------------------------------------
    # Assign dynamic signal / importance
    # --------------------------------------------------------

    for finding in final_findings:

        score = finding.get(
            "relevance_score",
            0
        )

        if score >= 15:

            finding["importance"] = "High"

            finding["signal"] = (
                "Strong match to the user's "
                "research objective."
            )

        elif score >= 8:

            finding["importance"] = "Medium"

            finding["signal"] = (
                "Meaningful relevance to the "
                "research objective."
            )

        else:

            finding["importance"] = "Low"

            finding["signal"] = (
                "Potentially useful contextual "
                "information."
            )

    # --------------------------------------------------------
    # Source summary
    # --------------------------------------------------------

    source_counts = {}

    for finding in final_findings:

        source = finding.get(
            "source",
            "Unknown"
        )

        source_counts[source] = (
            source_counts.get(
                source,
                0
            ) + 1
        )

    print(
        "Final findings:",
        len(final_findings)
    )

    print(
        "Source counts:",
        source_counts
    )

    print(
        "=========================================="
    )

    return {

        "selected_tools":
            selected_tools,

        "research_query":
            primary_query,

        "research_queries":
            research_queries,

        "findings":
            final_findings,

        "tool_status":
            tool_status,

        "source_counts":
            source_counts,

        "intent":
            detect_intent(
                topic,
                objective,
                competitors
            )

    }


# ============================================================
# SIMPLE DIRECT TEST
# ============================================================

if __name__ == "__main__":

    test_topic = (
        "AI Smart Study"
    )

    test_objective = (
        "Develop a personalized AI "
        "study assistant that recommends "
        "study plans based on student "
        "performance, learning needs, "
        "and study behavior."
    )

    test_result = run_intelligence_tools(
        test_topic,
        test_objective,
        ""
    )

    print()
    print(
        "Selected tools:"
    )

    for tool in test_result[
        "selected_tools"
    ]:

        print(
            "-",
            tool
        )

    print()
    print(
        "Top findings:"
    )

    for finding in test_result[
        "findings"
    ][:5]:

        print(
            "-",
            finding.get(
                "title",
                ""
            )
        )

        print(
            "  Source:",
            finding.get(
                "source",
                ""
            )
        )

        print(
            "  Relevance:",
            finding.get(
                "relevance_score",
                0
            )
        )