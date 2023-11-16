import os
from typing import Optional

from rank_bm25 import BM25Okapi


TEXT_DIR = "gutenberg/data/text"
CORPUS_SIZE = 100
SCORE_DIFF_THRESHOLD = 0.02


class BM25Scorer:

    def __init__(self):
        self.corpus = []  # todo: add metadata
        for txt in os.listdir(TEXT_DIR)[:CORPUS_SIZE]:
            if txt.endswith(".txt"):
                with open(os.path.join(TEXT_DIR, txt)) as f:
                    doc = f.read().lower()
                    self.corpus.append(doc)
        tokenized_corpus = [doc.split(" ") for doc in self.corpus]
        self.bm25 = BM25Okapi(tokenized_corpus)

    def find_suspected_source_of_response(self, text_to_check: str) -> Optional[str]:
        """
        Function for performing a BM25 search of the LLM response over our corpus.
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
            return self.corpus[top_doc_idx]

        # Else return None
        return None


if __name__ == '__main__':
    pass
