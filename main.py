import os
import psycopg2

from fastapi import FastAPI
from dotenv import load_dotenv

app = FastAPI()

load_dotenv()

DB_CONNECTION_URL = os.getenv("DB_CONNECTION_URL")
conn = psycopg2.connect(DB_CONNECTION_URL)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/init")
async def init():
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            user_id INT PRIMARY KEY AUTO INCREMENT, 
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password VARCHAR(100) NOT NULL,
        );

        CREATE TABLE IF NOT EXISTS songs (
            song_id VARCHAR(48) PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            release VARCHAR(100),
            year INT,
            duration FLOAT
        );

        CREATE TABLE IF NOT EXISTS artists (
            artist_id VARCHAR(48) PRIMARY KEY,
            mbid VARCHAR(100),
            name VARCHAR(100),
        );
        
        CREATE TABLE IF NOT EXISTS songs_artists (
            song_id VARCHAR(48) REFERENCES songs (song_id)
            artist_id VARCHAR(48) REFERENCES artists (artist_id)
        );

        CREATE TABLE IF NOT EXISTS playlists (
            playlist_id INT PRIMARY KEY AUTO INCREMENT,
            name VARCHAR(45),
            created_at TIMESTAMP CURRENT_TIMESTAMP
        )
        """
    )
