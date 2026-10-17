
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import defaultdict
import os
import secrets

app = FastAPI()

API_KEY = os.environ["ANALYTICS_API_KEY"]
EMAIL = "25ds3000021@ds.study.iitm.ac.in"

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Event(BaseModel):
    user: str
    amount: float
    ts: int

class AnalyticsRequest(BaseModel):
    events: list[Event]

@app.post("/analytics")
def analytics(
    data: AnalyticsRequest,
    x_api_key: str | None = Header(default=None)
):
    if x_api_key is None or not secrets.compare_digest(
        x_api_key, API_KEY
    ):
        raise HTTPException(
            status_code=401,
            detail="Unauthorized"
        )

    events = data.events

    total_events = len(events)

    unique_users = len(set(event.user for event in events))

    user_totals = defaultdict(float)

    for event in events:
        if event.amount > 0:
            user_totals[event.user] += event.amount

    revenue = sum(user_totals.values())

    top_user = (
        max(user_totals, key=user_totals.get)
        if user_totals else None
    )

    return {
        "email": EMAIL,
        "total_events": total_events,
        "unique_users": unique_users,
        "revenue": round(revenue, 2),
        "top_user": top_user
    }
