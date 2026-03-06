"""
Spacy NER Model Trainer
Custom NER training for legal contract entities
"""

import logging
import random
import json
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import spacy
from spacy.training import Example
from spacy.util import minibatch, compounding

logger = logging.getLogger(__name__)


class SpacyNERTrainer:
    """
    Train custom Spacy NER model for legal entities
    """
    
    def __init__(
        self,
        base_model: str = "en_core_web_sm",
        entity_labels: Optional[List[str]] = None
    ):
        """
        Initialize Spacy NER trainer
        
        Args:
            base_model: Base Spacy model to use
            entity_labels: List of entity labels to train
        """
        self.base_model = base_model
        self.entity_labels = entity_labels or [
            'PARTY', 'DATE', 'AMOUNT', 'JURISDICTION', 'TERM'
        ]
        
        # Load base model
        try:
            self.nlp = spacy.load(base_model)
            logger.info(f"Loaded base model: {base_model}")
        except OSError:
            logger.warning(f"Base model {base_model} not found, creating blank model")
            self.nlp = spacy.blank("en")
        
        # Get or create NER component
        if "ner" not in self.nlp.pipe_names:
            ner = self.nlp.add_pipe("ner", last=True)
        else:
            ner = self.nlp.get_pipe("ner")
        
        # Add entity labels
        for label in self.entity_labels:
            ner.add_label(label)
        
        logger.info(f"SpacyNERTrainer initialized with labels: {self.entity_labels}")
    
    def load_training_data(self, json_path: str) -> List[Tuple]:
        """
        Load training data from JSON file
        
        Args:
            json_path: Path to training data JSON
            
        Returns:
            List of (text, annotations) tuples
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            training_data = json.load(f)
        
        logger.info(f"Loaded {len(training_data)} training examples")
        return training_data
    
    def train(
        self,
        training_data: List[Tuple],
        n_iter: int = 30,
        dropout: float = 0.2,
        batch_size: int = 32,
        output_dir: Optional[str] = None
    ) -> Dict[str, float]:
        """
        Train the NER model
        
        Args:
            training_data: List of (text, annotations) tuples
            n_iter: Number of training iterations
            dropout: Dropout rate
            batch_size: Batch size
            output_dir: Directory to save model
            
        Returns:
            Dictionary with training metrics
        """
        logger.info(f"Starting training for {n_iter} iterations...")
        
        # Disable other pipes during training
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != "ner"]
        
        with self.nlp.disable_pipes(*other_pipes):
            # Get NER component
            ner = self.nlp.get_pipe("ner")
            
            # Initialize optimizer
            optimizer = self.nlp.initialize()
            
            # Training loop
            losses_history = []
            
            for iteration in range(n_iter):
                random.shuffle(training_data)
                losses = {}
                
                # Create batches
                batches = minibatch(training_data, size=compounding(4.0, batch_size, 1.001))
                
                for batch in batches:
                    examples = []
                    
                    for text, annotations in batch:
                        doc = self.nlp.make_doc(text)
                        example = Example.from_dict(doc, annotations)
                        examples.append(example)
                    
                    # Update model
                    self.nlp.update(
                        examples,
                        drop=dropout,
                        losses=losses
                    )
                
                avg_loss = losses.get('ner', 0.0)
                losses_history.append(avg_loss)
                
                if (iteration + 1) % 5 == 0:
                    logger.info(f"Iteration {iteration + 1}/{n_iter}, Loss: {avg_loss:.4f}")
        
        # Save model if output directory provided
        if output_dir:
            self.save_model(output_dir)
        
        metrics = {
            'final_loss': losses_history[-1] if losses_history else 0.0,
            'avg_loss': sum(losses_history) / len(losses_history) if losses_history else 0.0,
            'iterations': n_iter
        }
        
        logger.info(f"Training completed. Final loss: {metrics['final_loss']:.4f}")
        
        return metrics
    
    def evaluate(
        self,
        test_data: List[Tuple]
    ) -> Dict[str, float]:
        """
        Evaluate model on test data
        
        Args:
            test_data: List of (text, annotations) tuples
            
        Returns:
            Dictionary with evaluation metrics
        """
        logger.info(f"Evaluating on {len(test_data)} test examples...")
        
        examples = []
        for text, annotations in test_data:
            doc = self.nlp.make_doc(text)
            example = Example.from_dict(doc, annotations)
            examples.append(example)
        
        # Calculate scores
        scores = self.nlp.evaluate(examples)
        
        metrics = {
            'precision': scores.get('ents_p', 0.0),
            'recall': scores.get('ents_r', 0.0),
            'f1': scores.get('ents_f', 0.0)
        }
        
        logger.info(f"Evaluation - P: {metrics['precision']:.4f}, "
                   f"R: {metrics['recall']:.4f}, F1: {metrics['f1']:.4f}")
        
        return metrics
    
    def save_model(self, output_dir: str) -> None:
        """
        Save trained model to directory
        
        Args:
            output_dir: Directory to save model
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        self.nlp.to_disk(output_dir)
        logger.info(f"Model saved to {output_dir}")
    
    def load_model(self, model_dir: str) -> None:
        """
        Load trained model from directory
        
        Args:
            model_dir: Directory containing model
        """
        self.nlp = spacy.load(model_dir)
        logger.info(f"Model loaded from {model_dir}")


def create_synthetic_training_data(
    contracts_dir: str,
    master_clauses_path: str,
    output_file: str,
    max_samples: int = 100
) -> None:
    """
    Create synthetic training data from CUAD dataset
    
    Args:
        contracts_dir: Directory with contract text files
        master_clauses_path: Path to master_clauses.csv
        output_file: Output JSON file path
        max_samples: Maximum number of samples
    """
    import pandas as pd
    
    logger.info("Creating synthetic training data...")
    
    # Load master clauses
    df = pd.read_csv(master_clauses_path)
    df = df.head(max_samples)
    
    training_data = []
    contracts_dir = Path(contracts_dir)
    
    for idx, row in df.iterrows():
        filename = row['Filename']
        contract_path = contracts_dir / filename.replace('.pdf', '.txt')
        
        if not contract_path.exists():
            continue
        
        # Read contract text
        with open(contract_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()[:5000]  # Limit to first 5000 chars
        
        # Extract entities from row
        entities = []
        
        # Parties
        if pd.notna(row.get('Parties-Answer')):
            parties_text = str(row['Parties-Answer'])
            try:
                parties_list = eval(parties_text)
                if isinstance(parties_list, list):
                    for party in parties_list:
                        start = text.find(party)
                        if start != -1:
                            entities.append((start, start + len(party), 'PARTY'))
            except:
                pass
        
        # Dates
        date_fields = ['Agreement Date-Answer', 'Effective Date-Answer', 'Expiration Date-Answer']
        for field in date_fields:
            if pd.notna(row.get(field)):
                date_text = str(row[field])
                start = text.find(date_text)
                if start != -1:
                    entities.append((start, start + len(date_text), 'DATE'))
        
        # Jurisdiction
        if pd.notna(row.get('Governing Law-Answer')):
            jurisdiction = str(row['Governing Law-Answer'])
            start = text.find(jurisdiction)
            if start != -1:
                entities.append((start, start + len(jurisdiction), 'JURISDICTION'))
        
        if entities:
            training_data.append((text, {"entities": entities}))
        
        if (idx + 1) % 20 == 0:
            logger.info(f"Processed {idx + 1}/{len(df)} contracts")
    
    # Save to JSON
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2)
    
    logger.info(f"Created {len(training_data)} training examples")
    logger.info(f"Saved to {output_file}")
