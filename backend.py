# ─────────────────────────────────────────────
# Sentiment Broadcast — Backend
# ─────────────────────────────────────────────
# Install deps:
#   pip install fastapi uvicorn feedparser vaderSentiment
#
# Run (from inside the sentiment_broadcast folder):
#   uvicorn backend:app --reload
# ─────────────────────────────────────────────

import asyncio
import json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

analyzer = SentimentIntensityAnalyzer()

# Public RSS feeds — no API key required
RSS_FEEDS = [
    "http://feeds.bbci.co.uk/news/world/rss.xml",
    "https://feeds.reuters.com/reuters/worldNews",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

POLL_INTERVAL_SECONDS = 15
MAX_HEADLINES_PER_FEED = 15

connected_clients: list[WebSocket] = []


def fetch_sentiment() -> dict:
    """
    Fetches latest headlines from all RSS feeds,
    scores each with VADER, and returns the average
    compound sentiment score along with sampled headlines.
    """
    scores = []
    headlines = []

    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:MAX_HEADLINES_PER_FEED]:
                title = entry.get("title", "")
                if title:
                    compound = analyzer.polarity_scores(title)["compound"]
                    scores.append(compound)
                    moral = round((compound + 1) / 2 * 10, 2)  # -1…+1 → 0…10
                    headlines.append({"title": title, "score": round(compound, 4), "moral": moral})
        except Exception as e:
            print(f"Feed error ({url}): {e}")

    avg_score = round(sum(scores) / len(scores), 4) if scores else 0.0

    return {
        "sentiment": avg_score,
        "headline_count": len(headlines),
        "sample_headlines": headlines[:15],
    }


async def broadcast_loop():
    """
    Runs continuously in the background.
    Every POLL_INTERVAL_SECONDS, fetches fresh sentiment
    and pushes it to all connected WebSocket clients.
    """
    while True:
        data = fetch_sentiment()
        payload = json.dumps(data)

        print(f"[broadcast] sentiment={data['sentiment']} | clients={len(connected_clients)}")

        for ws in connected_clients.copy():
            try:
                await ws.send_text(payload)
            except Exception:
                connected_clients.remove(ws)

        await asyncio.sleep(POLL_INTERVAL_SECONDS)


@app.on_event("startup")
async def startup():
    asyncio.create_task(broadcast_loop())


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    connected_clients.append(ws)
    print(f"[ws] client connected — total: {len(connected_clients)}")

    try:
        data = fetch_sentiment()
        await ws.send_text(json.dumps(data))
    except Exception:
        pass

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        if ws in connected_clients:
            connected_clients.remove(ws)
        print(f"[ws] client disconnected — total: {len(connected_clients)}")
