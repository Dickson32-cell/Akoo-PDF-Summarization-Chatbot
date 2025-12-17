"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     AKOO AI - Knowledge Graph Generator                                     ║
║     Created by: Abdul Rashid Dickson                                        ║
║     © 2025 All Rights Reserved                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
import re
from collections import defaultdict
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

class KnowledgeGraphGenerator:
    """Generate interactive knowledge graphs from document content"""
    
    CREATOR = "Abdul Rashid Dickson"
    
    def __init__(self):
        self.entity_patterns = {
            'person': r'\b[A-Z][a-z]+ [A-Z][a-z]+\b',
            'organization': r'\b(?:University|Institute|Corporation|Company|Inc\.|Ltd\.)[^\.,]*\b',
            'concept': r'\b(?:theory|concept|principle|methodology|approach|framework)\s+of\s+\w+\b',
            'date': r'\b(?:\d{4}|\d{1,2}/\d{1,2}/\d{4}|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4})\b'
        }
    
    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract named entities from text"""
        entities = defaultdict(list)
        
        for entity_type, pattern in self.entity_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            # Deduplicate and clean
            unique_matches = list(set([m.strip() for m in matches if len(m.strip()) > 2]))
            entities[entity_type] = unique_matches[:20]  # Limit to 20 per type
        
        return dict(entities)
    
    def extract_relationships(self, text: str, entities: Dict[str, List[str]]) -> List[Tuple[str, str, str]]:
        """Extract relationships between entities"""
        relationships = []
        
        # Flatten entities
        all_entities = []
        for entity_list in entities.values():
            all_entities.extend(entity_list)
        
        # Simple co-occurrence based relationships
        sentences = text.split('.')
        for sentence in sentences:
            sentence_entities = [e for e in all_entities if e.lower() in sentence.lower()]
            
            # Create relationships between entities that appear together
            for i, e1 in enumerate(sentence_entities):
                for e2 in sentence_entities[i+1:]:
                    # Try to find relationship type
                    rel_type = self._infer_relationship(sentence, e1, e2)
                    relationships.append((e1, rel_type, e2))
        
        # Deduplicate
        unique_rels = list(set(relationships))[:50]  # Limit to 50 relationships
        return unique_rels
    
    def _infer_relationship(self, sentence: str, e1: str, e2: str) -> str:
        """Infer the type of relationship between two entities"""
        sentence_lower = sentence.lower()
        
        # Common relationship indicators
        if any(word in sentence_lower for word in ['wrote', 'authored', 'published']):
            return 'authored'
        elif any(word in sentence_lower for word in ['discovered', 'invented', 'created']):
            return 'discovered'
        elif any(word in sentence_lower for word in ['works at', 'employed by', 'member of']):
            return 'works_at'
        elif any(word in sentence_lower for word in ['related to', 'connected to', 'associated with']):
            return 'related_to'
        elif any(word in sentence_lower for word in ['uses', 'utilizes', 'employs']):
            return 'uses'
        elif any(word in sentence_lower for word in ['causes', 'leads to', 'results in']):
            return 'causes'
        else:
            return 'mentioned_with'
    
    def generate_graph(self, text: str, title: str = "Document") -> Dict[str, Any]:
        """Generate a knowledge graph from text"""
        logger.info(f"Generating knowledge graph for document: {title}")
        
        # Extract entities
        entities = self.extract_entities(text)
        
        # Extract relationships
        relationships = self.extract_relationships(text, entities)
        
        # Build graph structure for visualization
        nodes = []
        node_id_map = {}
        node_id = 0
        
        for entity_type, entity_list in entities.items():
            for entity in entity_list:
                node_id_map[entity] = node_id
                nodes.append({
                    'id': node_id,
                    'label': entity,
                    'type': entity_type,
                    'size': 10 + len([r for r in relationships if entity in r]) * 2
                })
                node_id += 1
        
        # Build edges
        edges = []
        for source, rel_type, target in relationships:
            if source in node_id_map and target in node_id_map:
                edges.append({
                    'source': node_id_map[source],
                    'target': node_id_map[target],
                    'label': rel_type
                })
        
        return {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'title': title,
                'entity_count': len(nodes),
                'relationship_count': len(edges),
                'creator': self.CREATOR
            }
        }
    
    def generate_summary_stats(self, graph: Dict[str, Any]) -> Dict[str, Any]:
        """Generate summary statistics for the knowledge graph"""
        nodes = graph.get('nodes', [])
        edges = graph.get('edges', [])
        
        # Count by type
        type_counts = defaultdict(int)
        for node in nodes:
            type_counts[node.get('type', 'unknown')] += 1
        
        # Find most connected nodes
        connection_counts = defaultdict(int)
        for edge in edges:
            connection_counts[edge['source']] += 1
            connection_counts[edge['target']] += 1
        
        most_connected = sorted(connection_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        most_connected_nodes = [
            {'node': nodes[node_id]['label'], 'connections': count}
            for node_id, count in most_connected if node_id < len(nodes)
        ]
        
        return {
            'total_entities': len(nodes),
            'total_relationships': len(edges),
            'entities_by_type': dict(type_counts),
            'most_connected': most_connected_nodes,
            'creator': self.CREATOR
        }
