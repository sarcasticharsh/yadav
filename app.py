from flask import Flask, render_template, request
import pickle
import pandas as pd
import requests

app = Flask(__name__)

# Load pre-computed data (outside the route function for efficiency)
movies_dict = pickle.load(open('movie_dict.pkl', 'rb'))
movies = pd.DataFrame(movies_dict)
similarity = pickle.load(open('similarity.pkl', 'rb'))

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=6c98798838816eddea5569bc141bfd87".format(movie_id)
    data = requests.get(url)
    data = data.json()

    try:
        poster_path = data['poster_path']
        full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
        return full_path
    except KeyError:
        # Handle potential missing poster data gracefully (e.g., placeholder image)
        return "https://via.placeholder.com/150"  # Placeholder image URL

@app.route('/')
def index():
    return render_template('index.html', movies=movies['title'].values)
@app.route('/recommend', methods=['POST'])
def recommend():
    selected_movie_name = request.form['movie']
    if selected_movie_name:
        try:
            movie_index = movies[movies['title'] == selected_movie_name].index[0]
            movies_list = sorted(list(enumerate(similarity[movie_index])), reverse=True, key=lambda x: x[1])[1:6]

            recommended_movies = []
            recommended_movies_posters = []
            for i in movies_list:
                movie_id = movies.iloc[i[0]].movie_id
                recommended_movies.append(movies.iloc[i[0]].title)
                recommended_movies_posters.append(fetch_poster(movie_id))

            # Pass `zip` to the template
            return render_template(
                'recommend.html',
                recommended_movies=recommended_movies,
                recommended_movies_posters=recommended_movies_posters,
                zip=zip  # Explicitly pass `zip` to the template
            )
        except (IndexError, KeyError):
            return render_template('error.html', message="Movie not found or poster unavailable.")
    else:
        return render_template('index.html', movies=movies['title'].values, error="Please select a movie.")


if __name__ == '__main__':
    app.run(debug=True)