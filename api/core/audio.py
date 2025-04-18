import os
import json
from pathlib import Path

import yt_dlp
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


class AudioDownloader:
    def __init__(self):
        self.yt = yt_dlp.YoutubeDL(
            {
                "noplaylist": True,
                "outtmpl": "output/%(title)s.%(ext)s",
                "format": "bestaudio",
            }
        )

    def download(self, song_id, q, artist):
        info = self.yt.extract_info(f"ytsearch1:{q} by {artist}", download=True)

        with open("output/dump.json", "w") as f:
            processed_info = self.yt.sanitize_info(info)
            json.dump(processed_info, f, indent=2)

        url = None
        thumbnail = None
        filename = None

        if "entries" in info and info["entries"]:
            url = info["entries"][0]["url"]
            thumbnail = info["entries"][0]["thumbnails"][-1]

            filepath = info["entries"][0]["requested_downloads"][0]["filepath"]
            common = os.path.commonpath([filepath, os.getcwd()])
            rel_path = filepath.replace(common, "")[1:]
            filename = os.path.basename(rel_path)

        details = {
            "url": url,
            "filepath": rel_path,
            "filename": filename,
            "thumbnail": thumbnail,
        }

        Path("output/metadata").mkdir(parents=True, exist_ok=True)
        with open(f"output/metadata/{song_id}.json", "w") as f:
            json.dump(details, f, indent=2)

        return details


class Recommender:
    def __init__(self, embeddings_path="song_embeddings.npy"):
        self.embeddings = np.load(embeddings_path)

    def find_similar_songs(self, song_code, top_k=5):
        song_embedding = self.embeddings[song_code].reshape(1, -1)

        # Compute cosine similarity between the input song and all songs
        similarities = cosine_similarity(song_embedding, self.embeddings).flatten()

        top_indices = np.argsort(similarities)[::-1][: top_k + 1]
        top_scores = similarities[top_indices]
        # Exclude the input song
        top_indices = top_indices[top_indices != song_code][:top_k]
        top_scores = top_scores[: len(top_indices)]

        return top_indices, top_scores
