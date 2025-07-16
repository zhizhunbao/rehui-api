from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from services.rank_service import RankService

app = FastAPI()
rank_service = RankService()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/ping")
def ping():
    return {"msg": "pong"}

@app.get("/api/rank/top")
def get_top_rank(
        limit: int = Query(5, ge=1, le=50),
        city: str = Query(None),
        make: str = Query(None)
):
    return rank_service.get_top_rank(limit=limit, city=city, make=make)

@app.get("/")
def default_top10():
    return rank_service.get_top_rank(limit=10, city=None, make=None)
