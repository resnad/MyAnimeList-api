from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel
import sqlite3
from typing import List

app = FastAPI(title="Top Anime API", description="API for accessing top 500 anime data from MyAnimeList")

def get_db_connection():
    conn = sqlite3.connect('top_anime.db')
    conn.row_factory = sqlite3.Row
    return conn

class Anime(BaseModel):
    rank: int
    title: str
    href: str
    score: float
    type_episodes: str
    aired: str
    members: int

@app.get("/")
async def root():
    return {"message": "Welcome to the Top Anime API"}

@app.get("/anime/{rank}", response_model=Anime)
async def get_anime_by_rank(rank: int):
    conn = get_db_connection()
    anime = conn.execute('SELECT * FROM anime WHERE rank = ?', (rank,)).fetchone()
    conn.close()
    
    if anime is None:
        raise HTTPException(status_code=404, detail="Anime not found")
    
    return dict(anime)

@app.get("/top", response_model=List[Anime])
async def get_top_anime(limit: int = Query(default=10, le=500)):
    conn = get_db_connection()
    anime_list = conn.execute('SELECT * FROM anime ORDER BY rank LIMIT ?', (limit,)).fetchall()
    conn.close()
    
    return [dict(anime) for anime in anime_list]

@app.get("/search", response_model=List[Anime])
async def search_anime(query: str, limit: int = Query(default=10, le=100)):
    conn = get_db_connection()
    anime_list = conn.execute('SELECT * FROM anime WHERE title LIKE ? ORDER BY rank LIMIT ?', 
                              (f'%{query}%', limit)).fetchall()
    conn.close()
    
    return [dict(anime) for anime in anime_list]

@app.get("/stats")
async def get_stats():
    conn = get_db_connection()
    total_anime = conn.execute('SELECT COUNT(*) FROM anime').fetchone()[0]
    avg_score = conn.execute('SELECT AVG(score) FROM anime').fetchone()[0]
    top_type = conn.execute('''
        SELECT type_episodes, COUNT(*) as count 
        FROM anime 
        GROUP BY type_episodes 
        ORDER BY count DESC 
        LIMIT 1
    ''').fetchone()
    conn.close()
    
    return {
        "total_anime": total_anime,
        "average_score": round(avg_score, 2),
        "most_common_type": top_type['type_episodes'],
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)