"""
Implements Statistical Semantic Chunking of legal documents
"""

import nltk
import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import logging

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ensure NLTK 'punkt' tokenizer is available
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    logger.info("NLTK 'punkt' tokenizer not found. Downloading...")
    nltk.download('punkt', quiet=True)


class StatisticalSemanticChunker:
    """
    A class to perform statistical semantic chunking on documents.
    It breaks down a document into coherent blocks of text based on
    semantic similarity between adjacent sentences. The threshold for
    splitting is determined statistically from the document's own
    similarity scores.
    """

    def __init__(self, model_name: str = 'all-MiniLM-L6-v2', threshold_factor: float = 1.0, min_chunk_sentences: int = 1):
        """
        Initializes the StatisticalSemanticChunker.

        Args:
            model_name (str): The name of the sentence-transformer model to use
                              (e.g., 'all-MiniLM-L6-v2', 'paraphrase-mpnet-base-v2').
            threshold_factor (float): A factor to determine the similarity threshold.
                                      The threshold is calculated as:
                                      mean_similarity - (threshold_factor * std_dev_similarity).
                                      A higher factor leads to fewer, larger chunks (as the threshold becomes lower).
                                      A lower factor (or negative) leads to more, smaller chunks.
            min_chunk_sentences (int): The minimum number of sentences a chunk should ideally have
                                       before a split is considered. This helps prevent overly granular chunks.
                                       The last chunk in a document might be smaller.
        """
        try:
            self.model = SentenceTransformer(model_name)
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model '{model_name}': {e}")
            raise
        self.threshold_factor = threshold_factor
        self.min_chunk_sentences = max(1, min_chunk_sentences)  # Ensure at least 1
        logger.info(f"StatisticalSemanticChunker initialized with model: {model_name}, threshold_factor: {threshold_factor}, min_chunk_sentences: {self.min_chunk_sentences}")

    def _tokenize_sentences(self, text: str) -> list[str]:
        """
        Tokenizes the input text into sentences.

        Args:
            text (str): The document text.

        Returns:
            list[str]: A list of sentences, stripped of leading/trailing whitespace.
                       Returns an empty list if the input text is empty or whitespace only.
        """
        if not text or not text.strip():
            return []
        sentences = nltk.sent_tokenize(text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_document(self, text: str) -> list[str]:
        """
        Chunks the document based on statistical semantic similarity.

        Args:
            text (str): The document text to be chunked.

        Returns:
            list[str]: A list of text chunks. Each chunk is a string containing one or more sentences.
                       Returns an empty list if no sentences are found or an error occurs.
        """
        sentences = self._tokenize_sentences(text)

        if not sentences:
            logger.warning("No sentences found in the document.")
            return []

        # If the number of sentences is very small, return the whole text as one chunk.
        if len(sentences) <= self.min_chunk_sentences : # A single sentence or fewer than min_chunk_sentences
            logger.info(f"Document has {len(sentences)} sentence(s), which is less than or equal to "
                        f"min_chunk_sentences ({self.min_chunk_sentences}) or too few to split meaningfully. "
                        f"Returning as a single chunk.")
            return [" ".join(sentences)]

        # Generate embeddings for all sentences
        try:
            embeddings = self.model.encode(sentences, show_progress_bar=False)
        except Exception as e:
            logger.error(f"Error encoding sentences: {e}. Returning document as a single chunk.")
            return [" ".join(sentences)] # Fallback to single chunk

        # Ensure embeddings is 2D
        if embeddings.ndim == 1:
            embeddings = embeddings.reshape(1, -1)
        
        if len(embeddings) < 2: # Should be caught by len(sentences) check, but as a safeguard
            logger.info("Not enough embeddings to calculate similarities. Returning as a single chunk.")
            return [" ".join(sentences)]

        # Calculate cosine similarity between adjacent sentences (S_i vs S_{i+1})
        similarities = []
        for i in range(len(embeddings) - 1):
            sim = cosine_similarity(embeddings[i].reshape(1, -1), embeddings[i+1].reshape(1, -1))[0, 0]
            similarities.append(sim)

        if not similarities: # Only one sentence pair resulted in no similarities (e.g. len(embeddings) was 1)
            logger.info("No similarity scores calculated (e.g., only one sentence after processing). Returning as a single chunk.")
            return [" ".join(sentences)]

        similarities_np = np.array(similarities)
        mean_similarity = np.mean(similarities_np)
        std_dev_similarity = np.std(similarities_np)

        # Determine the dynamic threshold
        # A lower similarity score indicates a potential boundary
        similarity_threshold = mean_similarity - (self.threshold_factor * std_dev_similarity)
        
        logger.info(f"Document sentences: {len(sentences)}. Similarity scores calculated: {len(similarities_np)}.")
        logger.info(f"Similarity stats: Mean={mean_similarity:.4f}, StdDev={std_dev_similarity:.4f}. Dynamic threshold={similarity_threshold:.4f}")

        chunks = []
        current_chunk_start_index = 0
        for i in range(len(sentences)):
            # Sentence `i` is the current sentence being considered.
            # The decision to end a chunk *after* sentence `i` depends on `similarities[i]`,
            # which is the similarity between `sentences[i]` and `sentences[i+1]`.
            
            is_last_sentence_in_doc = (i == len(sentences) - 1)
            
            split_after_this_sentence = False
            if is_last_sentence_in_doc:
                split_after_this_sentence = True
            else: # Not the last sentence, so similarities[i] is valid
                if similarities[i] < similarity_threshold:
                    # Potential split point. Check if current chunk (from current_chunk_start_index to i) is large enough.
                    current_chunk_length = i - current_chunk_start_index + 1
                    if current_chunk_length >= self.min_chunk_sentences:
                        split_after_this_sentence = True
                    # If not large enough, we don't split here; the sentence is added to the current chunk,
                    # and we continue, hoping a later split point allows this chunk to grow.

            if split_after_this_sentence:
                chunk_sentences = sentences[current_chunk_start_index : i + 1]
                chunks.append(" ".join(chunk_sentences))
                current_chunk_start_index = i + 1
        
        # This check ensures that if no chunks were formed (e.g. due to an unexpected issue, though unlikely with current logic),
        # the original text (or its sentences joined) is returned.
        if not chunks and sentences:
            logger.warning("Chunking logic resulted in no chunks despite having sentences. Returning document as a single chunk.")
            return [" ".join(sentences)]
            
        return chunks

# Example Usage (optional, can be removed or placed in a __main__ block)
# if __name__ == '__main__':
#     chunker = StatisticalSemanticChunker(threshold_factor=0.8, min_chunk_sentences=2)
#     sample_text = (
#         "Climate change is a significant global issue. It affects weather patterns worldwide. "
#         "Many countries are taking steps to reduce emissions. Renewable energy sources are becoming more popular. "
#         "Separately, economic policies also play a crucial role in national development. "
#         "Fiscal measures and trade agreements shape the future of economies. "
#         "Education systems are fundamental for societal progress. Investing in schools is key."
#     )
#     document_chunks = chunker.chunk_document(sample_text)
#     for idx, chunk_text in enumerate(document_chunks):
#         logger.info(f"--- Chunk {idx+1} ---")
#         logger.info(chunk_text)
