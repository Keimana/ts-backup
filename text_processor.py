import re
from collections import Counter
from rouge import Rouge
from bert_score import score
import torch
from transformers import BertTokenizer, BertModel  # Import the tokenizer and model


class TextProcessor:
    def __init__(self):
        self.fileContent = ''
        self.memo = {}  # Memoization table to store sentence scores
        self.title = ''  # Title attribute
        self.character_list = []  # List to store characters found
        self.original_text = ''  # Initialize original_text
        self.generated_summary = ''  # Initialize generated_summary
        self.rouge = Rouge()  # Initialize Rouge instance for ROUGE score calculation
        self.tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')  # Use the BERT tokenizer
        self.model = BertModel.from_pretrained('bert-base-uncased')  # Use the BERT model

    def set_content(self, content, title=''):
        """Sets the content of the text processor and optionally a title."""
        self.fileContent = content
        self.memo = {}  # Reset memoization table
        self.title = title  # Set the title
        self.character_list = self.extract_characters()  # Extract characters and update the list
        self.set_original_text(content)  # Set original text for ROUGE calculation

    def get_content(self):
        """Returns the current content of the text processor."""
        return self.fileContent

    def extract_characters(self):
        """Extracts character names from the file content."""
        characters = re.findall(r'\b[A-Z][a-z]*\b', self.fileContent)
        return list(set(characters))  # Remove duplicates

    def get_characters(self):
        """Returns the list of extracted characters.""" 
        return self.character_list

    def tokenize_sentences(self, text):
        """Splits text into sentences using regular expressions."""
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\!|\?)\s', text)
        return [sentence.strip() for sentence in sentences if sentence.strip()]

    def tokenize_words(self, text):
        """Splits text into words using regular expressions.""" 
        return re.findall(r'\w+', text.lower())

    def get_word_frequencies(self):
        """Calculates word frequencies and normalizes them."""
        words = self.tokenize_words(self.fileContent)
        word_frequencies = Counter(words)
        max_frequency = max(word_frequencies.values(), default=1)
        return {word: freq / max_frequency for word, freq in word_frequencies.items()}

    def get_sentence_score(self, sentence, freq_dist):
        """Returns the score of a sentence based on word frequency, using memoization.""" 
        if sentence in self.memo:
            return self.memo[sentence]
        
        words = self.tokenize_words(sentence)
        score = sum(freq_dist.get(word, 0) for word in words)
        self.memo[sentence] = score
        return score

    def generate_summary(self):
        """Generates a summary by selecting sentences based on their scores.""" 
        if not self.fileContent:
            return "No content available to summarize."
        
        sentences = self.tokenize_sentences(self.fileContent)
        freq_dist = self.get_word_frequencies()

        # Score all sentences and sort them
        sentence_scores = {sentence: self.get_sentence_score(sentence, freq_dist) for sentence in sentences}
        summarized_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)

        # Limit the summary to a specific number of sentences if needed (e.g., top 3)
        top_n_sentences = 3
        self.generated_summary = ' '.join(summarized_sentences[:top_n_sentences])  # Store the generated summary
        return self.generated_summary

    def display_memo(self):
        """Displays the memoization table containing sentence scores.""" 
        return self.memo

    def word_count(self):
        """Calculates and returns the word count of the file content.""" 
        return len(self.tokenize_words(self.fileContent))

    def summarized_word_count(self):
        """Calculates and returns the word count of the summarized content.""" 
        summary = self.generate_summary()
        return len(self.tokenize_words(summary))

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

    def get_reference_summary(self):
        """Returns the original text as the reference summary.""" 
        return self.original_text

    def print_reference_summary(self):
        """Prints the reference summary (original text)."""
        if self.original_text:
            print("Reference Summary:")
            print(self.original_text)
        else:
            print("No original text available.")
            
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