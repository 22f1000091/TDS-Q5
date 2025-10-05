from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

# Allow POST requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

# Load telemetry once at startup
with open(os.path.join(os.path.dirname(__file__), "../telemetry/q-vercel-latency.json")) as f:
    telemetry = json.load(f)

@app.post("/")
async def metrics(request: Request):
    data = await request.json()
    regions = data.get("regions", [])
    threshold = data.get("threshold_ms", 180)

    results = {}
    for region in regions:
        entries = [r for r in telemetry if r["region"] == region]
        if not entries:
            continue

        latencies = [e["latency_ms"] for e in entries]
        uptimes = [e["uptime"] for e in entries]
        breaches = sum(1 for l in latencies if l > threshold)

        results[region] = {
            "avg_latency": np.mean(latencies),
            "p95_latency": np.percentile(latencies, 95),
            "avg_uptime": np.mean(uptimes),
            "breaches": breaches
        }
    return results
