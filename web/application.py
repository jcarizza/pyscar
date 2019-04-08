"""
main web module
"""

from flask import (
    Flask,
    render_template,
    request
)

from filters import fix_url
from utils import Paginator
from search import Searcher

app = Flask(__name__)

app.jinja_env.filters["fix_url"] = fix_url


@app.route('/', methods=['GET'])
def search():
    query = request.args.get("q")
    if query is None:
        return render_template("index.html")

    try:
        page = int(request.args.get("p", 1))
    except (TypeError, ValueError):
        page = 1

    searcher = Searcher()
    results = searcher.search_page(query, page)
    paginator = Paginator(results)
    return render_template("index.html",
                           results=results,
                           paginator=paginator,
                           q=query)
