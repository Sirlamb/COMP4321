import sqlite3
import datetime
from pathlib import Path
from collections import defaultdict
import calendar
from datetime import datetime


# Connect to the documents database
connection = sqlite3.connect('database.db')
cursor = connection.cursor()

def page_id_to_page_info(id) -> tuple[str, str, int]:  
    """
    Get a page's entry in table page_info (title, size, last modified time) from its ID.

    Parameters
    id: The ID of the page.
    
    Returns
    class:`tuple[str, int, int]`
    Tuple containing title, size, last modified time of the page.

    example output: ('Test page', 'Tue, 16 May 2023 05:03:16 GMT', 35)

    
    """
    page_info = cursor.execute("SELECT title, date, size FROM web_info WHERE page_id = ?", (id,)).fetchone()   

    if page_info is None:
        raise ValueError("No page with the given ID is found.")
    
    return page_info

def timestamp_to_datetime(timestamp: int):
    """
    Convert UNIX timestamp to ISO 8601 date and [hh]:[mm]:[ss] time.

    Parameters
    -----------
    timestamp: :class:`int`
        The UNIX timestamp to be converted.
    """

    dt = datetime.strptime(timestamp, "%a, %d %b %Y %H:%M:%S %Z")
    # Convert to Unix timestamp (UTC, no timezone adjustment)
    unix_timestamp = calendar.timegm(dt.utctimetuple())

    return unix_timestamp



def page_id_to_url(id):
    """
    Get a page's entry in table id_url (URL) from its ID.
    Parameters
    id: The ID of the page.
    
    Returns
    The URL of the actual page on the remote server.
    
    """

    # Find entry in table
    url = cursor.execute("SELECT link FROM link_2_id WHERE link_id = ?", (id,)).fetchone()
    return url[0]

def page_id_to_stems(id, num_stems: int = 5, include_title: bool = True) -> list[tuple[str, int]]: #need fix 
    """
    Get the `num_stems` most frequent stemmed keywords of a page from its ID.

    Parameters
    -----------
    id:
        The ID of the page.
    num_stems: 
        Number of stems to return.
    include_title:
        Whether to include the title when counting the stems.

    Returns
    --------
    :class:`list[tuple[str, int]]`
        A list of tuples containing a stem and its frequency in the page.
    """

    # Get list of all stems in the document
    stems_freqs = list(cursor.execute("SELECT keyword_id, count FROM forward_idx WHERE page_id = ?", (id,)))
    
    if include_title:
        stems_freqs += list(cursor.execute("SELECT keyword_id, count FROM title_forward_index WHERE page_id = ?", (id,)))
    
    # Convert stem word IDs to stems
    stems_ids = [stem[0] for stem in stems_freqs]
    freqs = [stem[1] for stem in stems_freqs]
    stems = []
    for stem_id in stems_ids:
        stem= cursor.execute("SELECT keyword FROM keyword_2_id WHERE keyword_id = ?", (stem_id,)).fetchone()[0]
        stems.append(stem)

    # Combine stems and counts
    stems_counts = list(zip(stems, freqs))

    # Merge the keyword together
    dic = defaultdict(int)

    for i, j in stems_counts:
        dic[i] += j

    stems_counts = list(dic.items())

    # Sort and filter to get `num_stems` most frequent stems
    return sorted(stems_counts, key=lambda x: x[1], reverse=True)[0: num_stems]

def page_id_to_links(id, isparent: bool = True) -> list[str]:
    """
    Get the parent/child links of a page from its ID.

    Parameters
    -----------
    id: 
        The ID of the page.
    parent: 
        If true, search for parent links. Otherwise, search for child links.
    
    Returns
        List of parent/child links of the page.
    """

    # Get linked page IDs
    link_ids = []

    if isparent:
        link_ids = cursor.execute("SELECT parent_id FROM parent_child WHERE child_id = ?", (id,)).fetchall()
    else:
        link_ids = cursor.execute("SELECT child_id FROM parent_child WHERE parent_id = ?", (id,)).fetchall()
    
    # Convert ID of each linked page to its URL
    links = []
    for link_id in link_ids:
        link_id_flat = link_id[0]  # Extract ID from its containing tuple
        links.append(page_id_to_url(link_id_flat))
    
    return links


class SearchResult:
    """
    Represents a document retrieved by the search engine.

    Attributes
    -----------
    id: :class:`int`
        The ID of the document.
    score: :class:`float`
        The score of the document.
    title: :class:`str`
        The title of the document.
    time: :class:`int`
        The last modified time of the document.
    time_formatted: :class:`str`
        The last modified time of the document, formatted to string.
    size: :class:`int`
        The size of the document.
    url: :class:`str`
        The URL of the document.
    keywords: :class:`list[tuple[str, int]]`
        The 5 most frequent stemmed keywords (excluding stopwords) in the document, together with their occurence frequencies.
    parent_links: :class:`list[str]`
        The parent links of the document.
    child_links: :class:`list[str]`
        The child links of the document.
    """

    def __init__(self, id: int, score: float, num_keywords: int = 5):
        """
        Inits SearchResult.

        Parameters
        -----------
        num_keywords: :class:`int`
            Controls how many stemmed keywords in the document to be included. Defaults to 5.
        """

        # Initialize ID and score (given)
        self.id = id
        self.score = score

        # Initialize document title, last modified time, size
        page_info = page_id_to_page_info(id)
        self.title = page_info[0]
        self.time = page_info[1]
        self.size = page_info[2]

        # Format last modified time
        self.time_formatte = timestamp_to_datetime(self.time)

        # Initialize document URL
        self.url = page_id_to_url(id)

        # Initialize most frequent stemmed keywords
        self.keywords = page_id_to_stems(id)

        # Initialize parent links
        self.parent_links = page_id_to_links(id, parent=True)

        # Initialize child links
        self.child_links= page_id_to_links(id, parent=False)