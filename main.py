import os
import pickle
from typing import Optional,List,Dict,Any,Tuple,Literal, Annotated
from fastapi import FastAPI,HTTPException,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel,field_validator,Field
from dotenv import load_dotenv
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import requests

folder_path = r"D:\Movie Recommneder system\data"

load_dotenv()

app=FastAPI()

BASE_URL = "https://api.themoviedb.org/3/"
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w500"
TOKEN=os.getenv('TMDB_API_TOKEN')

headers = {
    "accept": "application/json",
    "Authorization": f"Bearer {TOKEN}"
}

loaded_files = {}

for filename in os.listdir(folder_path):
    if filename.endswith(".pkl"):
        file_path = os.path.join(folder_path, filename)

        with open(file_path, "rb") as f:
            loaded_files[filename] = pickle.load(f)

df = loaded_files["df.pkl"]
indices = loaded_files["indices.pkl"]
tfidf_matrix = loaded_files["tfidf_matrix.pkl"]

class UserInput(BaseModel):
    title: Annotated[str, Field(
            min_length=1,
            max_length=100,
            description="Movie title",
            examples=["Avatar"]
        )]



def movie_poster(path: str):
    return f"{IMAGE_BASE_URL}{path}"

@app.get("/health",status_code=200)
def liveness_check():
    return {"status":"ok"}



indices_lower = {
    str(title).strip().lower(): idx
    for title, idx in indices.items()
}

@app.get("/home")
def home(category: str = "popular"):

    if category == "trending":
        url = f"{BASE_URL}/trending/movie/day"
    else:
        url = f"{BASE_URL}/movie/{category}"

    response = requests.get(
        url,
        headers=headers
    )

    if response.status_code == 200:

        data = response.json()

        movies = []

        for movie in data["results"]:

            movies.append(
                {
                    "tmdb_id": movie["id"],
                    "title": movie["title"],
                    "poster_url": movie_poster(movie["poster_path"]) if movie["poster_path"] else None,
                    "rating": movie["vote_average"],
                    "release_date": movie["release_date"]
                }
            )

        return movies

    return {"error": "Could not fetch movies"}


def recommend(title, n=10):
    title = title.strip().lower()
    if title not in indices_lower:
        return []

    idx = indices_lower[title]
    qv = tfidf_matrix[idx]
    sim_score =  (tfidf_matrix @ qv.T).toarray().ravel()

    similar_idx = sim_score.argsort()[::-1][1:n+1]

    return df["title"].iloc[similar_idx].tolist()

@app.post("/recommend")

def get_recommend(userinput:UserInput,n:int=10):
    movies = []
    recommendations=recommend(userinput.title,n)
    
    for title in recommendations:

        url = f"{BASE_URL}/search/movie"

        params = {
            "query": title
        }

        response = requests.get(url, params=params, headers=headers)

        if response.status_code == 200:

            data = response.json()

            if data["results"]:

                movie = data["results"][0]

                movies.append({
                    "title": movie["title"],
                    "poster_url": movie_poster(movie["poster_path"]) if movie["poster_path"] else None,
                    "rating": movie["vote_average"],
                    "release_date": movie["release_date"],
                    "tmdb_id": movie["id"]
                })

    return {
        "recommendations": movies
    }

@app.get("/search")
def search_movie(title:str):
    url=f"{BASE_URL}/search/movie"
    params={
        "query":title
    }
    response=requests.get(url,params=params,headers=headers)
    if response.status_code == 200:
        data=response.json()
        movies = []
        for movie in data["results"]:
                movies.append(
                    {
                        "title": movie["title"],
                        "poster_url": movie_poster(movie["poster_path"]) if movie["poster_path"] else None,
                        "rating": movie["vote_average"],
                        "release_date": movie["release_date"],
                        "tmdb_id": movie["id"]
                    }
                )

        return movies
    else:
        return {"error": "Movie not found"}


@app.get("/movie_details")
def movie_details(title:str):
    url=f"{BASE_URL}/search/movie"
    params={
        "query":title
    }
    response=requests.get(url,params=params,headers=headers)
    if response.status_code == 200:
        data = response.json()

        if not data["results"]:
            return {"error": "Movie not found"}

        movie = data["results"][0]

        return {
            "title": movie["title"],
            "overview": movie["overview"],
            "original_language": movie["original_language"]
        }
    else:
        return {"error": "TMDB request failed"}
    
@app.get("/popular_movies")
def popular_movies():
    url=f"{BASE_URL}/movie/popular"

    response=requests.get(url,headers=headers)

    if response.status_code == 200:
        data=response.json()
        return [i["title"] for i in data["results"]]

    return {"error": "Could not fetch popular movies"}

@app.get("/trending_movies")
def trending_movies(time_window: str = "day"):
    url=f"{BASE_URL}/trending/movie/{time_window}"
   
    response=requests.get(url,headers=headers)

    if response.status_code == 200:
        if time_window not in ["day", "week"]:
            return {"error": "time_window must be 'day' or 'week'"}
        data=response.json()
        return [i["title"] for i in data["results"]]

    return {"error": "Could not fetch trending movies"}

