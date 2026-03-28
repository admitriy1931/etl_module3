"""Flatten nested XML into tabular structures."""

from pathlib import Path
from typing import Dict, List

import pandas as pd
from lxml import etree

from utils.logger import get_logger
from utils.io_helpers import read_xml_file, save_dataframe
from webinar_2.schemas import (
    BOOK_COLUMNS, BOOK_TAG_COLUMNS, BOOK_REVIEW_COLUMNS,
)

log = get_logger(__name__)


def flatten_xml(input_path: str, output_dir: str) -> Dict[str, pd.DataFrame]:
    """Read nested XML and produce flat DataFrames for each entity."""
    root = read_xml_file(input_path)

    books_rows: List[dict] = []
    tags_rows: List[dict] = []
    reviews_rows: List[dict] = []

    for store in root.findall(".//store"):
        store_name = store.get("name", "")
        store_city = store.get("city", "")

        for category in store.findall("category"):
            cat_name = category.get("name", "")

            for book in category.findall("book"):
                book_id = book.get("id", "")
                title_el = book.find("title")
                title = title_el.text if title_el is not None else ""

                author = book.find("author")
                author_fn = ""
                author_ln = ""
                if author is not None:
                    fn_el = author.find("first_name")
                    ln_el = author.find("last_name")
                    author_fn = fn_el.text if fn_el is not None else ""
                    author_ln = ln_el.text if ln_el is not None else ""

                price_el = book.find("price")
                price = ""
                price_currency = ""
                if price_el is not None:
                    price = price_el.text or ""
                    price_currency = price_el.get("currency", "")

                books_rows.append({
                    "store_name": store_name,
                    "store_city": store_city,
                    "category_name": cat_name,
                    "book_id": book_id,
                    "title": title,
                    "author_first_name": author_fn,
                    "author_last_name": author_ln,
                    "price": price,
                    "price_currency": price_currency,
                })

                tags_el = book.find("tags")
                if tags_el is not None:
                    for tag in tags_el.findall("tag"):
                        tags_rows.append({
                            "book_id": book_id,
                            "tag": tag.text or "",
                        })

                reviews_el = book.find("reviews")
                if reviews_el is not None:
                    for review in reviews_el.findall("review"):
                        reviews_rows.append({
                            "book_id": book_id,
                            "review_user": review.get("user", ""),
                            "review_rating": review.get("rating", ""),
                            "review_text": review.text or "",
                        })

    result = {}

    df_books = pd.DataFrame(books_rows, columns=BOOK_COLUMNS)
    result["books"] = df_books
    save_dataframe(df_books, str(Path(output_dir) / "xml_books.csv"))
    log.info("Flattened %d books", len(df_books))

    df_tags = pd.DataFrame(tags_rows, columns=BOOK_TAG_COLUMNS)
    result["book_tags"] = df_tags
    save_dataframe(df_tags, str(Path(output_dir) / "xml_book_tags.csv"))
    log.info("Flattened %d book-tag pairs", len(df_tags))

    df_reviews = pd.DataFrame(reviews_rows, columns=BOOK_REVIEW_COLUMNS)
    result["book_reviews"] = df_reviews
    save_dataframe(df_reviews, str(Path(output_dir) / "xml_book_reviews.csv"))
    log.info("Flattened %d book reviews", len(df_reviews))

    return result
