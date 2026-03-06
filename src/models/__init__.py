"""
Models Package
"""

# Always available - no heavy dependencies
from .baseline import BaselineNERModel, RegexExtractor, TFIDFClassifier

# Optional imports - only load if dependencies are available
__all__ = [
    'BaselineNERModel',
    'RegexExtractor',
    'TFIDFClassifier',
]

# Try to import Spacy NER (optional)
try:
    from .spacy_ner import SpacyNERTrainer, SpacyNERPredictor
    __all__.extend(['SpacyNERTrainer', 'SpacyNERPredictor'])
except Exception:
    # Catch all errors including DLL issues, missing dependencies, etc.
    SpacyNERTrainer = None
    SpacyNERPredictor = None

# Try to import BiLSTM (optional)
try:
    from .bilstm import BiLSTMNER
    __all__.append('BiLSTMNER')
except Exception:
    # Catch all errors including TensorFlow/Keras issues
    BiLSTMNER = None
