from pathlib import Path
import json

import pandas as pd
import re
import ast

def normalize_text(text):
    text = text.lower() # lowercase
    text = re.sub(r"[^\w\s]", " ", text) # replace punctuation symbols with " "
    text = re.sub(r"\s+", " ", text) # remove any trailing whitespaces
    return text

def normalize_ner_list(ner_list): # normalize an ner list
    normed = []
    for ner in ner_list:
        ner = ner.strip()
        if ner: # if can get words
            normed.append(normalize_text(ner)) # append it
    return normed

def main():    
    df = pd.read_csv("data/recipes_data.csv")
    # print("csv read") # debug    
    df = df.sample(frac=0.25, random_state=42).reset_index(drop=True)
    # print("df 1/4 sampled")
    
    df["NER_norm"] = df["NER"].apply(ast.literal_eval).apply(normalize_ner_list) # normalize NER (turn NERs into list of strings)
    # print("NER normalized") # debug
    df["doc_text"] = df["NER_norm"].apply(lambda x : " ".join(x)) # join for tokenizing
    # print("joined for tokenizing") # debug
    df["tokens"] = df["doc_text"].apply(lambda x : x.split()) # tokenize
    # print("tokenized") # debug

    records = df.to_dict(orient="records") # records for proper dictionary formatting    
    with open("data/BM25_data.jsonl", "w", encoding="utf-8") as bm25_f: # create preprocessed, normalized file
        # print("file opened and writing") # debug
        for record in records:
            bm25_f.write(json.dumps(record) + "\n") 

if __name__ == "__main__":
    main()