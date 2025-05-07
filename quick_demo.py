from nltk.stem import PorterStemmer as Stemmer
import sqlite3
from zlib import crc32
from pathlib import Path
from itertools import chain
from collections import Counter
import numpy as np

db_path = 'database.db'

# Initialize the database
connection = sqlite3.connect(db_path)
cursor = connection.cursor()


def createAdjMatrix(allPages):
    "input list[int] of all page ids, output adjacency matrix"
    matrixMap = {key: {val: 0 for val in allPages} for key in allPages}

    for page in allPages:
        children = cursor.execute("SELECT child_id FROM parent_child WHERE parent_id = ?", (page,)).fetchall()
        for child in children:
            matrixMap[page][child[0]] = 1

    matrixList = [[val for val in matrixMap[key].values()] for key in matrixMap.keys()]
    return np.array(matrixList).T

def page_rank(curPageRankScore: np.ndarray[int], adjacency_matrix: np.ndarray[np.ndarray[int]],
              teleportation_probability: float, max_iterations: int = 100) -> np.ndarray[int]:
    # Initialize the PageRank scores with a uniform distribution
    page_rank_scores = curPageRankScore

    # Iteratively update the PageRank scores
    for _ in range(max_iterations):
        # Perform the matrix-vector multiplication
        new_page_rank_scores = adjacency_matrix.dot(page_rank_scores)

        # Add the teleportation probability
        new_page_rank_scores = teleportation_probability + (1 - teleportation_probability) * new_page_rank_scores
        # Check for convergence
        if np.allclose(page_rank_scores, new_page_rank_scores):
            break

    page_rank_scores = new_page_rank_scores
    return page_rank_scores


allPages = [page[0] for page in cursor.execute("SELECT page_id FROM id_url").fetchall()]
adjacencyMatrix = createAdjMatrix(allPages)
pageRankScores = page_rank(np.ones(len(allPages)), adjacencyMatrix, 0.85)

#create the pagerank table here 


