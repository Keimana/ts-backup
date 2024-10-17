import nltk
import heapq
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.probability import FreqDist
from rouge import Rouge
from bert_score import score
import torch
from transformers import BertTokenizer, BertModel 

class NewAlgorithmProcessor:
    def __init__(self):
        self.fileContent = ""  # This will store the title
        self.bodyContent = ""  # This will store the body of the article
        self.memo = {}  # Memoization table to store sentence scores
        self.word_freq_cache = {}  # Cache for word frequencies
        self.generated_summary = ""  # Initialize generated summary attribute
        self.original_text = ''  # Initialize original_text
        self.generated_summary = ''  # Initialize generated_summary
        self.rouge = Rouge()  # Initialize Rouge instance for ROUGE score calculation
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # Use the BERT tokenizer
        self.model = BertModel.from_pretrained('bert-base-uncased')  # Use the BERT model

    def set_content(self, content):
        """Sets the content by extracting the title and body separately."""
        lines = content.splitlines()
        if lines:
            self.fileContent = lines[0].strip()  # First line is the title
            self.bodyContent = ' '.join(lines[1:]).strip()  # The rest is the body
        else:
            self.fileContent = ""
            self.bodyContent = ""
        self.memo = {}  # Reset memoization table
        self.word_freq_cache = {}  # Reset word frequency cache

    def get_title(self):
        """Returns the title of the current content."""
        return self.fileContent

    def get_body(self):
        """Returns the body of the current content."""
        return self.bodyContent

    def tokenize_sentences(self, text):
        """Tokenizes text into sentences using NLTK's sent_tokenize."""
        return sent_tokenize(text)

    def tokenize_words(self, text):
        """Tokenizes text into words using NLTK's word_tokenize."""
        return word_tokenize(text.lower())

    def normalize_text(self, text):
        """Normalize the text by removing unnecessary elements."""
        text = re.sub(r'\n+', ' ', text)  # Replace newlines with spaces
        text = re.sub(r'\d+', '', text)  # Remove numbers
        text = re.sub(r'[\u2022•-]', '', text)  # Remove bullet points
        return text.strip()

    def get_word_frequencies(self):
        """Calculates word frequencies and caches the result."""
        if not self.word_freq_cache:  # If cache is empty, calculate frequencies
            words = self.tokenize_words(self.bodyContent)
            freq_dist = FreqDist(words)
            max_frequency = max(freq_dist.values(), default=1)
            self.word_freq_cache = {word: freq / max_frequency for word, freq in freq_dist.items()}
        return self.word_freq_cache

    def get_sentence_score(self, sentence, freq_dist):
        """Returns the score of a sentence based on word frequency, using memoization."""
        if sentence in self.memo:
            return self.memo[sentence]
        
        words = self.tokenize_words(sentence)
        score = sum(freq_dist.get(word, 0) for word in words)
        self.memo[sentence] = score
        return score

    def segment_text_into_chunks(self, text, chunk_size):
        """Segments text into manageable chunks."""
        sentences = self.tokenize_sentences(text)
        chunks = []
        current_chunk = []

        for sentence in sentences:
            current_chunk.append(sentence)
            if sum(len(s) for s in current_chunk) > chunk_size:
                chunks.append(' '.join(current_chunk[:-1]))  # Add all but the last sentence
                current_chunk = [current_chunk[-1]]  # Start new chunk with the last sentence

        if current_chunk:  # Add remaining sentences as the last chunk
            chunks.append(' '.join(current_chunk))
        return chunks

    def generate_summary(self, num_sentences=3, chunk_size=1000):
        """Generates a summary by selecting the top sentences based on their scores."""
        if not self.bodyContent:
            return "No content available to summarize."

        normalized_body = self.normalize_text(self.bodyContent)
        chunks = self.segment_text_into_chunks(normalized_body, chunk_size)

        summaries = []

        for chunk in chunks:
            sentences = self.tokenize_sentences(chunk)  # Summarize each chunk
            freq_dist = self.get_word_frequencies()

            # Score all sentences
            sentence_scores = {sentence: self.get_sentence_score(sentence, freq_dist) for sentence in sentences}

            # Pruning: Discard sentences with low scores compared to the best-known score
            best_known_score = max(sentence_scores.values(), default=0)
            filtered_sentences = {s: score for s, score in sentence_scores.items() if score >= best_known_score * 0.5}

            # Get the top N sentences based on their scores
            top_sentences = heapq.nlargest(num_sentences, filtered_sentences, key=filtered_sentences.get)
            summaries.append(' '.join(top_sentences))

        final_summary = ' '.join(summaries)
        self.generated_summary = self.format_summary(final_summary)  # Store the summary
        return self.generated_summary  # Return the generated summary
    
    def format_summary(self, summary):
        """Formats the summary by removing unnecessary elements."""
        formatted_summary = []
        lines = summary.splitlines()
        
        for line in lines:
            line = line.strip()  # Remove leading and trailing spaces
            # Skip empty lines
            if line:
                formatted_summary.append(line)
        
        return "\n".join(formatted_summary)

    def set_original_text(self, original_text):
        """Set the original text for ROUGE score calculation."""
        self.original_text = original_text
    
    def get_rouge_scores(self, decimal_places=3):
        """Calculates and returns the ROUGE scores between the generated summary and the original text."""
        if not self.original_text:
            raise ValueError("Original text is empty. Please set the original text before calculating ROUGE scores.")

        # Calculate ROUGE scores
        scores = self.rouge.get_scores(self.generated_summary, self.original_text)

        # Round the scores to the specified number of decimal places
        for score in scores:
            for metric, values in score.items():
                values['p'] = round(values['p'], decimal_places)  # Precision
                values['r'] = round(values['r'], decimal_places)  # Recall
                values['f'] = round(values['f'], decimal_places)  # F1 score

        return scores
    


    def calculate_bertscore(self, generated_summary, reference_summary):
        # Use the BERTScore library to compute the score
        P, R, F1 = score([generated_summary], [reference_summary], lang='en', verbose=True)
        return {
            'precision': P.mean().item(),
            'recall': R.mean().item(),
            'f1': F1.mean().item()
        }
        
    def get_embedding(self, text):
        inputs = self.tokenizer(text, return_tensors='pt', truncation=True, padding=True)
        with torch.no_grad():
            outputs = self.model(**inputs)
        return outputs.last_hidden_state.mean(dim=1).squeeze()

    def semantic_correlation(self, original_text, summary):
        original_embedding = self.get_embedding(original_text)
        summary_embedding = self.get_embedding(summary)
        cos_sim = torch.nn.functional.cosine_similarity(original_embedding, summary_embedding, dim=0)
        return cos_sim.item()

    def compression_ratio(self, original_text, summary):
        return len(summary) / len(original_text)

    def compute_reference_free_score(self):
        if self.original_text and self.generated_summary:
            sem_corr = self.semantic_correlation(self.original_text, self.generated_summary)
            comp_ratio = self.compression_ratio(self.original_text, self.generated_summary)
            # Combine the metrics, you can adjust the weights as needed
            alpha = 0.5
            final_score = (sem_corr ** alpha) * (comp_ratio ** (1 - alpha))
            return final_score
        return None