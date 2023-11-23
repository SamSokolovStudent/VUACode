from flask import Blueprint, render_template, request, redirect, url_for
from database import ResearchPaperDB as db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('search.html')

@main.route('/search', methods=['POST'])
def search():
    query = request.form.get('query')
    if query:
        query_embedding = db.embed_query(query)
        similar_documents = db.find_similar_documents(
            embedding=query_embedding,
            index_name="paperSearchIndex",
            embedding_field="embedding"
        )
        return redirect(url_for('main.results', documents=similar_documents))
    return render_template('search.html')

@main.route('/results')
def results():
    documents = request.args.get('documents', [])
    return render_template('results.html', documents=documents)

@main.route('/top-results')
def top_results():
    documents = request.args.get('documents', [])
    top_3 = documents[:3]
    return render_template('top_results.html', top_3=top_3)
