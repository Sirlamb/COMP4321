from flask import Flask, render_template, make_response, request
import timeit
from typing import List
import json

from src import retriever   #src is a folder in the same directory as app.py
from src.util import SearchResult

app = Flask(__name__)

@app.route("/")
def searchbar():
    """
    Displays the homepage and search bar of the search engine.
    """
    history = json.loads(request.cookies.get('history', default="{}"))
    return render_template("index.html",HISTORY=history)


@app.route("/search/", methods=['POST'])
def submit_search():
    """
    Performs the search and displays the results in the webpage.
    """

    # Get query from search bar
    query = request.form.get('searchbar')
    # or history dropdown menu
    if not query:
        query = request.form.get('history')


    # Time the search operation
    start_time = timeit.default_timer()

    # Pass query into search engine and calulate time taken 
    query_parsed = retriever.parse_string(query)
    search_results_raw = retriever.search_engine(query_parsed)
    search_results_raw = retriever.search_engine([])  # DEBUG SKIP
    search_results_raw = retriever.search_engine(query)
    search_time_taken = timeit.default_timer() - start_time

    # Get data of the search results
    # k: page ID
    # v: page score
    search_results = []
    for key, val in sorted(search_results_raw.items(), key=lambda x: x[1], reverse=True):  # Sort the search results by score
        if val != 0:
            search_results.append(SearchResult(key, val))

    # Get search history
    history = json.loads(request.cookies.get('history', default="{}"))

    # Set up response
    res = make_response(
        render_template(
            "search_results.html",
            QUERY=query,
            RESULTS=search_results,
            TIME_TAKEN=search_time_taken,
            HISTORY=history
        )
    )

    # Add query to search history
    history = json.loads(request.cookies.get('history', default="[]"))
    if (query not in history) and (query != ""):
        history.append(query)
    res.set_cookie("history", json.dumps(history))

    return res


if __name__ == '__main__':
    app.run(debug = True)
