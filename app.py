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

def store_urls(urls):
    if urls:
        redis_client.sadd("extracted_urls", *urls)

class QueryRequest(BaseModel):
    topic: str

@app.get("/")
async def health():
    return {"status": "ok"}

@app.get("/stored_urls/")
async def get_stored_urls():
    stored_urls = redis_client.smembers("extracted_urls")
    return {"urls": stored_urls} 

@app.post("/search_resources/")
async def search_resources(request: QueryRequest):
    topic = request.topic
    try:
        search_output = run_search(topic)
        urls = []
        for line in search_output.splitlines():
            if line.strip().startswith(tuple(f"{i}." for i in range(1, 11))):
                url = line.split(".", 1)[-1].strip()
                urls.append(url)
        store_urls(urls)
        summaries = []
        for url in urls:
            summary = fetch_with_fallback(url)
            summaries.append(f"{url}:\n{summary}")
        ranked_list = run_rank("\n".join(summaries))
        result_urls = []
        for line in ranked_list.splitlines():
            if line.strip().startswith(tuple(f"{i}." for i in range(1, 6))):
                result_urls.append(line.split(".", 1)[-1].strip())
        return {"ranked_urls": result_urls}
    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
