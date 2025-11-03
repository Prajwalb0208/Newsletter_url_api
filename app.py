import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from claude_client import run_search, fetch_with_fallback, run_rank
from upstash_redis import Redis
from urllib.parse import urlparse
import json
from datetime import datetime

app = FastAPI()

redis_client = Redis(
    url=os.environ["UPSTASH_REDIS_REST_URL"],
    token=os.environ["UPSTASH_REDIS_REST_TOKEN"]
)

def store_resource(url: str, summary: str):
    parsed_url = urlparse(url)
    data = {
        "url": url,
        "name": parsed_url.hostname or "",
        "summary": summary,
        "date_stored": datetime.utcnow().isoformat() + "Z"
    }
    # Store as JSON string, key can be URL or hash of URL if long
    redis_client.set(url, json.dumps(data))

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
        val_json = redis_client.get(key)
        if val_json:
            resource = json.loads(val_json)
            resources.append(resource)
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
                store_resource(url, summary)
        ranked_list = run_rank("\n".join([f"{url}:\n{summary}" for url, summary in zip(urls, summaries)]))
        result_urls = []
        for line in ranked_list.splitlines():
            if line.strip().startswith(tuple(f"{i}." for i in range(1, 6))):
                result_urls.append(line.split(".", 1)[-1].strip())
        return {"ranked_urls": result_urls}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
