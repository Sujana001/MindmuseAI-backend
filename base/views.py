import os
import openai
from rest_framework.decorators import api_view
from rest_framework.response import Response
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv

load_dotenv()

@api_view(['POST'])
def recommend_music(request):
    mood = request.data.get("mood", "")
    journal = request.data.get("journal", "")

    prompt = f"""
    Based on the following mood and journal, suggest a music genre and matching Spotify playlist idea:
    Mood: {mood}
    Journal: {journal}
    Please reply with only a genre or keyword.
    """

    # OpenRouter setup
    openai.api_key = os.getenv("OPENROUTER_API_KEY")
    openai.api_base = "https://openrouter.ai/api/v1"

    gpt_response = openai.ChatCompletion.create(
        model="mistralai/mistral-7b",
        messages=[{"role": "user", "content": prompt}]
    )

    mood_genre = gpt_response["choices"][0]["message"]["content"].strip()

    # Spotify search
    sp = Spotify(auth_manager=SpotifyClientCredentials(
        client_id=os.getenv("SPOTIFY_CLIENT_ID"),
        client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
    ))

    results = sp.search(q=mood_genre, type='playlist', limit=3)
    playlists = [
        {"name": p["name"], "url": p["external_urls"]["spotify"]}
        for p in results["playlists"]["items"]
    ]

    return Response({
        "mood_summary": mood_genre,
        "recommendations": playlists
    })
