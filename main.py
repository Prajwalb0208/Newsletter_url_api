from claude_client import run_search, run_fetch, run_rank, fetch_with_fallback

def workflow(topic):
    print(f"Searching for resources on: {topic}")
    search_output = run_search(topic)
    urls = []
    for line in search_output.splitlines():
        if line.strip().startswith(tuple(f"{i}." for i in range(1, 11))):
            url = line.split(".", 1)[-1].strip()
            urls.append(url)

    summaries = []
    for url in urls:
        print(f"Fetching and summarizing {url}")
        try:
            summary = fetch_with_fallback(url)
            summaries.append(f"{url}:\n{summary}")
        except Exception as e:
            summaries.append(f"{url}: ERROR ({e})")

    print("\nRanking resources...")
    ranked_list = run_rank("\n".join(summaries))
    print("\nBest beginner resources (articles/images/videos):\n")
    print(ranked_list)


if __name__ == "__main__":
    topic = input("Enter topic: ")
    workflow(topic)
