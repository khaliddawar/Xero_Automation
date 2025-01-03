import re
from typing import Dict, Any, List, Optional
from datetime import datetime
import spacy
from collections import Counter

class InvoiceAnalyzer:
    def __init__(self):
        """Initialize with comprehensive invoice patterns"""
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Define enhanced patterns for invoice data
        self.patterns = {
            'vendor_name': [
                r'(?i)^([A-Za-z0-9\s&.,]+)(?:\n|$)',  # Company name at start
                r'(?i)from:\s*([A-Za-z0-9\s&.,]+)',   # From: Company
                r'(?i)vendor:\s*([A-Za-z0-9\s&.,]+)',  # Vendor: Company
                r'(?i)bill\s+from:\s*([A-Za-z0-9\s&.,]+)',  # Bill From: Company
                r'(?i)payable\s+to:\s*([A-Za-z0-9\s&.,]+)'  # Payable to: Company
            ],
            'invoice_number': [
                r'(?i)invoice\s*#?\s*[:.]?\s*(\w+[-/]?\w+)',
                r'(?i)inv\s*#?\s*[:.]?\s*(\w+[-/]?\w+)',
                r'(?i)bill\s*#?\s*[:.]?\s*(\w+[-/]?\w+)',
                r'(?i)reference\s*#?\s*[:.]?\s*(\w+[-/]?\w+)',
                r'(?i)document\s*#?\s*[:.]?\s*(\w+[-/]?\w+)',
                r'(?i)inv[^a-z]+(\d+)',  # Matches INV12345
                r'(?i)ref[^a-z]+(\d+)',  # Matches REF12345
                r'#\s*(\d+)',            # Matches #12345
            ],
            'amount': [
                r'\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # $1,234.56
                r'(?i)total[\s:]*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(?i)amount\s+due[\s:]*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(?i)balance[\s:]*\$\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',
                r'(?i)total:?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)',  # Without $ symbol
                r'(?i)due:?\s*(\d{1,3}(?:,\d{3})*(?:\.\d{2})?)'     # Without $ symbol
            ],
            'date': [
                r'(?i)date[\s:]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
                r'(?i)invoice\s+date[\s:]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
                r'(?i)dated?[\s:]+([A-Za-z]+\s+\d{1,2},?\s+\d{4})',
                r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',  # 12/31/2024
                r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})'     # 2024/12/31
            ]
        }
        
        self.invalid_vendor_names = {
            'invoice', 'statement', 'bill', 'date', 'page', 'total',
            'amount', 'balance', 'payment', 'due', 'ref', 'number'
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        # Basic cleaning
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_by_pattern(self, text: str, pattern: str) -> str:
        """Extract text based on a pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        if match and match.group(1):
            return match.group(1).strip()
        return ''

    def extract_invoice_number(self, text: str) -> Optional[str]:
        """Extract invoice number using multiple methods"""
        for pattern in self.patterns['invoice_number']:
            number = self.extract_by_pattern(text, pattern)
            if number and len(number) >= 3:  # Minimum length check
                return number
        return None

    def extract_amount(self, text: str) -> Optional[float]:
        """Extract amount with proper currency handling"""
        amounts = []
        
        for pattern in self.patterns['amount']:
            matches = re.finditer(pattern, text)
            for match in matches:
                try:
                    # Remove currency symbols and commas
                    amount_str = match.group(1).replace('$', '').replace(',', '')
                    amount = float(amount_str)
                    if 0.01 <= amount <= 1000000:  # Reasonable range check
                        amounts.append(amount)
                except ValueError:
                    continue
                    
        if amounts:
            return max(amounts)  # Return the largest amount found
        return None

    def is_valid_vendor_name(self, name: str) -> bool:
        """Validate vendor name with stricter rules"""
        if not name:
            return False
            
        name = name.lower().strip()
        
        # Length check
        if len(name) < 3:
            return False
            
        # Check for invalid words
        if any(word in name.split() for word in self.invalid_vendor_names):
            return False
            
        # Must contain at least one letter
        if not any(c.isalpha() for c in name):
            return False
            
        # No excessive punctuation
        if len(re.findall(r'[^\w\s]', name)) > 2:
            return False
            
        return True

    def extract_vendor_info(self, text: str) -> Dict[str, Any]:
        """Extract vendor information with improved accuracy"""
        candidate_names = []
        
        # Method 1: Look for company patterns
        for pattern in self.patterns['vendor_name']:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip()
                if self.is_valid_vendor_name(name):
                    candidate_names.append(name)
        
        # Method 2: Use NLP for organization detection
        doc = self.nlp(text)
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                name = ent.text.strip()
                if self.is_valid_vendor_name(name):
                    candidate_names.append(name)
        
        if candidate_names:
            # Count occurrences and get the most common valid name
            name_counts = Counter(candidate_names)
            most_common = name_counts.most_common(1)[0][0]
            return {
                'name': most_common,
                'confidence': 'high' if name_counts[most_common] > 1 else 'medium'
            }
        
        return {'name': None, 'confidence': 'low'}

    def analyze_invoice(self, text: str) -> Dict[str, Any]:
        """Complete invoice analysis with confidence scoring"""
        # Clean text
        cleaned_text = self.clean_text(text)
        
        # Extract all components
        vendor_info = self.extract_vendor_info(cleaned_text)
        invoice_number = self.extract_invoice_number(cleaned_text)
        amount = self.extract_amount(cleaned_text)
        
        # Find dates
        dates = []
        for pattern in self.patterns['date']:
            date_matches = re.finditer(pattern, cleaned_text)
            dates.extend(match.group(1) for match in date_matches)
        
        # Format results
        results = {
            'vendor_name': vendor_info['name'],
            'invoice_number': invoice_number,
            'amount': amount,
            'date': dates[0] if dates else None,
            'due_date': dates[1] if len(dates) > 1 else None,
            'confidence_scores': {
                'vendor': vendor_info['confidence'],
                'invoice_number': 'high' if invoice_number else 'low',
                'amount': 'high' if amount is not None else 'low',
                'date': 'high' if dates else 'low'
            }
        }
        
        return results

# Function to handle different date formats
def parse_date(date_str: str) -> Optional[datetime]:
    """Parse date string into datetime object"""
    try:
        # Try different date formats
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%m/%d/%Y',
            '%B %d, %Y',
            '%b %d, %Y',
            '%Y/%m/%d'
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
                
        return None
    except Exception:
        return None