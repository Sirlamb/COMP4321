from flask import Flask, render_template, make_response, request
import timeit
from typing import List
import json

from src import retriever  
from src.util import SearchResult

import numpy as np
import re
from math import log2
from time import time
from nltk.stem import PorterStemmer as Stemmer
import sqlite3
from zlib import crc32
from pathlib import Path
from itertools import chain
from collections import Counter
import sqlite3
import os 


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
    query: str = request.form.get('searchbar')

    if not query:
        query = request.form.get('history')

    if not query:
        query = ""

    # Time the search operation
    start_time = timeit.default_timer()

    # Pass query into search engine
    search_results_raw = retriever.search_engine(query)
    search_time_taken = timeit.default_timer() - start_time

    # Pass query 

    search_results_raw = retriever.search_engine(query)
    print(search_results_raw)
    end_time = timeit.default_timer()
    search_time_taken = end_time - start_time

    # Get data of the search results
    # k: page ID
    # v: page score
    search_results = []
    for key, val in sorted(search_results_raw.items(), key=lambda x: x[1], reverse=True):  # Sort the search results by score
        if val != 0:
            search_results.append(SearchResult(key, val))

    print(search_results)

    # Get search history
    history = json.loads(request.cookies.get('history', default="{}"))

    # Get search history
    history = json.loads(request.cookies.get('history', default="{}"))

    # Set up response
    res = make_response(
        render_template(
            "search_history.html",
            QUERY=query,
            RESULTS=search_results,
            TIME_TAKEN=search_time_taken,
            HISTORY=history
        )
    )

    # Add query to search history
    history: List[str] = json.loads(request.cookies.get('history', default="[]"))
    if (query not in history) and (query != ""):
        history.append(query)
    res.set_cookie("history", json.dumps(history))

    return res


if __name__ == '__main__':
    app.run(debug = True)
