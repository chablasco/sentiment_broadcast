# Sentiment Broadcast

A real-time news sentiment visualiser. Live headlines stream across the screen in rows, coloured from red to green based on their moral score — red for bleak news, amber for neutral, green for hopeful. When the backend is running, data is pulled live from RSS feeds every 15 seconds. Without the backend, the display falls back to a set of demo headlines.

---

## Project structure

```
sentiment_broadcast/
├── index.html      — Frontend ticker display
├── backend.py      — FastAPI + WebSocket backend
└── README.md
```

---

## Requirements

- Python 3.8 or later
- pip packages:

```
fastapi
uvicorn
feedparser
vaderSentiment
```

---

## Getting started

### 1. Clone the repo

```bash
git clone https://github.com/DITT_ANVÄNDARNAMN/sentiment_broadcast.git
cd sentiment_broadcast
```

### 2. Install dependencies

```bash
pip install fastapi uvicorn feedparser vaderSentiment
```

### 3. Start the backend

You must run this command from inside the `sentiment_broadcast` folder, otherwise uvicorn cannot find `backend.py`:

```bash
cd sentiment_broadcast
uvicorn backend:app --reload
```

The backend will be available at `http://localhost:8000`.

### 4. Open the frontend

Open `index.html` in your browser. It connects automatically to `ws://localhost:8000/ws`.

> If the backend is not running, the page still works and shows demo headlines instead of live data.

---

## Common error

**`ERROR: Could not import module "backend"`**

This means uvicorn was run from the wrong directory. Fix it by navigating into the project folder first:

```bash
cd ~/Desktop/sentiment_broadcast
uvicorn backend:app --reload
```

---

## Hosting the frontend on GitHub Pages

The `index.html` file is a standalone static page and can be hosted for free:

1. Go to your repo on GitHub
2. Settings → Pages
3. Source: `main` branch, `/ (root)` → Save

You will get a public URL that shows the ticker with demo headlines. The backend must be run locally or on a server separately.

---

## Colour scale

| Score | Colour | Meaning       |
|-------|--------|---------------|
| 0     | Red    | Very negative |
| 5     | Amber  | Neutral       |
| 10    | Green  | Very positive |

---

## Notes

- Headlines are fetched every 15 seconds
- Up to 15 headlines are sent per WebSocket update
- VADER is designed for short social text and works reasonably well on news headlines, but is not perfect
- The display updates smoothly without refreshing the page
