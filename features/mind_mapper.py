"""
╔══════════════════════════════════════════════════════════════════════════════╗
║     AKOO AI - Mind Map Generator                                            ║
║     Created by: Abdul Rashid Dickson                                        ║
║     © 2025 All Rights Reserved                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import logging
import re
from typing import Dict, List, Any
from collections import defaultdict

logger = logging.getLogger(__name__)

class MindMapGenerator:
    """Generate hierarchical mind maps from document content"""
    
    CREATOR = "Abdul Rashid Dickson"
    
    def __init__(self):
        self.section_patterns = [
            r'^#+\s+(.+)$',  # Markdown headers
            r'^([A-Z][^.!?]*):$',  # Title case with colon
            r'^\d+\.\s+(.+)$',  # Numbered sections
            r'^[IVX]+\.\s+(.+)$',  # Roman numeral sections
        ]
    
    def extract_structure(self, text: str) -> Dict[str, Any]:
        """Extract hierarchical structure from text"""
        lines = text.split('\n')
        structure = {
            'title': 'Document',
            'children': []
        }
        
        current_section = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Check if this is a section header
            is_header = False
            header_level = 0
            header_text = line
            
            # Check markdown headers
            md_match = re.match(r'^(#+)\s+(.+)$', line)
            if md_match:
                is_header = True
                header_level = len(md_match.group(1))
                header_text = md_match.group(2)
            
            # Check numbered sections
            num_match = re.match(r'^(\d+)\.\s+(.+)$', line)
            if num_match and not is_header:
                is_header = True
                header_level = 2
                header_text = num_match.group(2)
            
            # Check for ALL CAPS headers
            if line.isupper() and len(line) > 5 and len(line) < 100:
                is_header = True
                header_level = 1
                header_text = line.title()
            
            if is_header:
                # Save previous section
                if current_section:
                    current_section['content'] = ' '.join(current_content[:100])  # Limit content
                    structure['children'].append(current_section)
                
                # Start new section
                current_section = {
                    'title': header_text[:100],  # Limit title length
                    'level': header_level,
                    'children': [],
                    'content': ''
                }
                current_content = []
            else:
                current_content.append(line)
        
        # Add last section
        if current_section:
            current_section['content'] = ' '.join(current_content[:100])
            structure['children'].append(current_section)
        
        # If no structure found, create from paragraphs
        if not structure['children']:
            structure = self._structure_from_paragraphs(text)
        
        return structure
    
    def _structure_from_paragraphs(self, text: str) -> Dict[str, Any]:
        """Create structure from paragraphs when no headers found"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        
        structure = {
            'title': 'Document Analysis',
            'children': []
        }
        
        # First paragraph as introduction
        if paragraphs:
            structure['children'].append({
                'title': 'Introduction',
                'level': 1,
                'content': paragraphs[0][:500],
                'children': []
            })
        
        # Middle paragraphs as main content
        if len(paragraphs) > 2:
            main_content = {
                'title': 'Main Content',
                'level': 1,
                'children': [],
                'content': ''
            }
            
            for i, para in enumerate(paragraphs[1:-1], 1):
                # Extract key phrase from paragraph
                first_sentence = para.split('.')[0][:80]
                main_content['children'].append({
                    'title': f'Point {i}: {first_sentence}...',
                    'level': 2,
                    'content': para[:300],
                    'children': []
                })
            
            structure['children'].append(main_content)
        
        # Last paragraph as conclusion
        if len(paragraphs) > 1:
            structure['children'].append({
                'title': 'Conclusion',
                'level': 1,
                'content': paragraphs[-1][:500],
                'children': []
            })
        
        return structure
    
    def extract_key_concepts(self, text: str) -> List[str]:
        """Extract key concepts/topics from text"""
        # Simple keyword extraction based on frequency and capitalization
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # Count frequencies
        freq = defaultdict(int)
        for word in words:
            if len(word) > 2:
                freq[word] += 1
        
        # Sort by frequency and return top concepts
        sorted_concepts = sorted(freq.items(), key=lambda x: x[1], reverse=True)
        return [concept for concept, count in sorted_concepts[:10]]
    
    def generate_mindmap(self, text: str, title: str = "Document") -> Dict[str, Any]:
        """Generate a mind map from text"""
        logger.info(f"Generating mind map for document: {title}")
        
        # Extract structure
        structure = self.extract_structure(text)
        structure['title'] = title
        
        # Extract key concepts
        concepts = self.extract_key_concepts(text)
        
        # Add concepts as a branch
        if concepts:
            structure['children'].append({
                'title': 'Key Concepts',
                'level': 1,
                'children': [{'title': c, 'level': 2, 'children': []} for c in concepts],
                'content': ''
            })
        
        return {
            'mindmap': structure,
            'metadata': {
                'title': title,
                'sections': len(structure.get('children', [])),
                'concepts': len(concepts),
                'creator': self.CREATOR
            }
        }
    
    def to_markdown(self, mindmap: Dict[str, Any], indent: int = 0) -> str:
        """Convert mind map to markdown format"""
        result = []
        
        prefix = '  ' * indent
        bullet = '- ' if indent > 0 else '# '
        
        result.append(f"{prefix}{bullet}{mindmap.get('title', 'Untitled')}")
        
        if mindmap.get('content'):
            result.append(f"{prefix}  > {mindmap['content'][:100]}...")
        
        for child in mindmap.get('children', []):
            result.append(self.to_markdown(child, indent + 1))
        
        return '\n'.join(result)
