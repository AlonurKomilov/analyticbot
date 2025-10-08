"""
Content Data Processor
=====================

Text preprocessing and feature extraction for content analysis.
Handles tokenization, encoding, and feature engineering for text content.
"""

import logging
import re
import string
from collections import Counter
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch.nn.utils.rnn import pad_sequence

logger = logging.getLogger(__name__)


class ContentDataProcessor:
    """Specialized data processor for content analysis features"""

    def __init__(
        self,
        vocab_size: int = 10000,
        max_seq_length: int = 512,
        min_word_freq: int = 2,
        special_tokens: dict[str, int] | None = None,
        enable_preprocessing: bool = True,
        lowercase: bool = True,
    ):
        self.vocab_size = vocab_size
        self.max_seq_length = max_seq_length
        self.min_word_freq = min_word_freq
        self.enable_preprocessing = enable_preprocessing
        self.lowercase = lowercase

        # Special tokens
        self.special_tokens = special_tokens or {"<PAD>": 0, "<UNK>": 1, "<START>": 2, "<END>": 3}

        # Vocabulary mappings
        self.word_to_idx: dict[str, int] = {}
        self.idx_to_word: dict[int, str] = {}
        self.word_counts: Counter = Counter()

        # Content features
        self.content_features = [
            "text_length",
            "word_count",
            "unique_words",
            "avg_word_length",
            "punctuation_ratio",
            "uppercase_ratio",
            "question_count",
            "exclamation_count",
        ]

        self.is_fitted = False

        # Initialize with special tokens
        self._initialize_vocabulary()

        logger.info(f"📝 Content Data Processor initialized with vocab_size={vocab_size}")

    def _initialize_vocabulary(self):
        """Initialize vocabulary with special tokens"""
        for token, idx in self.special_tokens.items():
            self.word_to_idx[token] = idx
            self.idx_to_word[idx] = token

    def preprocess_text(self, text: str) -> str:
        """Preprocess text content

        Args:
            text: Raw text input

        Returns:
            Preprocessed text
        """
        if not self.enable_preprocessing:
            return text

        # Basic cleaning
        text = str(text) if text is not None else ""

        # Remove extra whitespace
        text = re.sub(r"\s+", " ", text)

        # Normalize common patterns
        text = re.sub(
            r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
            "<URL>",
            text,
        )
        text = re.sub(r"@\w+", "<MENTION>", text)
        text = re.sub(r"#\w+", "<HASHTAG>", text)
        text = re.sub(r"\d+", "<NUMBER>", text)

        # Lowercase if enabled
        if self.lowercase:
            text = text.lower()

        # Strip leading/trailing whitespace
        text = text.strip()

        return text

    def tokenize_text(self, text: str) -> list[str]:
        """Tokenize text into words

        Args:
            text: Input text

        Returns:
            List of tokens
        """
        # Preprocess first
        text = self.preprocess_text(text)

        # Simple word tokenization (can be enhanced with proper tokenizers)
        # Keep punctuation as separate tokens
        tokens = []

        # Split on whitespace and punctuation
        words = re.findall(r"\w+|[^\w\s]", text)

        for word in words:
            if word.strip():  # Skip empty tokens
                tokens.append(word)

        return tokens

    def build_vocabulary(self, texts: list[str]) -> dict[str, Any]:
        """Build vocabulary from training texts

        Args:
            texts: List of training texts

        Returns:
            Vocabulary statistics
        """
        logger.info(f"🔤 Building vocabulary from {len(texts)} texts...")

        # Count words
        word_counts = Counter()
        total_tokens = 0

        for text in texts:
            tokens = self.tokenize_text(text)
            word_counts.update(tokens)
            total_tokens += len(tokens)

        # Filter by frequency and build vocabulary
        vocab_words = []
        for word, count in word_counts.most_common():
            if count >= self.min_word_freq and len(vocab_words) < (
                self.vocab_size - len(self.special_tokens)
            ):
                vocab_words.append(word)

        # Build mappings
        current_idx = len(self.special_tokens)
        for word in vocab_words:
            if word not in self.word_to_idx:
                self.word_to_idx[word] = current_idx
                self.idx_to_word[current_idx] = word
                current_idx += 1

        self.word_counts = word_counts
        self.is_fitted = True

        vocab_stats = {
            "total_words": len(word_counts),
            "unique_words": len(vocab_words),
            "vocab_size": len(self.word_to_idx),
            "total_tokens": total_tokens,
            "coverage": len(vocab_words) / len(word_counts) if len(word_counts) > 0 else 0,
            "min_freq": self.min_word_freq,
        }

        logger.info(
            f"✅ Vocabulary built: {vocab_stats['vocab_size']} words, {vocab_stats['coverage']:.2%} coverage"
        )
        return vocab_stats

    def encode_text(self, text: str, add_special_tokens: bool = True) -> list[int]:
        """Encode text to token IDs

        Args:
            text: Input text
            add_special_tokens: Whether to add START/END tokens

        Returns:
            List of token IDs
        """
        if not self.is_fitted:
            raise ValueError("Processor must be fitted before encoding")

        tokens = self.tokenize_text(text)

        # Convert to IDs
        token_ids = []

        if add_special_tokens:
            token_ids.append(self.special_tokens["<START>"])

        for token in tokens:
            if token in self.word_to_idx:
                token_ids.append(self.word_to_idx[token])
            else:
                token_ids.append(self.special_tokens["<UNK>"])

        if add_special_tokens:
            token_ids.append(self.special_tokens["<END>"])

        # Truncate if too long
        if len(token_ids) > self.max_seq_length:
            token_ids = token_ids[: self.max_seq_length - 1] + [self.special_tokens["<END>"]]

        return token_ids

    def decode_ids(self, token_ids: list[int], skip_special: bool = True) -> str:
        """Decode token IDs back to text

        Args:
            token_ids: List of token IDs
            skip_special: Whether to skip special tokens

        Returns:
            Decoded text
        """
        tokens = []
        special_values = set(self.special_tokens.values())

        for token_id in token_ids:
            if skip_special and token_id in special_values:
                continue

            if token_id in self.idx_to_word:
                tokens.append(self.idx_to_word[token_id])
            else:
                tokens.append("<UNK>")

        return " ".join(tokens)

    def extract_content_features(self, text: str) -> np.ndarray:
        """Extract statistical features from text content

        Args:
            text: Input text

        Returns:
            Feature vector
        """
        if not text or pd.isna(text):
            return np.zeros(len(self.content_features))

        text = str(text)
        tokens = self.tokenize_text(text)

        # Calculate features
        features = []

        # Text length
        features.append(len(text))

        # Word count
        word_tokens = [t for t in tokens if t.isalnum()]
        features.append(len(word_tokens))

        # Unique words
        features.append(len(set(word_tokens)))

        # Average word length
        if word_tokens:
            avg_word_len = sum(len(word) for word in word_tokens) / len(word_tokens)
        else:
            avg_word_len = 0
        features.append(avg_word_len)

        # Punctuation ratio
        punct_count = sum(1 for char in text if char in string.punctuation)
        punct_ratio = punct_count / len(text) if len(text) > 0 else 0
        features.append(punct_ratio)

        # Uppercase ratio
        upper_count = sum(1 for char in text if char.isupper())
        upper_ratio = upper_count / len(text) if len(text) > 0 else 0
        features.append(upper_ratio)

        # Question count
        question_count = text.count("?")
        features.append(question_count)

        # Exclamation count
        exclamation_count = text.count("!")
        features.append(exclamation_count)

        return np.array(features, dtype=np.float32)

    def process_batch(
        self, texts: list[str], labels: dict[str, list[Any]] | None = None
    ) -> dict[str, torch.Tensor]:
        """Process a batch of texts for model input

        Args:
            texts: List of input texts
            labels: Optional dictionary of labels for each task

        Returns:
            Dictionary with processed tensors
        """
        if not self.is_fitted:
            raise ValueError("Processor must be fitted before processing")

        # Encode texts
        encoded_texts = [self.encode_text(text) for text in texts]

        # Convert to tensors and pad
        input_ids = [torch.tensor(ids, dtype=torch.long) for ids in encoded_texts]
        input_ids = pad_sequence(
            input_ids, batch_first=True, padding_value=self.special_tokens["<PAD>"]
        )

        # Create attention mask
        attention_mask = (input_ids != self.special_tokens["<PAD>"]).long()

        # Extract content features
        content_features = np.array([self.extract_content_features(text) for text in texts])
        content_features = torch.tensor(content_features, dtype=torch.float32)

        batch_dict = {
            "input_ids": input_ids,
            "attention_mask": attention_mask,
            "content_features": content_features,
            "original_texts": texts,
        }

        # Add labels if provided
        if labels:
            for task_name, task_labels in labels.items():
                batch_dict[f"{task_name}_labels"] = torch.tensor(task_labels, dtype=torch.long)

        return batch_dict

    def analyze_text_complexity(self, text: str) -> dict[str, float]:
        """Analyze text complexity metrics

        Args:
            text: Input text

        Returns:
            Dictionary with complexity metrics
        """
        if not text or pd.isna(text):
            return {
                metric: 0.0 for metric in ["readability", "complexity", "diversity", "formality"]
            }

        tokens = self.tokenize_text(text)
        words = [t for t in tokens if t.isalnum()]

        # Simple readability (average sentence length)
        sentences = text.split(".")
        avg_sentence_length = len(words) / len(sentences) if sentences else 0
        readability = min(avg_sentence_length / 20, 1.0)  # Normalize

        # Lexical diversity (unique words / total words)
        diversity = len(set(words)) / len(words) if words else 0

        # Complexity (average word length)
        avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
        complexity = min(avg_word_length / 10, 1.0)  # Normalize

        # Formality (ratio of long words)
        long_words = sum(1 for word in words if len(word) > 6)
        formality = long_words / len(words) if words else 0

        return {
            "readability": readability,
            "complexity": complexity,
            "diversity": diversity,
            "formality": formality,
        }

    def get_vocabulary_info(self) -> dict[str, Any]:
        """Get vocabulary information and statistics

        Returns:
            Dictionary with vocabulary info
        """
        if not self.is_fitted:
            return {"fitted": False}

        # Most common words (excluding special tokens)
        common_words = []
        special_values = set(self.special_tokens.values())

        for word, count in self.word_counts.most_common(20):
            if word in self.word_to_idx and self.word_to_idx[word] not in special_values:
                common_words.append((word, count))

        return {
            "fitted": True,
            "vocab_size": len(self.word_to_idx),
            "special_tokens": self.special_tokens,
            "most_common_words": common_words[:10],
            "total_word_count": sum(self.word_counts.values()),
            "unique_words": len(self.word_counts),
            "max_seq_length": self.max_seq_length,
        }

    def validate_inputs(self, texts: list[str]) -> dict[str, Any]:
        """Validate input texts

        Args:
            texts: List of input texts

        Returns:
            Validation report
        """
        report = {
            "valid": True,
            "issues": [],
            "recommendations": [],
            "stats": {
                "total_texts": len(texts),
                "empty_texts": 0,
                "too_long": 0,
                "avg_length": 0,
                "vocab_coverage": 0,
            },
        }

        if not texts:
            report["valid"] = False
            report["issues"].append("No texts provided")
            return report

        lengths = []
        empty_count = 0
        too_long_count = 0
        unknown_token_counts = []

        for text in texts:
            if not text or pd.isna(text) or str(text).strip() == "":
                empty_count += 1
                continue

            text_str = str(text)
            lengths.append(len(text_str))

            # Check if too long
            tokens = self.tokenize_text(text_str)
            if len(tokens) > self.max_seq_length:
                too_long_count += 1

            # Check vocabulary coverage if fitted
            if self.is_fitted:
                unknown_count = sum(1 for token in tokens if token not in self.word_to_idx)
                unknown_token_counts.append(unknown_count / len(tokens) if tokens else 0)

        # Update stats
        report["stats"]["empty_texts"] = empty_count
        report["stats"]["too_long"] = too_long_count
        report["stats"]["avg_length"] = np.mean(lengths) if lengths else 0

        if self.is_fitted and unknown_token_counts:
            report["stats"]["vocab_coverage"] = 1 - np.mean(unknown_token_counts)

        # Add issues and recommendations
        if empty_count > 0:
            report["issues"].append(f"{empty_count} empty texts found")
            report["recommendations"].append("Remove or replace empty texts")

        if too_long_count > 0:
            report["issues"].append(f"{too_long_count} texts exceed max length")
            report["recommendations"].append(
                f"Texts will be truncated to {self.max_seq_length} tokens"
            )

        if self.is_fitted and unknown_token_counts and np.mean(unknown_token_counts) > 0.3:
            report["issues"].append("High percentage of unknown tokens")
            report["recommendations"].append("Consider expanding vocabulary or preprocessing")

        return report

    def get_processor_stats(self) -> dict[str, Any]:
        """Get processor statistics and configuration

        Returns:
            Dictionary with processor information
        """
        return {
            "vocab_size": self.vocab_size,
            "max_seq_length": self.max_seq_length,
            "min_word_freq": self.min_word_freq,
            "preprocessing_enabled": self.enable_preprocessing,
            "lowercase": self.lowercase,
            "is_fitted": self.is_fitted,
            "feature_count": len(self.content_features),
            "special_tokens": self.special_tokens,
            "vocabulary_info": self.get_vocabulary_info(),
        }
