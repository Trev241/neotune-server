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


# Bad artists examples:
#   AR2O1PB1187B9B29EA (Bad character)
#   ARZNC3M1187FB392CC (Duplicate)
# cur.execute("SELECT * FROM songs WHERE artist_id = 'AR2O1PB1187B9B29EA'")
# print(cur.fetchall())

# psql command
# \COPY artists(id, name, bio, image_url) FROM 'artists.csv' WITH (FORMAT CSV, HEADER);

cur.execute(
    """
    SELECT DISTINCT
        s.artist_id AS id, 
        s.artist_name AS "name", 
        NULL as bio, 
        NULL as image_url 
    FROM (
        SELECT artist_id, artist_name,
            ROW_NUMBER() OVER (PARTITION BY artist_id ORDER BY artist_name ASC) AS rn
        FROM songs
        INNER JOIN song_codes USING (song_id)
        WHERE "index" IS NOT NULL
    ) AS s
    WHERE s.rn = 1;
    """
)

with open("artists.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "name", "bio", "image_url"])

    # writer.writerows(cur.fetchall())

    for row in cur:
        cleaned_row = list(row)
        cleaned_row[1] = clean_text(row[1])
        writer.writerow(cleaned_row)

conn.close()
