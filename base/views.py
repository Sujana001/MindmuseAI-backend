import os
from openai import OpenAI
from openai import OpenAIError
from openai._client import OpenAI as OpenAIClient
from rest_framework.decorators import api_view
from rest_framework.response import Response
from spotipy import Spotify
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to the MindmuseAI backend")

load_dotenv()

@api_view(['POST'])
def recommend_music(request):
    print("Request data:", request.data)

    mood = request.data.get("mood", "").strip()
    journal = request.data.get("journal", "").strip()

    if not mood or not journal:
        print("Missing mood or journal")
        return Response({"error": "Missing mood or journal"}, status=400)

    if mood.lower() == "chat":
        prompt = f"""
        You are a supportive mental health assistant.
        Respond to the user's journal entry with encouragement and empathy.

        Journal: {journal}
        """
    else:
        prompt = f"""
        Based on the user's mood (emoji or word) and journal entry,
        suggest one music genre (like 'lofi', 'pop', 'ambient'):

        Mood: {mood}
        Journal: {journal}

        Only reply with one word (the genre or keyword).
        """

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.getenv("OPENROUTER_API_KEY"),
        default_headers={
            "HTTP-Referer": "https://github.com/Sujana001/MindmuseAI-backend",
            "X-Title": "MindmuseAI"
        }
    )

    try:
        gpt_response = client.chat.completions.create(
            model="mistralai/mistral-7b-instruct",
            messages=[{"role": "user", "content": prompt}],
        )
        mood_genre = gpt_response.choices[0].message.content.strip()
    except Exception as e:
        print("OpenRouter Error:", str(e))
        return Response({"error": "AI generation failed"}, status=500)

    if mood.lower() == "chat":
        return Response({"mood_summary": mood_genre})

    try:
        sp = Spotify(auth_manager=SpotifyClientCredentials(
            client_id=os.getenv("SPOTIFY_CLIENT_ID"),
            client_secret=os.getenv("SPOTIFY_CLIENT_SECRET")
        ))

        results = sp.search(q=mood_genre, type='playlist', limit=3)
        playlists = [
            {"name": p["name"], "url": p["external_urls"]["spotify"]}
            for p in results["playlists"]["items"]
        ]
    except Exception as e:
        print("Spotify error:", e)
        playlists = []

    if not playlists:
        playlists = [{"name": "Open Spotify", "url": "https://open.spotify.com"}]

    return Response({
        "mood_summary": mood_genre,
        "recommendations": playlists
    })
