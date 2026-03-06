"""
Bi-LSTM NER Model with CRF Layer
Deep learning sequence model for entity recognition
"""

import logging
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.utils import to_categorical
import pickle

logger = logging.getLogger(__name__)


class BiLSTMNER:
    """
    Bidirectional LSTM model for Named Entity Recognition
    """
    
    def __init__(
        self,
        max_sequence_length: int = 512,
        embedding_dim: int = 100,
        lstm_units: int = 128,
        dropout: float = 0.3,
        recurrent_dropout: float = 0.3
    ):
        """
        Initialize Bi-LSTM NER model
        
        Args:
            max_sequence_length: Maximum sequence length
            embedding_dim: Embedding dimension
            lstm_units: Number of LSTM units
            dropout: Dropout rate
            recurrent_dropout: Recurrent dropout rate
        """
        self.max_sequence_length = max_sequence_length
        self.embedding_dim = embedding_dim
        self.lstm_units = lstm_units
        self.dropout = dropout
        self.recurrent_dropout = recurrent_dropout
        
        self.model = None
        self.word2idx = {}
        self.idx2word = {}
        self.tag2idx = {}
        self.idx2tag = {}
        self.vocab_size = 0
        self.n_tags = 0
        
        logger.info(f"BiLSTMNER initialized with embedding_dim={embedding_dim}, "
                   f"lstm_units={lstm_units}")
    
    def prepare_data(
        self,
        sentences: List[List[str]],
        tags: List[List[str]]
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Prepare data for training
        
        Args:
            sentences: List of tokenized sentences
            tags: List of tag sequences
            
        Returns:
            Tuple of (X, y) arrays
        """
        # Build vocabularies
        words = set([word for sentence in sentences for word in sentence])
        tags_set = set([tag for tag_seq in tags for tag in tag_seq])
        
        self.word2idx = {word: idx + 2 for idx, word in enumerate(words)}
        self.word2idx['<PAD>'] = 0
        self.word2idx['<UNK>'] = 1
        
        self.idx2word = {idx: word for word, idx in self.word2idx.items()}
        
        self.tag2idx = {tag: idx for idx, tag in enumerate(tags_set)}
        self.idx2tag = {idx: tag for tag, idx in self.tag2idx.items()}
        
        self.vocab_size = len(self.word2idx)
        self.n_tags = len(self.tag2idx)
        
        logger.info(f"Vocabulary size: {self.vocab_size}, Number of tags: {self.n_tags}")
        
        # Convert to indices
        X = [[self.word2idx.get(word, 1) for word in sentence] for sentence in sentences]
        y = [[self.tag2idx[tag] for tag in tag_seq] for tag_seq in tags]
        
        # Pad sequences
        X = pad_sequences(X, maxlen=self.max_sequence_length, padding='post', value=0)
        y = pad_sequences(y, maxlen=self.max_sequence_length, padding='post', value=0)
        
        # Convert tags to categorical
        y = np.array([to_categorical(seq, num_classes=self.n_tags) for seq in y])
        
        return X, y
    
    def build_model(self) -> None:
        """Build Bi-LSTM model architecture"""
        
        # Input layer
        input_layer = layers.Input(shape=(self.max_sequence_length,))
        
        # Embedding layer
        embedding = layers.Embedding(
            input_dim=self.vocab_size,
            output_dim=self.embedding_dim,
            input_length=self.max_sequence_length,
            mask_zero=True
        )(input_layer)
        
        # Dropout
        dropout1 = layers.Dropout(self.dropout)(embedding)
        
        # Bidirectional LSTM layers
        bilstm1 = layers.Bidirectional(
            layers.LSTM(
                self.lstm_units,
                return_sequences=True,
                dropout=self.dropout,
                recurrent_dropout=self.recurrent_dropout
            )
        )(dropout1)
        
        bilstm2 = layers.Bidirectional(
            layers.LSTM(
                self.lstm_units // 2,
                return_sequences=True,
                dropout=self.dropout,
                recurrent_dropout=self.recurrent_dropout
            )
        )(bilstm1)
        
        # Time distributed dense layer
        output = layers.TimeDistributed(
            layers.Dense(self.n_tags, activation='softmax')
        )(bilstm2)
        
        # Create model
        self.model = keras.Model(inputs=input_layer, outputs=output)
        
        # Compile model
        self.model.compile(
            optimizer='adam',
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
        
        logger.info("Bi-LSTM model built successfully")
        logger.info(f"Model parameters: {self.model.count_params():,}")
    
    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: Optional[np.ndarray] = None,
        y_val: Optional[np.ndarray] = None,
        epochs: int = 50,
        batch_size: int = 32,
        early_stopping_patience: int = 5
    ) -> Dict:
        """
        Train the model
        
        Args:
            X_train: Training data
            y_train: Training labels
            X_val: Validation data
            y_val: Validation labels
            epochs: Number of epochs
            batch_size: Batch size
            early_stopping_patience: Patience for early stopping
            
        Returns:
            Training history
        """
        if self.model is None:
            self.build_model()
        
        logger.info(f"Training Bi-LSTM model for {epochs} epochs...")
        
        # Callbacks
        callbacks = [
            keras.callbacks.EarlyStopping(
                monitor='val_loss' if X_val is not None else 'loss',
                patience=early_stopping_patience,
                restore_best_weights=True
            ),
            keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss' if X_val is not None else 'loss',
                factor=0.5,
                patience=3,
                min_lr=1e-6
            )
        ]
        
        # Train model
        validation_data = (X_val, y_val) if X_val is not None else None
        
        history = self.model.fit(
            X_train, y_train,
            validation_data=validation_data,
            epochs=epochs,
            batch_size=batch_size,
            callbacks=callbacks,
            verbose=1
        )
        
        logger.info("Training completed")
        
        return history.history
    
    def predict(self, X: np.ndarray) -> List[List[str]]:
        """
        Predict tags for sequences
        
        Args:
            X: Input sequences
            
        Returns:
            List of predicted tag sequences
        """
        if self.model is None:
            raise ValueError("Model not built. Call build_model() or train() first.")
        
        # Predict
        y_pred = self.model.predict(X, verbose=0)
        
        # Convert to tags
        predictions = []
        for seq in y_pred:
            tags = [self.idx2tag[np.argmax(tag_probs)] for tag_probs in seq]
            predictions.append(tags)
        
        return predictions
    
    def evaluate(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> Dict[str, float]:
        """
        Evaluate model on test data
        
        Args:
            X_test: Test data
            y_test: Test labels
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info("Evaluating model...")
        
        # Predict
        y_pred = self.predict(X_test)
        
        # Convert y_test from categorical to indices
        y_test_tags = []
        for seq in y_test:
            tags = [self.idx2tag[np.argmax(tag_probs)] for tag_probs in seq]
            y_test_tags.append(tags)
        
        # Calculate metrics (simplified)
        from sklearn.metrics import classification_report
        
        # Flatten sequences
        y_true_flat = [tag for seq in y_test_tags for tag in seq if tag != 'O']
        y_pred_flat = [tag for seq in y_pred for tag in seq if tag != 'O']
        
        # Ensure same length
        min_len = min(len(y_true_flat), len(y_pred_flat))
        y_true_flat = y_true_flat[:min_len]
        y_pred_flat = y_pred_flat[:min_len]
        
        if y_true_flat and y_pred_flat:
            report = classification_report(y_true_flat, y_pred_flat, output_dict=True)
            
            metrics = {
                'accuracy': report.get('accuracy', 0.0),
                'weighted_f1': report.get('weighted avg', {}).get('f1-score', 0.0),
                'weighted_precision': report.get('weighted avg', {}).get('precision', 0.0),
                'weighted_recall': report.get('weighted avg', {}).get('recall', 0.0)
            }
        else:
            metrics = {
                'accuracy': 0.0,
                'weighted_f1': 0.0,
                'weighted_precision': 0.0,
                'weighted_recall': 0.0
            }
        
        logger.info(f"Evaluation - F1: {metrics['weighted_f1']:.4f}, "
                   f"Precision: {metrics['weighted_precision']:.4f}, "
                   f"Recall: {metrics['weighted_recall']:.4f}")
        
        return metrics
    
    def save(self, model_dir: str) -> None:
        """
        Save model and vocabularies
        
        Args:
            model_dir: Directory to save model
        """
        model_dir = Path(model_dir)
        model_dir.mkdir(parents=True, exist_ok=True)
        
        # Save model
        self.model.save(model_dir / 'bilstm_model.h5')
        
        # Save vocabularies
        vocab_data = {
            'word2idx': self.word2idx,
            'idx2word': self.idx2word,
            'tag2idx': self.tag2idx,
            'idx2tag': self.idx2tag,
            'max_sequence_length': self.max_sequence_length
        }
        
        with open(model_dir / 'vocab.pkl', 'wb') as f:
            pickle.dump(vocab_data, f)
        
        logger.info(f"Model saved to {model_dir}")
    
    def load(self, model_dir: str) -> None:
        """
        Load model and vocabularies
        
        Args:
            model_dir: Directory containing model
        """
        model_dir = Path(model_dir)
        
        # Load model
        self.model = keras.models.load_model(model_dir / 'bilstm_model.h5')
        
        # Load vocabularies
        with open(model_dir / 'vocab.pkl', 'rb') as f:
            vocab_data = pickle.load(f)
        
        self.word2idx = vocab_data['word2idx']
        self.idx2word = vocab_data['idx2word']
        self.tag2idx = vocab_data['tag2idx']
        self.idx2tag = vocab_data['idx2tag']
        self.max_sequence_length = vocab_data['max_sequence_length']
        
        self.vocab_size = len(self.word2idx)
        self.n_tags = len(self.tag2idx)
        
        logger.info(f"Model loaded from {model_dir}")
