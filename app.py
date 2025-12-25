from flask import Flask, render_template, request
import pickle
import numpy as np

# Load pickles
popular_df = pickle.load(open('popular.pkl','rb'))
pt = pickle.load(open('pt.pkl','rb'))
books = pickle.load(open('books.pkl','rb'))
similarity_scores = pickle.load(open('similarity_scores.pkl','rb'))

# Clean column names to avoid KeyError
for df in [popular_df, books]:
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace('-', ' ')

# Auto-detect the Book Author column
author_col_popular = [col for col in popular_df.columns if 'book' in col.lower() and 'author' in col.lower()][0]
author_col_books = [col for col in books.columns if 'book' in col.lower() and 'author' in col.lower()][0]

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=list(popular_df['Book-Title'].values),
                           author=list(popular_df[author_col_popular].values),
                           image=list(popular_df['Image-URL-M'].values),
                           votes=list(popular_df['num_ratings'].values),
                           rating=list(popular_df['avg_rating'].values)
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input')
    
    if user_input not in pt.index:
        return render_template('recommend.html', data=[], message="Book not found!")

    index = np.where(pt.index == user_input)[0][0]
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:5]

    data = []
    for i in similar_items:
        temp_df = books[books['Book-Title'] == pt.index[i[0]]].drop_duplicates('Book-Title')
        item = [
            temp_df['Book-Title'].values[0],
            temp_df[author_col_books].values[0],
            temp_df['Image-URL-M'].values[0]
        ]
        data.append(item)

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(debug=True)
