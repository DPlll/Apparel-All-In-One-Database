import os
import sqlite3
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pipeline.database import get_connection
from api.routes import products, brands, search, clicks

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    db_path = os.getenv("DB_PATH", "./data/products.db")
    db_dir = os.path.dirname(db_path)
    if db_dir:
        os.makedirs(db_dir, exist_ok=True)
    app.state.db = get_connection(db_path)
    yield
    app.state.db.close()


app = FastAPI(title="Bikini Catalog API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(products.router)
app.include_router(brands.router)
app.include_router(search.router)
app.include_router(clicks.router)


@app.get("/health")
def health():
    return {"status": "ok"}
