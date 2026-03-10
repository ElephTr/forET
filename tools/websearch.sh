#!/bin/bash
# Web Search Tool Wrapper
# Usage: websearch.sh <query> [max_results]

QUERY="$1"
MAX_RESULTS="${2:-5}"

if [ -z "$QUERY" ]; then
    echo "Usage: websearch.sh <query> [max_results]" >&2
    echo "" >&2
    echo "To use this tool, you need to set up one of the following API keys:" >&2
    echo "  - BRAVE_API_KEY: Get from https://brave.com/search/api/" >&2
    echo "  - BING_API_KEY: Get from https://www.microsoft.com/en-us/bing/apis/bing-web-search-api" >&2
    echo "  - SERPER_API_KEY: Get from https://serper.dev/" >&2
    exit 1
fi

# Try Serper.dev (Google Search API) - most reliable
if [ -n "$SERPER_API_KEY" ]; then
    curl -s -X POST "https://google.serper.dev/search" \
        -H "X-API-KEY: $SERPER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{\"q\":\"$QUERY\",\"num\":$MAX_RESULTS}" 2>/dev/null | python3 -m json.tool 2>/dev/null
    exit 0
fi

# Try Brave Search API
if [ -n "$BRAVE_API_KEY" ]; then
    curl -s "https://api.search.brave.com/res/v1/web/search?q=$(echo "$QUERY" | sed 's/ /+/g')&count=$MAX_RESULTS" \
        -H "X-Subscription-Token: $BRAVE_API_KEY" \
        -H "Accept: application/json" 2>/dev/null | python3 -m json.tool 2>/dev/null
    exit 0
fi

# Try Bing Search API
if [ -n "$BING_API_KEY" ]; then
    curl -s "https://api.bing.microsoft.com/v7.0/search?q=$(echo "$QUERY" | sed 's/ /+/g')&count=$MAX_RESULTS" \
        -H "Ocp-Apim-Subscription-Key: $BING_API_KEY" 2>/dev/null | python3 -m json.tool 2>/dev/null
    exit 0
fi

# Fallback: Try to use a public SearX instance with timeout
echo "No API key found. Trying public search instances..." >&2

SEARX_INSTANCES=(
    "https://search.sapti.me"
    "https://search.bus-hit.me"
)

for INSTANCE in "${SEARX_INSTANCES[@]}"; do
    RESULT=$(curl -s --max-time 5 "${INSTANCE}/search?q=$(echo "$QUERY" | sed 's/ /+/g')&format=json&language=zh-CN" 2>/dev/null)
    if [ -n "$RESULT" ] && echo "$RESULT" | python3 -c "import sys,json; json.load(sys.stdin)" 2>/dev/null; then
        echo "$RESULT" | python3 -m json.tool 2>/dev/null
        exit 0
    fi
done

echo "Error: Unable to perform search. Please set up an API key." >&2
echo "" >&2
echo "Quick setup:" >&2
echo "  export SERPER_API_KEY='your_key_here'  # Recommended" >&2
echo "  export BRAVE_API_KEY='your_key_here'" >&2
echo "  export BING_API_KEY='your_key_here'" >&2
exit 1
