import sqlite3
import csv

conn = sqlite3.connect("track_metadata.db")
cur = conn.cursor()


def clean_text(text):
    if text is None:
        return text

    replacements = {
        "Ð": "D",
        "Á": "A",
        "Í": "I",
        "Đ": "D",
        "Č": "C",
        "Š": "S",
        "Ž": "Z",
    }

    text = text.translate(str.maketrans(replacements))
    text = text.replace("\x13", "-")  # Control character (possible corrupted dash)
    text = text.replace("\x19", "'")  # Control character (corrupted apostrophe)

    return text


# Duplicate example: SOPWKOX12A8C139D43
cur.execute(
    """
    SELECT 
        s.song_id, 
        sc."index" AS song_code, 
        COALESCE(NULLIF(s.title, ''), 'Unknown title') AS title, 
        COALESCE(NULLIF(s.release, ''), 'Unknown Release') AS release, 
        COALESCE(s.year, 0) AS year, 
        COALESCE(s.duration, 0.0) AS duration,
        NULL AS thumbnail_url, 
        s.artist_id 
    FROM (
        SELECT song_id, title, release, year, duration, artist_id,
            ROW_NUMBER() OVER (PARTITION BY song_id ORDER BY year DESC, title ASC) AS rn
        FROM songs
    ) AS s 
    INNER JOIN 
        song_codes AS sc 
    ON s.song_id = sc.song_id 
    WHERE 
        sc."index" IS NOT NULL AND
        s.rn = 1;
    """
)

with open("songs.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(
        [
            "song_id",
            "song_code",
            "title",
            "release",
            "year",
            "duration",
            "thumbnail_url",
            "artist_id",
        ]
    )

    # writer.writerows(cur.fetchall())

    for row in cur:
        cleaned_row = list(row)
        cleaned_row[2] = clean_text(row[2])
        cleaned_row[3] = clean_text(row[3])
        writer.writerow(cleaned_row)

conn.close()
