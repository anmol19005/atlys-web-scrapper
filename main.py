import os
import logging
from fastapi import FastAPI, Depends, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from sqlalchemy.orm import Session

import config
from database import SessionLocal, engine, Base
from schemas import ScrapeSettings, ScrapeResponse
from scraper import Scraper

load_dotenv()


Base.metadata.create_all(bind=engine)

app = FastAPI()
security = HTTPBearer()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != config.Config.API_TOKEN:
        raise HTTPException(status_code=403, detail="Invalid or missing token")


@app.post("/scrape", response_model=ScrapeResponse)
async def scrape(scrape_settings: ScrapeSettings, db: Session = Depends(get_db), token: str = Depends(verify_token)):
    try:
        scraper = Scraper(scrape_settings, db)
        results = await scraper.scrape()
        return results
    except Exception as e:
        logger.error(f"Scraping failed: {e}")
        raise HTTPException(status_code=500, detail="Scraping failed")
