# from flask import Flask, request, render_template, redirect, url_for, jsonify
# import pandas as pd
# import numpy as np
# import pickle

# app = Flask(__name__)

# # Load the preprocessed data and similarity matrix
# with open('preprocessed_data.pkl', 'rb') as f:
#     new_df = pickle.load(f)
# with open('similarity_matrix.pkl', 'rb') as f:
#     similarity = pickle.load(f)

# def recommend(anime, sort_by=None, order='asc', filter_genre=None):
#     if anime not in new_df['Name'].values:
#         return None

#     anime_index = new_df[new_df['Name'] == anime].index[0]
#     distances = similarity[anime_index]
#     anime_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
#     recommendations = []

#     for i in anime_list:
#         row = new_df.iloc[i[0]]
#         if filter_genre and filter_genre not in row['Genres']:
#             continue
#         recommendations.append({
#             'Name': row['Name'],
#             'Genres': ', '.join(row['Genres']),
#             'Episodes': row['Episodes'],
#             'Score': row['Score'],
#             'Type': row['Type'],
#             'Rating': row['Rating'],
#             'Links': row['Links']
#         })

#     if sort_by and sort_by != 'Genres':
#         recommendations = sorted(recommendations, key=lambda x: float(x[sort_by]) if x[sort_by] != 'UNKNOWN' else float('inf'), reverse=(order == 'desc'))

#     available_genres = sorted(set(genre for rec in recommendations for genre in rec['Genres'].split(', ')))
    
#     return recommendations, available_genres

# @app.route('/')
# def home():
#     return render_template('index01.html')

# @app.route('/recommend', methods=['POST'])
# def get_recommendations():
#     anime_name = request.form['anime_name']
#     return redirect(url_for('show_recommendations', anime_name=anime_name))

# @app.route('/recommendations/<anime_name>')
# def show_recommendations(anime_name):
#     sort_by = request.args.get('sort_by')
#     order = request.args.get('order', 'asc')
#     filter_genre = request.args.get('filter_genre')
#     recommendations, available_genres = recommend(anime_name, sort_by=sort_by, order=order, filter_genre=filter_genre)
#     return render_template('recommendations.html', recommendations=recommendations, anime_name=anime_name, sort_by=sort_by, order=order, available_genres=available_genres, filter_genre=filter_genre)

# @app.route('/search', methods=['GET'])
# def search():
#     query = request.args.get('query', '')
#     results = new_df[new_df['Name'].str.contains(query, case=False, na=False)]['Name'].tolist()
#     return jsonify(results)

# if __name__ == '__main__':
#     app.run(debug=True)



from flask import Flask, request, render_template, redirect, url_for, jsonify
import pandas as pd
import numpy as np
import pickle
import boto3
from botocore.exceptions import NoCredentialsError
import os

app = Flask(__name__)

# AWS S3 settings from environment variables
S3_BUCKET = os.getenv('S3_BUCKET', 'animerecommend')
S3_KEY = os.getenv('S3_KEY', 'similarity_matrix.pkl')
S3_REGION = os.getenv('S3_REGION', 'ap-south-1')
S3_URL = f'https://animerecommend.s3.ap-south-1.amazonaws.com/similarity_matrix.pkl'

# Download function for S3
def download_from_s3(bucket_name, file_key, download_path):
    s3 = boto3.client('s3', region_name=S3_REGION)
    try:
        s3.download_file(bucket_name, file_key, download_path)
    except NoCredentialsError:
        print('Credentials not available')

# Local file paths
similarity_matrix_path = 'similarity_matrix.pkl'

# Download the file from S3 if not already present
# download_from_s3(S3_BUCKET, S3_KEY, similarity_matrix_path)

# Load the preprocessed data and similarity matrix
with open('preprocessed_data.pkl', 'rb') as f:
    new_df = pickle.load(f)
with open(similarity_matrix_path, 'rb') as f:
    similarity = pickle.load(f)

def recommend(anime, sort_by=None, order='asc', filter_genre=None):
    if anime not in new_df['Name'].values:
        return None

    anime_index = new_df[new_df['Name'] == anime].index[0]
    distances = similarity[anime_index]
    anime_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]
    recommendations = []

    for i in anime_list:
        row = new_df.iloc[i[0]]
        if filter_genre and filter_genre not in row['Genres']:
            continue
        recommendations.append({
            'Name': row['Name'],
            'Genres': ', '.join(row['Genres']),
            'Episodes': row['Episodes'],
            'Score': row['Score'],
            'Type': row['Type'],
            'Rating': row['Rating'],
            'Links': row['Links']
        })

    if sort_by and sort_by != 'Genres':
        recommendations = sorted(recommendations, key=lambda x: float(x[sort_by]) if x[sort_by] != 'UNKNOWN' else float('inf'), reverse=(order == 'desc'))

    available_genres = sorted(set(genre for rec in recommendations for genre in rec['Genres'].split(', ')))
    
    return recommendations, available_genres

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/recommend', methods=['POST'])
def get_recommendations():
    anime_name = request.form['anime_name']
    return redirect(url_for('show_recommendations', anime_name=anime_name))

@app.route('/recommendations/<anime_name>')
def show_recommendations(anime_name):
    sort_by = request.args.get('sort_by')
    order = request.args.get('order', 'asc')
    filter_genre = request.args.get('filter_genre')
    recommendations, available_genres = recommend(anime_name, sort_by=sort_by, order=order, filter_genre=filter_genre)
    return render_template('recommendations.html', recommendations=recommendations, anime_name=anime_name, sort_by=sort_by, order=order, available_genres=available_genres, filter_genre=filter_genre)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    results = new_df[new_df['Name'].str.contains(query, case=False, na=False)]['Name'].tolist()
    return jsonify(results)

if __name__ == '__main__':
    # Run on all IP addresses and default port (8000 for Versal)
    app.run(debug=True)
