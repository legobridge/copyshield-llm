import pickle
from dataclasses import dataclass
from typing import Optional
from pathlib import Path

import pandas as pd
from rank_bm25 import BM25Okapi

DATA_DIR = Path("data/")
TEXT_DIR = DATA_DIR / "text"
METADATA_PATH = DATA_DIR / "metadata.csv"
CORPUS_PICKLE_PATH = DATA_DIR / "corpus_pickle.pkl"
BM25_PICKLE_PATH = DATA_DIR / "bm25_pickle.pkl"
CORPUS_SIZE = 10000
DOCUMENT_SIZE = 5000
SCORE_DIFF_THRESHOLD = 0.15


@dataclass
class DocumentMetadata:
    title: str
    author: str
    segment: int


class BM25Scorer:

    def __init__(self):
        if CORPUS_PICKLE_PATH.exists():
            with open(CORPUS_PICKLE_PATH, 'rb') as f:
                self.corpus_metadata = pickle.load(f)
            with open(BM25_PICKLE_PATH, 'rb') as f:
                self.bm25 = pickle.load(f)
            if len(self.corpus_metadata) == CORPUS_SIZE:
                return
        # If pickle doesn't exist, or is the wrong size, regenerate it
        metadata_df = pd.read_csv(METADATA_PATH)
        self.corpus_metadata = []
        tokenized_corpus = []
        for _, row in metadata_df.iterrows():
            doc_id = row['id']
            doc_path = TEXT_DIR / f"{doc_id}_text.txt"
            if doc_path.exists():
                title = row['title']
                author = row['author']
                with open(doc_path) as f:
                    text = f.read()
                tokenized_text = text.split()
                segment_id = 0
                while segment_id * DOCUMENT_SIZE < len(tokenized_text):
                    start = segment_id * DOCUMENT_SIZE
                    end = min(len(tokenized_text), (segment_id + 1) * DOCUMENT_SIZE)
                    tokenized_corpus.append(tokenized_text[start:end])
                    self.corpus_metadata.append(DocumentMetadata(title, author, segment_id))
                    segment_id += 1
                    if len(self.corpus_metadata) == CORPUS_SIZE:
                        break
                if len(self.corpus_metadata) == CORPUS_SIZE:
                    break
        self.bm25 = BM25Okapi(tokenized_corpus)
        with open(CORPUS_PICKLE_PATH, 'wb') as f:
            pickle.dump(self.corpus_metadata, f)
        with open(BM25_PICKLE_PATH, 'wb') as f:
            pickle.dump(self.bm25, f)

    def find_suspected_source_of_response(self, text_to_check: str) -> Optional[DocumentMetadata]:
        """
        Function for performing a BM25 search of the LLM response over our corpus
        :param text_to_check: the text to check for infringement
        :return: the name of a source document if a significant match is found, None if not confident about the match.
        """
        # Score corpus documents against text
        tokenized_text = text_to_check.split(" ")
        doc_scores = self.bm25.get_scores(tokenized_text)

        # Find the normalized score difference between the top two documents
        top_doc_idx = doc_scores.argmax()
        score_diff_in_first_second_result = 1.0
        for i in range(len(doc_scores)):
            if i != top_doc_idx:
                normalized_score = doc_scores[i] / doc_scores[top_doc_idx]
                score_diff_in_first_second_result = min(score_diff_in_first_second_result, 1 - normalized_score)
        print(score_diff_in_first_second_result)

        # If the difference is large enough, return the details of the top document
        if score_diff_in_first_second_result > SCORE_DIFF_THRESHOLD:
            return self.corpus_metadata[top_doc_idx]

        # Else return None
        return None


if __name__ == '__main__':
    pass
