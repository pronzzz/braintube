import sqlite3
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = "braintube.sqlite3"

def init_db():
    """ Initializes the SQLite database for the multi-video library memory. """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS videos (
            id TEXT PRIMARY KEY,
            url TEXT,
            title TEXT,
            summary TEXT,
            transcription_path TEXT,
            vectorstore_path TEXT,
            created_at TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()
    logger.info("Initialized memory SQLite database.")

def save_video(video_id: str, url: str, title: str, summary: str, transcription_path: str, vectorstore_path: str):
    """ Saves video metadata and paths to db. """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO videos (id, url, title, summary, transcription_path, vectorstore_path, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (video_id, url, title, summary, transcription_path, vectorstore_path, datetime.now()))
    conn.commit()
    conn.close()
    logger.info(f"Saved video {video_id} to library.")

def get_all_videos():
    """ Retrieves the entire multi-video library directory from memory. """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, url, title, summary, created_at FROM videos ORDER BY created_at DESC')
    rows = cursor.fetchall()
    conn.close()
    
    videos = []
    for row in rows:
        videos.append({
            "id": row[0],
            "url": row[1],
            "title": row[2],
            "summary": row[3],
            "created_at": row[4]
        })
    return videos
