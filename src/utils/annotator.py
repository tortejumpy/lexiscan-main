"""
Data Annotation Utilities for NER Training
Converts CUAD dataset to IOB2 format for NER training
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import pandas as pd
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Entity:
    """Represents a named entity"""
    text: str
    label: str
    start: int
    end: int


@dataclass
class AnnotatedDocument:
    """Represents an annotated document"""
    filename: str
    text: str
    entities: List[Entity]


class NERAnnotator:
    """
    Convert CUAD annotations to NER training format
    """
    
    # Entity type mapping from CUAD to our labels
    ENTITY_MAPPING = {
        'Parties': 'PARTY',
        'Agreement Date': 'DATE',
        'Effective Date': 'DATE',
        'Expiration Date': 'DATE',
        'Renewal Term': 'TERM',
        'Governing Law': 'JURISDICTION',
        'Document Name': 'DOC_NAME',
    }
    
    def __init__(self, cuad_json_path: str, contracts_dir: str):
        """
        Initialize annotator
        
        Args:
            cuad_json_path: Path to CUAD_v1.json
            contracts_dir: Directory containing contract text files
        """
        self.cuad_json_path = Path(cuad_json_path)
        self.contracts_dir = Path(contracts_dir)
        
        logger.info(f"Initializing NER Annotator with CUAD data from {cuad_json_path}")
    
    def load_cuad_data(self) -> Dict:
        """
        Load CUAD dataset
        
        Returns:
            CUAD data dictionary
        """
        with open(self.cuad_json_path, 'r', encoding='utf-8') as f:
            cuad_data = json.load(f)
        
        logger.info(f"Loaded CUAD dataset with {len(cuad_data.get('data', []))} entries")
        return cuad_data
    
    def load_master_clauses(self, csv_path: str) -> pd.DataFrame:
        """
        Load master clauses CSV
        
        Args:
            csv_path: Path to master_clauses.csv
            
        Returns:
            DataFrame with clause annotations
        """
        df = pd.read_csv(csv_path)
        logger.info(f"Loaded {len(df)} annotated contracts from master_clauses.csv")
        return df
    
    def extract_entities_from_row(
        self,
        row: pd.Series,
        text: str
    ) -> List[Entity]:
        """
        Extract entities from a master_clauses row
        
        Args:
            row: DataFrame row
            text: Full contract text
            
        Returns:
            List of Entity objects
        """
        entities = []
        
        # Extract parties
        if pd.notna(row.get('Parties-Answer')):
            parties_text = str(row['Parties-Answer'])
            # Parse parties (format: "['Company A', 'Company B']")
            try:
                parties_list = eval(parties_text)
                if isinstance(parties_list, list):
                    for party in parties_list:
                        # Find party in text
                        start = text.find(party)
                        if start != -1:
                            entities.append(Entity(
                                text=party,
                                label='PARTY',
                                start=start,
                                end=start + len(party)
                            ))
            except:
                pass
        
        # Extract dates
        date_fields = [
            ('Agreement Date-Answer', 'DATE'),
            ('Effective Date-Answer', 'DATE'),
            ('Expiration Date-Answer', 'DATE'),
        ]
        
        for field, label in date_fields:
            if pd.notna(row.get(field)):
                date_text = str(row[field])
                start = text.find(date_text)
                if start != -1:
                    entities.append(Entity(
                        text=date_text,
                        label=label,
                        start=start,
                        end=start + len(date_text)
                    ))
        
        # Extract jurisdiction
        if pd.notna(row.get('Governing Law-Answer')):
            jurisdiction = str(row['Governing Law-Answer'])
            start = text.find(jurisdiction)
            if start != -1:
                entities.append(Entity(
                    text=jurisdiction,
                    label='JURISDICTION',
                    start=start,
                    end=start + len(jurisdiction)
                ))
        
        # Extract renewal terms
        if pd.notna(row.get('Renewal Term-Answer')):
            term = str(row['Renewal Term-Answer'])
            start = text.find(term)
            if start != -1:
                entities.append(Entity(
                    text=term,
                    label='TERM',
                    start=start,
                    end=start + len(term)
                ))
        
        return entities
    
    def text_to_iob2(
        self,
        text: str,
        entities: List[Entity]
    ) -> List[Tuple[str, str]]:
        """
        Convert text and entities to IOB2 format
        
        Args:
            text: Input text
            entities: List of entities
            
        Returns:
            List of (token, tag) tuples
        """
        # Sort entities by start position
        entities = sorted(entities, key=lambda e: e.start)
        
        # Tokenize text (simple whitespace tokenization)
        tokens = text.split()
        token_positions = []
        current_pos = 0
        
        for token in tokens:
            start = text.find(token, current_pos)
            end = start + len(token)
            token_positions.append((token, start, end))
            current_pos = end
        
        # Assign IOB2 tags
        iob2_data = []
        
        for token, token_start, token_end in token_positions:
            tag = 'O'  # Default: Outside
            
            for entity in entities:
                # Check if token overlaps with entity
                if token_start >= entity.start and token_end <= entity.end:
                    # Token is inside entity
                    if token_start == entity.start:
                        tag = f'B-{entity.label}'  # Beginning
                    else:
                        tag = f'I-{entity.label}'  # Inside
                    break
            
            iob2_data.append((token, tag))
        
        return iob2_data
    
    def create_training_data(
        self,
        master_clauses_path: str,
        output_dir: str,
        max_samples: Optional[int] = None
    ) -> None:
        """
        Create IOB2 formatted training data from master_clauses.csv
        
        Args:
            master_clauses_path: Path to master_clauses.csv
            output_dir: Directory to save training data
            max_samples: Maximum number of samples to process
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load master clauses
        df = self.load_master_clauses(master_clauses_path)
        
        if max_samples:
            df = df.head(max_samples)
        
        all_iob2_data = []
        
        logger.info(f"Processing {len(df)} contracts for NER training data")
        
        for idx, row in df.iterrows():
            filename = row['Filename']
            
            # Load contract text
            contract_path = self.contracts_dir / filename.replace('.pdf', '.txt')
            
            if not contract_path.exists():
                logger.warning(f"Contract file not found: {contract_path}")
                continue
            
            with open(contract_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            # Extract entities
            entities = self.extract_entities_from_row(row, text)
            
            if not entities:
                continue
            
            # Convert to IOB2
            iob2_data = self.text_to_iob2(text, entities)
            all_iob2_data.extend(iob2_data)
            all_iob2_data.append(('', ''))  # Blank line between documents
            
            if (idx + 1) % 10 == 0:
                logger.info(f"Processed {idx + 1}/{len(df)} contracts")
        
        # Save to file
        output_file = output_dir / 'training_data.iob2'
        with open(output_file, 'w', encoding='utf-8') as f:
            for token, tag in all_iob2_data:
                if token:
                    f.write(f"{token}\t{tag}\n")
                else:
                    f.write("\n")
        
        logger.info(f"Saved IOB2 training data to {output_file}")
        logger.info(f"Total tokens: {len([t for t in all_iob2_data if t[0]])}")
    
    def create_spacy_training_data(
        self,
        master_clauses_path: str,
        output_file: str,
        max_samples: Optional[int] = None
    ) -> None:
        """
        Create Spacy-compatible training data
        
        Args:
            master_clauses_path: Path to master_clauses.csv
            output_file: Output JSON file path
            max_samples: Maximum number of samples
        """
        df = self.load_master_clauses(master_clauses_path)
        
        if max_samples:
            df = df.head(max_samples)
        
        training_data = []
        
        for idx, row in df.iterrows():
            filename = row['Filename']
            contract_path = self.contracts_dir / filename.replace('.pdf', '.txt')
            
            if not contract_path.exists():
                continue
            
            with open(contract_path, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            
            entities = self.extract_entities_from_row(row, text)
            
            if not entities:
                continue
            
            # Spacy format: (text, {"entities": [(start, end, label)]})
            spacy_entities = [
                (e.start, e.end, e.label) for e in entities
            ]
            
            training_data.append((text, {"entities": spacy_entities}))
        
        # Save to JSON
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2)
        
        logger.info(f"Saved Spacy training data to {output_file}")
        logger.info(f"Total training examples: {len(training_data)}")
