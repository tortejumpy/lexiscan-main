"""
Spacy NER Predictor
Inference using trained Spacy NER model
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import spacy
from spacy.tokens import Doc

logger = logging.getLogger(__name__)


class SpacyNERPredictor:
    """
    Predict entities using trained Spacy NER model
    """
    
    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize predictor
        
        Args:
            model_path: Path to trained model directory
        """
        self.model_path = model_path
        self.nlp = None
        
        if model_path:
            self.load_model(model_path)
    
    def load_model(self, model_path: str) -> None:
        """
        Load trained Spacy model
        
        Args:
            model_path: Path to model directory
        """
        try:
            self.nlp = spacy.load(model_path)
            logger.info(f"Loaded Spacy NER model from {model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def predict(self, text: str) -> List[Dict]:
        """
        Extract entities from text
        
        Args:
            text: Input text
            
        Returns:
            List of entity dictionaries
        """
        if self.nlp is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Process text
        doc = self.nlp(text)
        
        # Extract entities
        entities = []
        for ent in doc.ents:
            entities.append({
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': 1.0,  # Spacy doesn't provide confidence by default
                'method': 'spacy'
            })
        
        logger.debug(f"Extracted {len(entities)} entities using Spacy")
        
        return entities
    
    def predict_batch(self, texts: List[str]) -> List[List[Dict]]:
        """
        Extract entities from multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of entity lists
        """
        if self.nlp is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        all_entities = []
        
        # Process texts in batch
        for doc in self.nlp.pipe(texts):
            entities = []
            for ent in doc.ents:
                entities.append({
                    'text': ent.text,
                    'label': ent.label_,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 1.0,
                    'method': 'spacy'
                })
            all_entities.append(entities)
        
        logger.info(f"Processed {len(texts)} texts in batch")
        
        return all_entities
    
    def get_entity_summary(self, entities: List[Dict]) -> Dict[str, int]:
        """
        Get summary of entity counts by type
        
        Args:
            entities: List of entities
            
        Returns:
            Dictionary with counts by label
        """
        summary = {}
        for entity in entities:
            label = entity['label']
            summary[label] = summary.get(label, 0) + 1
        return summary
    
    def visualize_entities(self, text: str, jupyter: bool = False) -> None:
        """
        Visualize entities in text
        
        Args:
            text: Input text
            jupyter: Whether running in Jupyter notebook
        """
        if self.nlp is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        from spacy import displacy
        
        doc = self.nlp(text)
        
        if jupyter:
            displacy.render(doc, style="ent", jupyter=True)
        else:
            html = displacy.render(doc, style="ent", page=True)
            
            # Save to file
            output_file = Path("entity_visualization.html")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html)
            
            logger.info(f"Visualization saved to {output_file}")
