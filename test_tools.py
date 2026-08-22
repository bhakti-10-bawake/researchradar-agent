from intelligence_tools import run_intelligence_tools

topic = "quantum computing"
competitors = "IBM, Google, Microsoft"

result = run_intelligence_tools(topic, competitors)

print("\nSELECTED TOOLS:")
print(result["selected_tools"])

print("\nTOOL STATUS:")

for tool in result["tool_status"]:
    print(
        tool["tool"],
        "->",
        tool["reason"]
    )

print("\nFINDINGS:")

for finding in result["findings"]:
    print(
        "\n",
        finding["tool"],
        "|",
        finding["title"]
    )

print(
    "\nTOTAL FINDINGS:",
    len(result["findings"])
)