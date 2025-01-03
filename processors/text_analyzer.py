import spacy
import re
from typing import Dict, Any, List
from datetime import datetime

class TextAnalyzer:
    def __init__(self):
        # Load English language model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Enhanced patterns for financial data
        self.patterns = {
            'amount': r'\$\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',  # Matches $67.12
            'invoice_number': r'(?i)(?:invoice|receipt|ref|order)(?:[:\s#-]+)([\w\d-]+)',
            'date': r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}',
            'tax': r'(?i)(?:tax|gst|vat)[:\s]*\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            'total': r'(?i)(?:total|amount due|balance|sum)[:\s]*\$?\s*\d{1,3}(?:,\d{3})*(?:\.\d{2})?',
            'vendor_header': r'(?im)^([A-Za-z\s&]+)$'  # Look for company name at start of lines
        }
        
        # Invalid vendor names to filter out
        self.invalid_vendors = {
            'date', 'invoice', 'receipt', 'unknown', 'vendor', 'supplier', 
            'company', 'business', 'total', 'amount', 'due', 'paid', 'statement',
            'bill', 'payment', 'account'
        }

    def extract_amount(self, text: str) -> float:
        """Extract amount from text with improved decimal handling"""
        # First look for amounts with decimal points
        decimal_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*\.\d{2})'
        decimal_matches = re.finditer(decimal_pattern, text, re.IGNORECASE)
        amounts = []
        
        # Process matches with decimals
        for match in decimal_matches:
            try:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                if 0.01 <= amount <= 10000.00:  # Reasonable range check
                    amounts.append(amount)
            except:
                continue
        
        # If we found valid decimal amounts, use those
        if amounts:
            return max(amounts)  # Return the highest amount found
            
        # If no decimal amounts found, try whole numbers
        whole_pattern = r'\$\s*(\d{1,3}(?:,\d{3})*)'
        whole_matches = re.finditer(whole_pattern, text, re.IGNORECASE)
        
        for match in whole_matches:
            try:
                amount_str = match.group(1).replace(',', '')
                amount = float(amount_str)
                if 1.0 <= amount <= 10000.0:  # Reasonable range check
                    amounts.append(amount)
            except:
                continue
                
        if amounts:
            return max(amounts)  # Return the highest amount found
            
        return 0.0

    def clean_vendor_name(self, name: str) -> str:
        """Clean and validate vendor name"""
        if not name:
            return ''
            
        # Remove special characters and extra spaces
        name = re.sub(r'[^\w\s&]', ' ', name)
        name = re.sub(r'\s+', ' ', name).strip()
        
        # Remove any numbers or IDs from the end
        name = re.sub(r'\s+(?:\d+|[A-Z]+-\d+|\w+\d+\w*)$', '', name)
        
        # Check if the cleaned name is valid
        name_lower = name.lower()
        if (name_lower not in self.invalid_vendors and 
            not any(invalid in name_lower for invalid in self.invalid_vendors) and
            len(name) >= 3 and
            not name.isdigit() and
            not re.match(r'^[0-9\W]+$', name)):
            return name
            
        return ''

    def find_likely_vendor_name(self, text: str) -> str:
        """Find the most likely vendor name in the first few lines"""
        lines = text.split('\n')
        for line in lines[:5]:  # Check first 5 lines
            line = line.strip()
            if line and len(line) >= 3:
                cleaned = self.clean_vendor_name(line)
                if cleaned:
                    return cleaned
        return ''

    def extract_vendor_info(self, text: str) -> Dict[str, Any]:
        """Extract vendor information using multiple methods"""
        vendor_info = {
            'name': None,
            'address': [],
            'contact': []
        }
        
        # Method 1: Try finding vendor name in header
        vendor_name = self.find_likely_vendor_name(text)
        if vendor_name:
            vendor_info['name'] = vendor_name
            return vendor_info
        
        # Method 2: Use NLP for organization detection
        doc = self.nlp(text)
        org_candidates = []
        
        for ent in doc.ents:
            if ent.label_ == 'ORG':
                name = self.clean_vendor_name(ent.text)
                if name:
                    org_candidates.append(name)
        
        # Filter and sort candidates by length
        if org_candidates:
            # Pick the first valid organization name
            vendor_info['name'] = org_candidates[0]
        
        return vendor_info

    def extract_patterns(self, text: str) -> Dict[str, List[str]]:
        """Extract common financial patterns from text"""
        results = {}
        
        # Normalize text
        text = text.replace('\n', ' ').strip()
        
        for pattern_name, pattern in self.patterns.items():
            matches = re.finditer(pattern, text, re.MULTILINE | re.IGNORECASE)
            values = []
            
            for match in matches:
                if len(match.groups()) > 0:
                    values.append(match.group(1))
                else:
                    values.append(match.group(0))
                    
            if values:
                results[pattern_name] = values
                
        return results

    def process_text(self, text: str) -> Dict[str, Any]:
        """Process text and extract all relevant information"""
        # Extract patterns
        patterns = self.extract_patterns(text)
        
        # Extract vendor info
        vendor_info = self.extract_vendor_info(text)
        
        # Extract amount
        amount = self.extract_amount(text)
        
        # Format results
        results = {
            'patterns': patterns,
            'vendor_info': vendor_info,
            'financial_data': {
                'highest_amount': amount,
                'formatted_amount': f"${amount:.2f}"
            },
            'metadata': {
                'processed_at': datetime.now().isoformat()
            }
        }

        # Add invoice data
        invoice_data = self.extract_invoice_data(text, patterns, vendor_info)
        if invoice_data:
            results['invoice_data'] = invoice_data
        
        return results

    def extract_invoice_data(self, text: str, patterns: Dict[str, List[str]], vendor_info: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured invoice data"""
        today = datetime.now().strftime('%Y-%m-%d')
        
        data = {
            'vendor_name': vendor_info.get('name', ''),
            'invoice_number': None,
            'date': today,
            'due_date': None,
            'total_amount': None,
            'tax_amount': None
        }
        
        # Get invoice number from patterns
        if patterns.get('invoice_number'):
            data['invoice_number'] = patterns['invoice_number'][0]
        
        # Get dates
        if patterns.get('date'):
            dates = patterns['date']
            if len(dates) >= 1:
                data['date'] = dates[0]
            if len(dates) >= 2:
                data['due_date'] = dates[1]
                
        # Format amount
        if 'financial_data' in patterns:
            data['total_amount'] = patterns['financial_data']['formatted_amount']
        
        # Get tax amount
        if patterns.get('tax'):
            data['tax_amount'] = patterns['tax'][0]
            
        return data