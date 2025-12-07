"""
SEC EDGAR XBRL Parser Service
Handles parsing of XBRL, XML, HTML, and other SEC filings
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import io
from bs4 import BeautifulSoup
import xml.etree.ElementTree as ET
import re

logger = logging.getLogger(__name__)


class SECEdgarParser:
    """Parser for SEC EDGAR filings including XBRL, XML, HTML formats"""
    
    # XBRL namespaces commonly used in SEC filings
    XBRL_NAMESPACES = {
        'xbrli': 'http://www.xbrl.org/2003/instance',
        'xbrldi': 'http://www.xbrl.org/2006/xbrldi',
        'link': 'http://www.xbrl.org/2003/linkbase',
        'xlink': 'http://www.w3.org/1999/xlink',
        'us-gaap': 'http://fasb.org/us-gaap/2023',
        'dei': 'http://xbrl.sec.gov/dei/2023',
        'iso4217': 'http://www.xbrl.org/2003/iso4217'
    }
    
    # Common US-GAAP elements for financial statements
    GAAP_ELEMENTS = {
        # Income Statement
        'revenue': [
            'Revenues',
            'RevenueFromContractWithCustomerExcludingAssessedTax',
            'SalesRevenueNet',
            'RevenueFromContractWithCustomer'
        ],
        'gross_profit': [
            'GrossProfit'
        ],
        'operating_income': [
            'OperatingIncomeLoss',
            'IncomeFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest'
        ],
        'net_income': [
            'NetIncomeLoss',
            'ProfitLoss'
        ],
        'earnings_per_share': [
            'EarningsPerShareBasic',
            'EarningsPerShareDiluted'
        ],
        
        # Balance Sheet
        'total_assets': [
            'Assets',
            'AssetsCurrent'
        ],
        'current_assets': [
            'AssetsCurrent'
        ],
        'cash': [
            'CashAndCashEquivalentsAtCarryingValue',
            'Cash'
        ],
        'total_liabilities': [
            'Liabilities',
            'LiabilitiesCurrent'
        ],
        'current_liabilities': [
            'LiabilitiesCurrent'
        ],
        'total_debt': [
            'DebtCurrent',
            'LongTermDebt',
            'DebtLongTermAndShortTerm'
        ],
        'shareholders_equity': [
            'StockholdersEquity',
            'StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest'
        ],
        
        # Cash Flow
        'operating_cash_flow': [
            'NetCashProvidedByUsedInOperatingActivities'
        ],
        'investing_cash_flow': [
            'NetCashProvidedByUsedInInvestingActivities'
        ],
        'financing_cash_flow': [
            'NetCashProvidedByUsedInFinancingActivities'
        ]
    }
    
    def __init__(self):
        self.supported_formats = ['xbrl', 'xml', 'htm', 'html', 'txt', 'json']
    
    def detect_filing_type(self, content: bytes, filename: str) -> str:
        """Detect the type of SEC filing from content and filename."""
        filename_lower = filename.lower()
        
        # XBRL files
        if filename_lower.endswith(('.xbrl', '.xml')) or '_htm.xml' in filename_lower:
            try:
                # Check if it's valid XBRL
                if b'<xbrl' in content or b'xbrli:' in content or b'us-gaap:' in content:
                    return 'xbrl'
                return 'xml'
            except:
                pass
        
        # HTML/HTM files
        if filename_lower.endswith(('.htm', '.html')):
            return 'html'
        
        # JSON files (modern SEC API format)
        if filename_lower.endswith('.json'):
            return 'json'
        
        # Text files
        if filename_lower.endswith('.txt'):
            return 'text'
        
        # Try to detect from content
        try:
            content_str = content.decode('utf-8', errors='ignore')[:1000]
            if '<xbrl' in content_str or 'xbrli:' in content_str:
                return 'xbrl'
            elif '<?xml' in content_str:
                return 'xml'
            elif '<html' in content_str.lower() or '<!doctype html' in content_str.lower():
                return 'html'
            elif content_str.strip().startswith('{'):
                return 'json'
        except:
            pass
        
        return 'unknown'
    
    def parse_file(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse SEC filing and extract structured financial data."""
        filing_type = self.detect_filing_type(content, filename)
        
        logger.info(f"Parsing file: {filename}, detected type: {filing_type}")
        
        if filing_type == 'xbrl':
            return self._parse_xbrl(content, filename)
        elif filing_type == 'html':
            return self._parse_html(content, filename)
        elif filing_type == 'xml':
            return self._parse_xml(content, filename)
        elif filing_type == 'json':
            return self._parse_json(content, filename)
        elif filing_type == 'text':
            return self._parse_text(content, filename)
        else:
            return {
                'error': f'Unsupported file format: {filing_type}',
                'filing_type': filing_type,
                'filename': filename
            }
    
    def _parse_xbrl(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse XBRL file and extract financial data."""
        try:
            # Parse XML
            root = ET.fromstring(content)
            
            # Extract company information
            company_info = self._extract_company_info_xbrl(root)
            
            # Extract financial statements
            financials = self._extract_financial_data_xbrl(root)
            
            # Extract context information (periods, segments)
            contexts = self._extract_contexts_xbrl(root)
            
            # Extract units (currencies)
            units = self._extract_units_xbrl(root)
            
            return {
                'filing_type': 'xbrl',
                'filename': filename,
                'company_info': company_info,
                'financials': financials,
                'contexts': contexts,
                'units': units,
                'parsed_successfully': True
            }
        except Exception as e:
            logger.error(f"Error parsing XBRL file: {str(e)}")
            return {
                'error': f'Failed to parse XBRL: {str(e)}',
                'filing_type': 'xbrl',
                'filename': filename,
                'parsed_successfully': False
            }
    
    def _extract_company_info_xbrl(self, root: ET.Element) -> Dict[str, Any]:
        """Extract company identifying information from XBRL."""
        company_info = {}
        
        # Common DEI (Document and Entity Information) elements
        dei_elements = {
            'EntityRegistrantName': 'company_name',
            'EntityCentralIndexKey': 'cik',
            'TradingSymbol': 'ticker',
            'EntityCommonStockSharesOutstanding': 'shares_outstanding',
            'EntityFilerCategory': 'filer_category',
            'EntityCurrentReportingStatus': 'reporting_status',
            'EntityVoluntaryFilers': 'voluntary_filer',
            'EntityWellKnownSeasonedIssuer': 'well_known_issuer',
            'DocumentType': 'document_type',
            'DocumentPeriodEndDate': 'period_end_date',
            'DocumentFiscalYearFocus': 'fiscal_year',
            'DocumentFiscalPeriodFocus': 'fiscal_period'
        }
        
        # Search for DEI elements
        for elem in root.iter():
            tag_name = elem.tag.split('}')[-1]  # Remove namespace
            if tag_name in dei_elements:
                key = dei_elements[tag_name]
                company_info[key] = elem.text
        
        return company_info
    
    def _extract_financial_data_xbrl(self, root: ET.Element) -> Dict[str, Any]:
        """Extract financial statement data from XBRL."""
        financials = {
            'income_statement': {},
            'balance_sheet': {},
            'cash_flow': {},
            'other_metrics': {}
        }
        
        # Extract all financial elements
        for elem in root.iter():
            tag_name = elem.tag.split('}')[-1]  # Remove namespace
            
            # Check if this is a GAAP element we're interested in
            for category, gaap_elements in self.GAAP_ELEMENTS.items():
                if tag_name in gaap_elements:
                    # Get the value
                    value = self._parse_xbrl_value(elem)
                    if value is not None:
                        # Get context ref to understand the period
                        context_ref = elem.get('contextRef', '')
                        
                        # Categorize the element
                        if any(x in category for x in ['revenue', 'income', 'profit', 'earnings']):
                            financials['income_statement'][category] = {
                                'value': value,
                                'context': context_ref,
                                'element': tag_name
                            }
                        elif any(x in category for x in ['assets', 'liabilities', 'equity', 'debt', 'cash']):
                            financials['balance_sheet'][category] = {
                                'value': value,
                                'context': context_ref,
                                'element': tag_name
                            }
                        elif 'cash_flow' in category:
                            financials['cash_flow'][category] = {
                                'value': value,
                                'context': context_ref,
                                'element': tag_name
                            }
        
        return financials
    
    def _parse_xbrl_value(self, elem: ET.Element) -> Optional[float]:
        """Parse numeric value from XBRL element."""
        try:
            text = elem.text
            if text:
                # Remove commas and convert to float
                value = float(text.replace(',', ''))
                
                # Check for scale attributes (e.g., values in thousands)
                decimals = elem.get('decimals')
                scale = elem.get('scale')
                
                if scale:
                    value = value * (10 ** int(scale))
                
                return value
        except (ValueError, AttributeError):
            return None
        
        return None
    
    def _extract_contexts_xbrl(self, root: ET.Element) -> Dict[str, Any]:
        """Extract context information (time periods, segments) from XBRL."""
        contexts = {}
        
        for context in root.findall('.//{http://www.xbrl.org/2003/instance}context'):
            context_id = context.get('id')
            if context_id:
                period_info = {}
                
                # Extract period information
                period = context.find('{http://www.xbrl.org/2003/instance}period')
                if period is not None:
                    instant = period.find('{http://www.xbrl.org/2003/instance}instant')
                    start_date = period.find('{http://www.xbrl.org/2003/instance}startDate')
                    end_date = period.find('{http://www.xbrl.org/2003/instance}endDate')
                    
                    if instant is not None:
                        period_info['instant'] = instant.text
                    if start_date is not None:
                        period_info['start_date'] = start_date.text
                    if end_date is not None:
                        period_info['end_date'] = end_date.text
                
                # Extract entity information
                entity = context.find('{http://www.xbrl.org/2003/instance}entity')
                if entity is not None:
                    identifier = entity.find('{http://www.xbrl.org/2003/instance}identifier')
                    if identifier is not None:
                        period_info['cik'] = identifier.text
                
                contexts[context_id] = period_info
        
        return contexts
    
    def _extract_units_xbrl(self, root: ET.Element) -> Dict[str, str]:
        """Extract unit definitions (currencies) from XBRL."""
        units = {}
        
        for unit in root.findall('.//{http://www.xbrl.org/2003/instance}unit'):
            unit_id = unit.get('id')
            if unit_id:
                measure = unit.find('{http://www.xbrl.org/2003/instance}measure')
                if measure is not None:
                    units[unit_id] = measure.text.split(':')[-1]  # Get currency code
        
        return units
    
    def _parse_html(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse HTML SEC filing (e.g., 10-K, 10-Q HTML format)."""
        try:
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extract tables (financial statements are usually in tables)
            tables = []
            for table in soup.find_all('table'):
                table_data = self._parse_html_table(table)
                if table_data:
                    tables.append(table_data)
            
            # Extract text content
            text_content = soup.get_text()
            
            # Try to identify company name
            company_name = self._extract_company_name_html(soup)
            
            # Try to identify filing type
            filing_type = self._extract_filing_type_html(soup, text_content)
            
            return {
                'filing_type': filing_type,
                'filename': filename,
                'company_name': company_name,
                'tables': tables,
                'text_length': len(text_content),
                'table_count': len(tables),
                'parsed_successfully': True
            }
        except Exception as e:
            logger.error(f"Error parsing HTML file: {str(e)}")
            return {
                'error': f'Failed to parse HTML: {str(e)}',
                'filing_type': 'html',
                'filename': filename,
                'parsed_successfully': False
            }
    
    def _parse_html_table(self, table) -> Optional[Dict[str, Any]]:
        """Parse a single HTML table into structured data."""
        try:
            rows = []
            headers = []
            
            # Extract headers
            header_row = table.find('tr')
            if header_row:
                headers = [th.get_text(strip=True) for th in header_row.find_all(['th', 'td'])]
            
            # Extract data rows
            for tr in table.find_all('tr')[1:]:  # Skip header row
                cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
                if cells:
                    rows.append(cells)
            
            if not rows:
                return None
            
            return {
                'headers': headers,
                'rows': rows,
                'row_count': len(rows),
                'column_count': len(headers)
            }
        except Exception as e:
            logger.debug(f"Error parsing table: {str(e)}")
            return None
    
    def _extract_company_name_html(self, soup) -> Optional[str]:
        """Extract company name from HTML filing."""
        # Look for common patterns
        patterns = [
            soup.find('span', class_='companyName'),
            soup.find('div', class_='companyName'),
            soup.find(text=re.compile(r'Company Name:', re.I))
        ]
        
        for pattern in patterns:
            if pattern:
                return pattern.get_text(strip=True) if hasattr(pattern, 'get_text') else str(pattern)
        
        return None
    
    def _extract_filing_type_html(self, soup, text: str) -> str:
        """Determine filing type from HTML content."""
        text_lower = text.lower()
        
        if '10-k' in text_lower or 'annual report' in text_lower:
            return '10-K'
        elif '10-q' in text_lower or 'quarterly report' in text_lower:
            return '10-Q'
        elif '8-k' in text_lower or 'current report' in text_lower:
            return '8-K'
        elif 'proxy statement' in text_lower or 'def 14a' in text_lower:
            return 'DEF 14A'
        elif 's-1' in text_lower or 'registration statement' in text_lower:
            return 'S-1'
        
        return 'html'
    
    def _parse_xml(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse generic XML file (non-XBRL)."""
        try:
            root = ET.fromstring(content)
            
            # Extract all elements into a dictionary
            data = self._xml_to_dict(root)
            
            return {
                'filing_type': 'xml',
                'filename': filename,
                'data': data,
                'root_tag': root.tag,
                'parsed_successfully': True
            }
        except Exception as e:
            logger.error(f"Error parsing XML file: {str(e)}")
            return {
                'error': f'Failed to parse XML: {str(e)}',
                'filing_type': 'xml',
                'filename': filename,
                'parsed_successfully': False
            }
    
    def _xml_to_dict(self, element: ET.Element) -> Dict[str, Any]:
        """Convert XML element to dictionary recursively."""
        result = {}
        
        # Add attributes
        if element.attrib:
            result['@attributes'] = element.attrib
        
        # Add text content
        if element.text and element.text.strip():
            if len(element) == 0:  # Leaf node
                return element.text.strip()
            result['#text'] = element.text.strip()
        
        # Add child elements
        for child in element:
            child_data = self._xml_to_dict(child)
            child_tag = child.tag.split('}')[-1]  # Remove namespace
            
            if child_tag in result:
                # Multiple elements with same tag - convert to list
                if not isinstance(result[child_tag], list):
                    result[child_tag] = [result[child_tag]]
                result[child_tag].append(child_data)
            else:
                result[child_tag] = child_data
        
        return result if result else None
    
    def _parse_json(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse JSON SEC filing (modern API format)."""
        try:
            import json
            data = json.loads(content.decode('utf-8'))
            
            return {
                'filing_type': 'json',
                'filename': filename,
                'data': data,
                'parsed_successfully': True
            }
        except Exception as e:
            logger.error(f"Error parsing JSON file: {str(e)}")
            return {
                'error': f'Failed to parse JSON: {str(e)}',
                'filing_type': 'json',
                'filename': filename,
                'parsed_successfully': False
            }
    
    def _parse_text(self, content: bytes, filename: str) -> Dict[str, Any]:
        """Parse plain text SEC filing."""
        try:
            text = content.decode('utf-8', errors='ignore')
            
            # Extract basic information
            lines = text.split('\n')
            
            # Try to find company name (usually in first 50 lines)
            company_name = None
            for line in lines[:50]:
                if 'COMPANY' in line.upper() or 'REGISTRANT' in line.upper():
                    company_name = line.strip()
                    break
            
            # Try to identify filing type
            filing_type = 'text'
            for line in lines[:20]:
                if '10-K' in line:
                    filing_type = '10-K'
                    break
                elif '10-Q' in line:
                    filing_type = '10-Q'
                    break
                elif '8-K' in line:
                    filing_type = '8-K'
                    break
            
            return {
                'filing_type': filing_type,
                'filename': filename,
                'company_name': company_name,
                'text': text[:5000],  # First 5000 characters
                'line_count': len(lines),
                'character_count': len(text),
                'parsed_successfully': True
            }
        except Exception as e:
            logger.error(f"Error parsing text file: {str(e)}")
            return {
                'error': f'Failed to parse text: {str(e)}',
                'filing_type': 'text',
                'filename': filename,
                'parsed_successfully': False
            }


# Singleton instance
sec_edgar_parser = SECEdgarParser()
