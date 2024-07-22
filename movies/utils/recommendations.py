import numpy as np


def recommend(user_id, user_movie_ratings, user_similarity, top_n=10):
    user_index = user_id - 1
    similar_users = np.argsort(-user_similarity[user_index])[1:]
    recommendations = {}

    for similar_user in similar_users:
        for movie_id, rating in enumerate(user_movie_ratings.iloc[similar_user]):
            if user_movie_ratings.iloc[user_index, movie_id] == 0:
                if movie_id not in recommendations:
                    recommendations[movie_id] = rating
                else:
                    recommendations[movie_id] += rating
    return sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:top_n]
