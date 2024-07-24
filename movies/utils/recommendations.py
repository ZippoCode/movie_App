import numpy as np
import pandas as pd


def weighted_rating(x, m, c):
    v = x['num_votes']
    r = x['average_rating']
    if v >= m:
        return (v / (v + m) * r) + (m / (m + v) * c)
    else:
        return c


def build_measure(df: pd.DataFrame, percentile=0.95, minimum_votes=5):
    num_votes = df[df['num_votes'] > minimum_votes]['num_votes'].astype('int')
    average_ratings = df[df['average_rating'].notnull()]['average_rating'].astype('int')
    c = average_ratings.mean()
    m = num_votes.quantile(percentile)
    return c, m


def build_chart(df: pd.DataFrame, genre: str, num_elements: int):
    s = df.apply(lambda x: pd.Series(x['genres']), axis=1).stack().reset_index(level=1, drop=True)
    s.name = 'genre'
    gen_md = df.drop('genres', axis=1).join(s)
    df = gen_md[gen_md['genre'] == genre]

    c, m = build_measure(df)
    qualified = df[(df['num_votes'] >= m) & (df['num_votes'].notnull()) & (df['average_rating'].notnull())][
        ['title', 'release_year', 'num_votes', 'average_rating', 'popularity']]
    qualified['num_votes'] = qualified['num_votes'].astype('int')
    qualified['average_rating'] = qualified['average_rating'].astype('int')

    qualified['wr'] = qualified.apply(lambda x: weighted_rating(x, m, c), axis=1)
    qualified = qualified.sort_values('wr', ascending=False).head(num_elements)

    return qualified


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
