# MagniFood 

## Environment Setup
Create a Python virtual environment through `python -m venv venv`, then activate the environment through `source venv/bin/activate` if on macOS or Linux (or `venv\Scripts\activate` if on Windows).  
After activating your Python environment, run `pip install -r requirements.txt`. This will install all the relevant dependencies used in this project such as `food2vec` for Vector Search's embeddings and `rank_bm25` for BM25's processing.

## Project Description
MagniFood is a ingredient-recipe matching project. It uses Okapi BM25 and Vector Search to rank ingredients, then processes those ranks through RRF (Reciprocal Rank Fusion) to produce proper search results.

The BM25 component implements the Okapi BM25 algorithm to rank recipes based on term frequency, inverse document frequency, and document length normalization. Recipe data is preprocessed (normalized and tokenized) in `BM25Preprocess.py` into a jsonl file which `BM25Search.py` uses to rank and process recipes according to the user's query. A limiter for the amount of recipes is set to allow for quicker processing of the recipes.

The Embedding powered components uses cosine similarity to rank recipes. All recipes are embedded into vectors using a semantic embedding model which we access through the Food2Vec API. When a query comes in, it is embedded into the same space and recipes are ranked based on similarity within that vector space.
