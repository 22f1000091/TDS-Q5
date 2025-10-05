from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import json
import numpy as np
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

data_path = os.path.join(os.path.dirname(__file__), "../telemetry/sample.json")
with open(data_path, "r") as f:
    telemetry = json.load(f)

@app.post("/")
async def metrics(request: Request):
    payload = await request.json()
    regions = payload.get("regions", [])
    threshold = payload.get("threshold_ms", 180)

    result = {}
    for region in regions:
        entries = [r for r in telemetry if r["region"] == region]
        if not entries:
            continue
        latencies = [e["latency_ms"] for e in entries]
        uptimes = [e["uptime"] for e in entries]
        breaches = sum(l > threshold for l in latencies)
        result[region] = {
            "avg_latency": float(np.mean(latencies)),
            "p95_latency": float(np.percentile(latencies, 95)),
            "avg_uptime": float(np.mean(uptimes)),
            "breaches": breaches,
        }
    return result
