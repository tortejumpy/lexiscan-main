"""
TF-IDF based text classifier for entity classification
"""

import logging
import pickle
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, f1_score

logger = logging.getLogger(__name__)


class TFIDFClassifier:
    """
    TF-IDF based classifier for entity type classification
    """
    
    def __init__(
        self,
        max_features: int = 5000,
        ngram_range: Tuple[int, int] = (1, 3)
    ):
        """
        Initialize TF-IDF classifier
        
        Args:
            max_features: Maximum number of features
            ngram_range: N-gram range for TF-IDF
        """
        self.max_features = max_features
        self.ngram_range = ngram_range
        
        # Create pipeline
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(
                max_features=max_features,
                ngram_range=ngram_range,
                lowercase=True,
                stop_words='english'
            )),
            ('classifier', LogisticRegression(
                max_iter=1000,
                random_state=42,
                class_weight='balanced'
            ))
        ])
        
        self.is_trained = False
        logger.info(f"TFIDFClassifier initialized with max_features={max_features}, "
                   f"ngram_range={ngram_range}")
    
    def train(
        self,
        texts: List[str],
        labels: List[str],
        test_size: float = 0.2
    ) -> Dict[str, float]:
        """
        Train the classifier
        
        Args:
            texts: List of text samples
            labels: List of corresponding labels
            test_size: Proportion of test set
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Training TF-IDF classifier on {len(texts)} samples")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            texts, labels,
            test_size=test_size,
            random_state=42,
            stratify=labels
        )
        
        # Train pipeline
        self.pipeline.fit(X_train, y_train)
        self.is_trained = True
        
        # Evaluate
        y_pred = self.pipeline.predict(X_test)
        
        # Calculate metrics
        f1 = f1_score(y_test, y_pred, average='weighted')
        
        logger.info(f"Training completed. F1-score: {f1:.4f}")
        logger.info("\nClassification Report:\n" + 
                   classification_report(y_test, y_pred))
        
        return {
            'f1_score': f1,
            'train_size': len(X_train),
            'test_size': len(X_test)
        }
    
    def predict(self, texts: List[str]) -> List[str]:
        """
        Predict labels for texts
        
        Args:
            texts: List of text samples
            
        Returns:
            List of predicted labels
        """
        if not self.is_trained:
            raise ValueError("Classifier must be trained before prediction")
        
        predictions = self.pipeline.predict(texts)
        return predictions.tolist()
    
    def predict_proba(self, texts: List[str]) -> np.ndarray:
        """
        Predict probabilities for texts
        
        Args:
            texts: List of text samples
            
        Returns:
            Array of prediction probabilities
        """
        if not self.is_trained:
            raise ValueError("Classifier must be trained before prediction")
        
        probabilities = self.pipeline.predict_proba(texts)
        return probabilities
    
    def get_feature_importance(self, top_n: int = 20) -> Dict[str, List[Tuple[str, float]]]:
        """
        Get top features for each class
        
        Args:
            top_n: Number of top features to return
            
        Returns:
            Dictionary mapping class to top features
        """
        if not self.is_trained:
            raise ValueError("Classifier must be trained first")
        
        # Get feature names and coefficients
        feature_names = self.pipeline['tfidf'].get_feature_names_out()
        coefficients = self.pipeline['classifier'].coef_
        classes = self.pipeline['classifier'].classes_
        
        importance = {}
        
        for idx, class_name in enumerate(classes):
            # Get coefficients for this class
            class_coef = coefficients[idx]
            
            # Get top features
            top_indices = np.argsort(class_coef)[-top_n:][::-1]
            top_features = [
                (feature_names[i], class_coef[i])
                for i in top_indices
            ]
            
            importance[class_name] = top_features
        
        return importance
    
    def save(self, filepath: str) -> None:
        """
        Save trained model to file
        
        Args:
            filepath: Path to save model
        """
        if not self.is_trained:
            raise ValueError("Cannot save untrained model")
        
        filepath = Path(filepath)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(self.pipeline, f)
        
        logger.info(f"Model saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """
        Load trained model from file
        
        Args:
            filepath: Path to model file
        """
        with open(filepath, 'rb') as f:
            self.pipeline = pickle.load(f)
        
        self.is_trained = True
        logger.info(f"Model loaded from {filepath}")


class BaselineNERModel:
    """
    Baseline NER model combining TF-IDF and Regex
    """
    
    def __init__(self):
        """Initialize baseline model"""
        from .regex_extractor import RegexExtractor
        
        self.regex_extractor = RegexExtractor()
        self.tfidf_classifier = TFIDFClassifier()
        
        logger.info("BaselineNERModel initialized")
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract entities from text using baseline approach
        
        Args:
            text: Input text
            
        Returns:
            List of entity dictionaries
        """
        # Use regex extractor
        entities = self.regex_extractor.extract_all(text)
        
        # Convert to dictionary format
        entity_dicts = [
            {
                'text': e.text,
                'label': e.label,
                'start': e.start,
                'end': e.end,
                'confidence': e.confidence,
                'method': 'regex'
            }
            for e in entities
        ]
        
        return entity_dicts
    
    def get_summary(self, entities: List[Dict]) -> Dict[str, int]:
        """Get entity count summary"""
        summary = {}
        for entity in entities:
            label = entity['label']
            summary[label] = summary.get(label, 0) + 1
        return summary
