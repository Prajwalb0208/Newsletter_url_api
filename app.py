import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from claude_client import run_search, fetch_with_fallback, run_rank
from upstash_redis import Redis

app = FastAPI()

redis_client = Redis(
    url=os.environ["UPSTASH_REDIS_REST_URL"],
    token=os.environ["UPSTASH_REDIS_REST_TOKEN"]
)


def store_url_summary(url: str, summary: str):
    redis_client.set(url, summary)

class QueryRequest(BaseModel):
    topic: str


@app.get("/")
async def health():
    return {"status": "ok"}


@app.get("/stored_resources/")
async def get_stored_resources():
    keys = redis_client.keys("*")
    resources = []
    for key in keys:
        summary = redis_client.get(key)
        resources.append({"url": key, "summary": summary})
    return {"resources": resources}


@app.post("/search_resources/")
async def search_resources(request: QueryRequest):
    topic = request.topic
    try:
        search_output = run_search(topic)
        urls = []
        summaries = []
        for line in search_output.splitlines():
            if line.strip().startswith(tuple(f"{i}." for i in range(1, 11))):
                url = line.split(".", 1)[-1].strip()
                summary = fetch_with_fallback(url)
                if "blocked" in summary.lower() or "error" in summary.lower():
                    continue
                urls.append(url)
                summaries.append(summary)
                store_url_summary(url, summary)
        ranked_list = run_rank("\n".join([f"{url}:\n{summary}" for url, summary in zip(urls, summaries)]))
        result_urls = []
        for line in ranked_list.splitlines():
            if line.strip().startswith(tuple(f"{i}." for i in range(1, 6))):
                result_urls.append(line.split(".", 1)[-1].strip())
        return {"ranked_urls": result_urls}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
