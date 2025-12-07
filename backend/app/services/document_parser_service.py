"""
Document Parser Service for Financial Documents
Supports: Profit & Loss Statements, Balance Sheets, Pink Slips (Trade Confirmations)
"""

import csv
import io
import re
import math
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class FinancialDocumentParser:
    """Parser for various financial documents"""
    
    def __init__(self):
        # Keywords for document type detection
        self.pl_keywords = ['revenue', 'income', 'expense', 'profit', 'loss', 'net income', 'gross profit']
        self.balance_sheet_keywords = ['assets', 'liabilities', 'equity', 'total assets', 'current assets']
        self.pink_slip_keywords = ['trade', 'execution', 'shares', 'price', 'commission', 'symbol']
    
    def detect_document_type(self, content: str) -> str:
        """Detect the type of financial document"""
        content_lower = content.lower()
        
        pl_score = sum(1 for keyword in self.pl_keywords if keyword in content_lower)
        bs_score = sum(1 for keyword in self.balance_sheet_keywords if keyword in content_lower)
        ps_score = sum(1 for keyword in self.pink_slip_keywords if keyword in content_lower)
        
        scores = {
            'profit_loss': pl_score,
            'balance_sheet': bs_score,
            'pink_slip': ps_score
        }
        
        detected_type = max(scores, key=scores.get)
        
        if scores[detected_type] == 0:
            return 'unknown'
        
        return detected_type
    
    def parse_csv(self, file_content: bytes, filename: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
        """
        Parse CSV file and return document type and parsed data.
        If the file is HTML, extract tables and convert to CSV first.
        """
        try:
            # Detect if file is HTML by filename or content
            is_html = False
            # Correct simple filename-based HTML detection
            if filename and filename.lower().endswith(('.htm', '.html')):
                is_html = True
            else:
                # Check for HTML doctype or tags in first 1KB
                sample = file_content[:1024].decode('utf-8', errors='ignore').lower()
                if '<html' in sample or '<table' in sample:
                    is_html = True
            
            if is_html:
                try:
                    import pandas as pd
                    from bs4 import BeautifulSoup
                    from io import StringIO
                except ImportError as e:
                    logger.error("pandas and beautifulsoup4 are required for HTML table extraction.")
                    raise
                # Financial keyword heuristics
                financial_keywords = {
                    'revenue','revenues','sales','net income','income','expense','expenses','gross','profit',
                    'assets','liabilities','equity','total assets','cash','operating','financing','investing',
                    'net cash','shareholders','depreciation','amortization','cost of goods','cost of revenues'
                }
                soup = BeautifulSoup(file_content, 'html.parser')
                tables = soup.find_all('table')
                if not tables:
                    raise ValueError("No tables found in HTML file.")

                filtered_csv = []
                total_tables = 0
                kept_tables = 0
                # Structured lines will accumulate simplified "category,amount" pairs to aid downstream parsing
                structured_lines: List[str] = ["category,amount"]
                # Multi-period structured financial data placeholder
                multi_data = {
                    'income_statement': {
                        'periods': {},  # year -> {revenue:{}, expenses:{}, gross_profit, operating_income, net_income}
                        'metrics': {}
                    },
                    'balance_sheet': {
                        'periods': {},  # year -> {assets:{}, liabilities:{}, equity:{}}
                        'metrics': {}
                    },
                    'cash_flow_statement': {
                        'periods': {},  # year -> {operating:{}, investing:{}, financing:{}, net_change, beginning_cash, ending_cash}
                        'metrics': {}
                    }
                }

                def canonical_label(label: str) -> str:
                    l = label.lower().strip()
                    l = re.sub(r'[^a-z0-9]+', ' ', l)
                    l = re.sub(r'\s+', ' ', l).strip()
                    synonyms = {
                        'revenues': 'revenue', 'sales': 'revenue', 'cost of revenues': 'cost of goods sold',
                        'cost of goods sold': 'cost of goods sold', 'gross profit loss': 'gross profit',
                        'gross profit': 'gross profit', 'operating expenses': 'operating expenses',
                        'total operating expenses': 'operating expenses total', 'net income loss': 'net income',
                        'net income': 'net income', 'income from operations': 'operating income',
                        'income loss from operations': 'operating income', 'cash end of the period': 'ending cash',
                        'cash end of period': 'ending cash', 'cash beginning of the period': 'beginning cash',
                        'cash at beginning of year': 'beginning cash', 'cash at end of period': 'ending cash',
                        'total assets': 'total assets', 'total current assets': 'total current assets',
                        'total liabilities': 'total liabilities', 'total current liabilities': 'total current liabilities',
                        'total shareholder s equity': 'total equity', 'total shareholders equity': 'total equity',
                        'total liabilities and shareholder equity': 'total liabilities and equity'
                    }
                    return synonyms.get(l, l)

                def ensure_income_period(year: str):
                    if year not in multi_data['income_statement']['periods']:
                        multi_data['income_statement']['periods'][year] = {
                            'revenue': {}, 'expenses': {}, 'gross_profit': 0.0,
                            'operating_income': 0.0, 'net_income': 0.0
                        }

                def ensure_bs_period(year: str):
                    if year not in multi_data['balance_sheet']['periods']:
                        multi_data['balance_sheet']['periods'][year] = {
                            'assets': {}, 'liabilities': {}, 'equity': {}
                        }

                def ensure_cf_period(year: str):
                    if year not in multi_data['cash_flow_statement']['periods']:
                        multi_data['cash_flow_statement']['periods'][year] = {
                            'operating': {}, 'investing': {}, 'financing': {},
                            'net_change': 0.0, 'beginning_cash': 0.0, 'ending_cash': 0.0
                        }

                year_pattern = re.compile(r'20\d{2}')

                for table in tables:
                    total_tables += 1
                    # Manual row extraction to capture hidden/spanned text
                    raw_rows = []
                    for tr in table.find_all('tr'):
                        cells = [c.get_text(strip=True) for c in tr.find_all(['th','td'])]
                        # Skip empty rows
                        if any(cells) and len(cells) > 0:
                            raw_rows.append(cells)
                    if not raw_rows:
                        continue
                    # Build preliminary DF from manual rows (pad uneven lengths)
                    max_len = max(len(r) for r in raw_rows)
                    padded_rows = [r + ['']*(max_len-len(r)) for r in raw_rows]
                    df_manual = pd.DataFrame(padded_rows)

                    # Try pandas read_html for structured version as secondary source
                    try:
                        df_list = pd.read_html(StringIO(str(table)))
                    except Exception:
                        df_list = [df_manual]

                    # Choose the largest non-empty df variant
                    base_df = max([d for d in df_list if not d.empty] + [df_manual], key=lambda d: (len(d.columns), len(d)))
                    # Clean: drop all-empty cols/rows
                    base_df = base_df.dropna(how='all').dropna(how='all', axis=1)
                    if base_df.empty:
                        continue

                    # Heuristics: count keyword hits & numeric cells
                    text_sample = ' '.join(base_df.astype(str).head(50).values.ravel()).lower()
                    keyword_hits = sum(1 for kw in financial_keywords if kw in text_sample)
                    # Numeric cell detection (digits, parentheses for negatives)
                    numeric_cells = 0
                    for val in base_df.values.ravel():
                        if val is None:
                            continue
                        sval = str(val).strip()
                        if sval in {'$','-'}:
                            continue
                        if re.search(r'[0-9]', sval):
                            numeric_cells += 1

                    # Decide keep: require at least 3 keywords and 3 numeric cells OR table contains section anchors
                    keep = (keyword_hits >= 3 and numeric_cells >= 3) or ('balance sheet' in text_sample or 'cash flows' in text_sample or 'income' in text_sample)

                    if not keep:
                        continue

                    kept_tables += 1

                    # Attempt label-value pairing improvement: if a row has pattern [label,'$',number] collapse
                    enhanced_rows = []
                    for row in base_df.values.tolist():
                        # Normalize row length
                        r = [str(x).strip() for x in row]
                        if len(r) >= 3 and r[1] == '$' and re.search(r'[0-9]', r[2]):
                            enhanced_rows.append([r[0], r[2]])
                        else:
                            enhanced_rows.append(r)
                    df_out = pd.DataFrame(enhanced_rows)
                    csv_str = df_out.to_csv(index=False, header=False)
                    filtered_csv.append(csv_str)

                    # Attempt to extract semantic label->amount pairs for P&L style parsing
                    for row_vals in df_out.values.tolist():
                        # Separate numeric vs text cells
                        texts = []
                        numbers = []
                        for cell in row_vals:
                            cell_str = str(cell).strip()
                            if not cell_str:
                                continue
                            # Detect numeric tokens (including parentheses negatives, dashes representing zero, em dash)
                            numeric_match = re.fullmatch(r"[\(\)-]*\$?[0-9,]+(\.[0-9]+)?|\([0-9,]+\)|\$?[0-9]+|\([0-9]+\)|\$?[0-9,]+", cell_str.replace('—','').replace('–','-'))
                            if numeric_match or re.search(r"[0-9]", cell_str):
                                # Filter out pure year labels (e.g., 2023, 2024) unless accompanied by keyword in same row
                                if re.fullmatch(r"20[0-9]{2}", cell_str) and not any(kw in ' '.join(row_vals).lower() for kw in ['revenue','income','expense','profit','assets','liabilities','cash']):
                                    continue
                                numbers.append(cell_str)
                            else:
                                texts.append(cell_str)
                        if not numbers or not texts:
                            continue
                        label = texts[0].lower()
                        # Basic label filtering to avoid generic years or section headers
                        if any(skip in label for skip in ['year ended','years ended','fiscal year','december','consolidated','unaudited','see accompanying','balance sheets','statement','statements','cash flows']):
                            continue
                        # Choose the first numeric value that looks like an amount (exclude short like '400' only if multiple present; keep all for now)
                        amount_raw = numbers[0]
                        amount_clean = self._parse_amount(amount_raw)
                        if amount_clean == 0:
                            # Try next numeric token if first parsed to zero (maybe formatting)
                            for nxt in numbers[1:]:
                                amount_clean = self._parse_amount(nxt)
                                if amount_clean != 0:
                                    amount_raw = nxt
                                    break
                        if amount_clean == 0:
                            continue
                        # Reconstruct original label (strip excessive spaces)
                        structured_lines.append(f"{label.replace(',', ' ').strip()},{amount_raw}")

                    # Attempt multi-period extraction: detect header with multiple distinct years
                    # Convert df_out to list of rows again for period mapping
                    rows_all = [ [str(c).strip() for c in r] for r in df_out.values.tolist() ]
                    candidate_year_rows = [r for r in rows_all if sum(1 for c in r if year_pattern.fullmatch(c)) >= 2]
                    periods = []
                    if candidate_year_rows:
                        # Use the first candidate as period header
                        header_row = candidate_year_rows[0]
                        periods = [c for c in header_row if year_pattern.fullmatch(c)]
                        periods = list(dict.fromkeys(periods))  # preserve order, deduplicate
                    if periods:
                        # Iterate rows to map label -> amounts per period (aligning by index after first label cell)
                        for r in rows_all:
                            # skip header row
                            if r == header_row:
                                continue
                            if not r or all(not cell for cell in r):
                                continue
                            label_cell = r[0].strip()
                            if year_pattern.fullmatch(label_cell):
                                # rows starting with a year are likely transposed; skip
                                continue
                            # Count numeric cells among remaining
                            numeric_cells = [c for c in r[1:1+len(periods)] if re.search(r'[0-9]', c)]
                            if len(numeric_cells) == 0:
                                continue
                            canon = canonical_label(label_cell)
                            # Map amounts per year
                            for idx, yr in enumerate(periods):
                                if idx+1 >= len(r):
                                    continue
                                raw_amt = r[idx+1]
                                amt = self._parse_amount(raw_amt)
                                if amt == 0.0 and not re.search(r'[0-9]', raw_amt):
                                    continue
                                # Classification heuristics
                                lower_label = canon
                                if any(k in lower_label for k in ['revenue','sales']):
                                    ensure_income_period(yr)
                                    if canon not in multi_data['income_statement']['periods'][yr]['revenue']:
                                        multi_data['income_statement']['periods'][yr]['revenue'][canon] = amt
                                elif any(k in lower_label for k in ['cost of goods','cost of revenues','expense','expenses','depreciation','amortization','marketing','administrative']):
                                    ensure_income_period(yr)
                                    if canon not in multi_data['income_statement']['periods'][yr]['expenses']:
                                        multi_data['income_statement']['periods'][yr]['expenses'][canon] = amt
                                elif 'gross profit' in lower_label:
                                    ensure_income_period(yr)
                                    multi_data['income_statement']['periods'][yr]['gross_profit'] = amt
                                elif 'operating income' in lower_label or 'operating profit' in lower_label:
                                    ensure_income_period(yr)
                                    multi_data['income_statement']['periods'][yr]['operating_income'] = amt
                                elif 'net income' in lower_label or 'net loss' in lower_label:
                                    ensure_income_period(yr)
                                    multi_data['income_statement']['periods'][yr]['net_income'] = amt
                                elif any(k in lower_label for k in ['total assets','current assets','assets']) and not any(k in lower_label for k in ['liabilities']):
                                    ensure_bs_period(yr)
                                    multi_data['balance_sheet']['periods'][yr]['assets'][canon] = amt
                                elif any(k in lower_label for k in ['liabilities','payables']):
                                    ensure_bs_period(yr)
                                    multi_data['balance_sheet']['periods'][yr]['liabilities'][canon] = amt
                                elif any(k in lower_label for k in ['equity','shareholder']):
                                    ensure_bs_period(yr)
                                    multi_data['balance_sheet']['periods'][yr]['equity'][canon] = amt
                                elif any(k in lower_label for k in ['net cash provided','net cash used','net cash', 'beginning cash','ending cash','cash at end','cash at beginning']):
                                    ensure_cf_period(yr)
                                    if 'net cash' in lower_label and ('provided' in lower_label or 'used' in lower_label):
                                        multi_data['cash_flow_statement']['periods'][yr]['operating'][canon] = amt
                                    elif 'beginning' in lower_label:
                                        multi_data['cash_flow_statement']['periods'][yr]['beginning_cash'] = amt
                                    elif 'ending' in lower_label or 'end of' in lower_label or 'cash at end' in lower_label:
                                        multi_data['cash_flow_statement']['periods'][yr]['ending_cash'] = amt
                                    elif 'net cash' in lower_label and 'increase' in lower_label or 'decrease' in lower_label:
                                        multi_data['cash_flow_statement']['periods'][yr]['net_change'] = amt
                                    else:
                                        # Fallback categorize as operating if unsure
                                        multi_data['cash_flow_statement']['periods'][yr]['operating'][canon] = amt

                # Fallback: if filtering removed everything, include first 5 tables raw
                if not filtered_csv:
                    logger.warning("HTML filtering yielded no financial tables; falling back to raw concatenation.")
                    fallback_csv = []
                    for table in tables[:5]:
                        try:
                            df_list = pd.read_html(StringIO(str(table)))
                            for df in df_list:
                                df = df.dropna(how='all').dropna(how='all', axis=1)
                                if df.empty:
                                    continue
                                fallback_csv.append(df.to_csv(index=False))
                        except Exception:
                            continue
                    filtered_csv = fallback_csv

                # If we successfully extracted structured lines (more than header), prepend them as a synthetic CSV block
                if len(structured_lines) > 1:
                    filtered_csv.insert(0, '\n'.join(structured_lines))

                decoded_content = '\n\n'.join(filtered_csv)
                logger.info(f"HTML tables processed: total={total_tables}, kept={kept_tables}")
                # Compute metrics for multi-period income statement if populated
                if any(multi_data['income_statement']['periods']):
                    for yr, pdata in multi_data['income_statement']['periods'].items():
                        total_rev = sum(pdata['revenue'].values())
                        total_exp = sum(pdata['expenses'].values())
                        if pdata['gross_profit'] == 0 and total_rev > 0:
                            pdata['gross_profit'] = total_rev - total_exp
                        if pdata['net_income'] == 0 and total_rev > 0:
                            # Approximate net income if not provided using gross - expenses (double subtract expenses already in gross?) -> fallback to gross_profit - total_expenses only if gross was derived.
                            derived_gross = pdata['gross_profit']
                            # If gross was derived, don't subtract expenses twice.
                            pdata['net_income'] = derived_gross if (derived_gross == total_rev - total_exp) else derived_gross - total_exp
                        multi_data['income_statement']['metrics'][yr] = {
                            'total_revenue': total_rev,
                            'total_expenses': total_exp,
                            'gross_profit_margin': (pdata['gross_profit']/total_rev*100) if total_rev>0 else 0,
                            'net_profit_margin': (pdata['net_income']/total_rev*100) if total_rev>0 else 0,
                            'expense_ratio': (total_exp/total_rev*100) if total_rev>0 else 0,
                            'profitable': pdata['net_income'] > 0
                        }
                    # Revenue fallback & dedup pass
                    for yr, pdata in multi_data['income_statement']['periods'].items():
                        metrics = multi_data['income_statement']['metrics'][yr]
                        # Derive revenue if zero but have cost of goods + gross profit
                        if metrics['total_revenue'] == 0:
                            cost_of_goods_total = sum(v for k,v in pdata['expenses'].items() if 'cost of goods sold' in k or 'cost of goods' in k or 'cost of revenues' in k)
                            if pdata['gross_profit'] > 0 and cost_of_goods_total > 0:
                                derived_rev = pdata['gross_profit'] + cost_of_goods_total
                                metrics['total_revenue'] = derived_rev
                                # Recompute margins
                                metrics['gross_profit_margin'] = (pdata['gross_profit']/derived_rev*100) if derived_rev>0 else 0
                                metrics['net_profit_margin'] = (pdata['net_income']/derived_rev*100) if derived_rev>0 else 0
                                metrics['expense_ratio'] = (metrics['total_expenses']/derived_rev*100) if derived_rev>0 else 0
                        # Deduplicate synonymous revenue labels keeping max
                        rev_groups = {}
                        for label, amount in pdata['revenue'].items():
                            base = canonical_label(label)
                            if base not in rev_groups or amount > rev_groups[base]:
                                rev_groups[base] = amount
                        pdata['revenue'] = rev_groups
                        # Recalc revenue total after dedup
                        metrics['total_revenue'] = sum(pdata['revenue'].values()) or metrics['total_revenue']
                        # Deduplicate expenses similarly
                        exp_groups = {}
                        for label, amount in pdata['expenses'].items():
                            base = canonical_label(label)
                            if base not in exp_groups or amount > exp_groups[base]:
                                exp_groups[base] = amount
                        pdata['expenses'] = exp_groups
                        metrics['total_expenses'] = sum(pdata['expenses'].values()) or metrics['total_expenses']
                        # Recompute margins after dedup if revenue >0
                        if metrics['total_revenue'] > 0:
                            pdata['gross_profit'] = pdata['gross_profit'] if pdata['gross_profit'] else metrics['total_revenue'] - metrics['total_expenses']
                            metrics['gross_profit_margin'] = (pdata['gross_profit']/metrics['total_revenue']*100)
                            metrics['net_profit_margin'] = (pdata['net_income']/metrics['total_revenue']*100) if pdata['net_income'] else 0
                            metrics['expense_ratio'] = (metrics['total_expenses']/metrics['total_revenue']*100)
                            metrics['profitable'] = pdata['net_income'] > 0
                    # Balance sheet metrics
                    for yr, bdata in multi_data['balance_sheet']['periods'].items():
                        assets_total = 0.0
                        liabilities_total = 0.0
                        equity_total = 0.0
                        for k,v in bdata['assets'].items():
                            assets_total += v
                        for k,v in bdata['liabilities'].items():
                            liabilities_total += v
                        for k,v in bdata['equity'].items():
                            equity_total += v
                        current_assets = sum(v for k,v in bdata['assets'].items() if any(t in k for t in ['cash','receivable','contract receivables','contract assets','prepaid']))
                        current_liabilities = sum(v for k,v in bdata['liabilities'].items() if any(t in k for t in ['accounts payable','accrued','contract liabilities','payables']))
                        multi_data['balance_sheet']['metrics'][yr] = {
                            'total_assets': assets_total,
                            'total_liabilities': liabilities_total,
                            'total_equity': equity_total,
                            'current_ratio': (current_assets/current_liabilities) if current_liabilities>0 else 0,
                            'debt_to_equity': (liabilities_total/equity_total) if equity_total>0 else 0,
                            'equity_ratio': (equity_total/assets_total*100) if assets_total>0 else 0,
                            'working_capital': current_assets - current_liabilities
                        }
                    # Cash flow metrics
                    for yr, cfdata in multi_data['cash_flow_statement']['periods'].items():
                        net_change = cfdata['net_change'] if cfdata['net_change'] else (cfdata['ending_cash'] - cfdata['beginning_cash'] if cfdata['ending_cash'] and cfdata['beginning_cash'] else 0.0)
                        operating_total = sum(cfdata['operating'].values())
                        multi_data['cash_flow_statement']['metrics'][yr] = {
                            'operating_cash_flow': operating_total,
                            'net_change': net_change,
                            'cash_conversion': (operating_total / operating_total) if operating_total>0 else 0,  # placeholder, refine later
                            'ending_cash': cfdata['ending_cash'],
                            'beginning_cash': cfdata['beginning_cash']
                        }
                    # Period type detection (simple heuristic)
                    period_type_map = {}
                    for table in tables:
                        snippet = table.get_text(" ", strip=True).lower()
                        for yr in multi_data['income_statement']['periods'].keys():
                            if yr in snippet:
                                if 'year ended' in snippet or 'years ended' in snippet:
                                    period_type_map[yr] = 'annual'
                                elif 'as of' in snippet:
                                    period_type_map[yr] = 'point-in-time'
                    # Assign period types defaulting to annual
                    for yr in multi_data['income_statement']['periods'].keys():
                        multi_data['income_statement']['periods'][yr]['period_type'] = period_type_map.get(yr,'annual')
                # Return early if multi-period data is meaningful
                if any(multi_data['income_statement']['periods']):
                    return 'multi_financials', multi_data
            else:
                decoded_content = file_content.decode('utf-8')
            
            doc_type = self.detect_document_type(decoded_content)
            if doc_type == 'profit_loss':
                return 'profit_loss', self.parse_profit_loss(decoded_content)
            elif doc_type == 'balance_sheet':
                return 'balance_sheet', self.parse_balance_sheet(decoded_content)
            elif doc_type == 'pink_slip':
                return 'pink_slip', self.parse_pink_slip(decoded_content)
            elif 'symbol' in decoded_content.lower() and 'quantity' in decoded_content.lower():
                # Fallback to portfolio parsing
                return 'portfolio', self.parse_portfolio(decoded_content)
            else:
                raise ValueError("Could not determine document type")
        except Exception as e:
            logger.error(f"Error parsing file: {str(e)}")
            raise
    
    def parse_profit_loss(self, content: str) -> Dict[str, Any]:
        """
        Parse Profit & Loss Statement
        Expected format:
        - Category, Amount (or)
        - Revenue, ..., Expenses, ..., Net Income
        """
        csv_reader = csv.DictReader(io.StringIO(content))
        rows = list(csv_reader)

        def _norm_key(k: Any) -> str:
            if k is None:
                return ''
            return str(k).lower().strip()
        def _norm_val(v: Any) -> str:
            if v is None:
                return ''
            return str(v).strip()

        # Normalize keys/values safely
        rows_normalized = [{_norm_key(k): _norm_val(v) for k, v in row.items() if k is not None} for row in rows]
        
        pl_data = {
            'revenue': {},
            'expenses': {},
            'gross_profit': 0,
            'operating_income': 0,
            'net_income': 0,
            'period': None,
            'raw_data': rows_normalized
        }
        
        # Try to extract standard P&L items
        for row in rows_normalized:
            category = row.get('category', row.get('item', row.get('account', '')))
            amount_str = row.get('amount', row.get('value', row.get('total', '0')))
            
            # Clean amount string
            amount = self._parse_amount(amount_str)
            
            category_lower = category.lower()
            
            # Classify items
            if 'revenue' in category_lower or 'sales' in category_lower or 'income' in category_lower:
                if 'net' not in category_lower and 'operating' not in category_lower:
                    pl_data['revenue'][category] = amount
            elif any(exp in category_lower for exp in ['expense', 'cost', 'depreciation', 'amortization']):
                pl_data['expenses'][category] = amount
            elif 'gross profit' in category_lower:
                pl_data['gross_profit'] = amount
            elif 'operating income' in category_lower or 'ebit' in category_lower:
                pl_data['operating_income'] = amount
            elif 'net income' in category_lower or 'net profit' in category_lower:
                pl_data['net_income'] = amount
            elif 'period' in category_lower or 'date' in category_lower:
                pl_data['period'] = amount_str
        
        # Calculate totals if not provided
        total_revenue = sum(pl_data['revenue'].values())
        total_expenses = sum(pl_data['expenses'].values())
        
        if pl_data['gross_profit'] == 0 and total_revenue > 0:
            pl_data['gross_profit'] = total_revenue - total_expenses
        
        if pl_data['net_income'] == 0:
            pl_data['net_income'] = pl_data['gross_profit'] - total_expenses
        
        # Calculate metrics
        pl_data['metrics'] = self._calculate_pl_metrics(pl_data)
        
        return pl_data
    
    def parse_balance_sheet(self, content: str) -> Dict[str, Any]:
        """
        Parse Balance Sheet
        Expected format:
        - Account, Amount (or)
        - Assets, ..., Liabilities, ..., Equity
        """
        csv_reader = csv.DictReader(io.StringIO(content))
        rows = list(csv_reader)

        def _norm_key(k: Any) -> str:
            if k is None:
                return ''
            return str(k).lower().strip()
        def _norm_val(v: Any) -> str:
            if v is None:
                return ''
            return str(v).strip()

        rows_normalized = [{_norm_key(k): _norm_val(v) for k, v in row.items() if k is not None} for row in rows]
        
        bs_data = {
            'assets': {
                'current': {},
                'non_current': {},
                'total': 0
            },
            'liabilities': {
                'current': {},
                'long_term': {},
                'total': 0
            },
            'equity': {},
            'date': None,
            'raw_data': rows_normalized
        }
        
        current_section = None
        
        for row in rows_normalized:
            account = row.get('account', row.get('item', row.get('category', '')))
            amount_str = row.get('amount', row.get('value', row.get('balance', '0')))
            
            amount = self._parse_amount(amount_str)
            account_lower = account.lower()
            
            # Detect sections
            if 'asset' in account_lower and 'total' not in account_lower:
                current_section = 'assets'
                if 'current' in account_lower:
                    current_section = 'current_assets'
                continue
            elif 'liabilit' in account_lower and 'total' not in account_lower:
                current_section = 'liabilities'
                if 'current' in account_lower:
                    current_section = 'current_liabilities'
                continue
            elif 'equity' in account_lower and 'total' not in account_lower:
                current_section = 'equity'
                continue
            
            # Classify items
            if 'total assets' in account_lower:
                bs_data['assets']['total'] = amount
            elif 'total liabilities' in account_lower:
                bs_data['liabilities']['total'] = amount
            elif current_section == 'current_assets' or (current_section == 'assets' and any(kw in account_lower for kw in ['cash', 'receivable', 'inventory'])):
                bs_data['assets']['current'][account] = amount
            elif current_section == 'assets':
                bs_data['assets']['non_current'][account] = amount
            elif current_section == 'current_liabilities' or (current_section == 'liabilities' and any(kw in account_lower for kw in ['payable', 'accrued'])):
                bs_data['liabilities']['current'][account] = amount
            elif current_section == 'liabilities':
                bs_data['liabilities']['long_term'][account] = amount
            elif current_section == 'equity' or 'equity' in account_lower:
                bs_data['equity'][account] = amount
            elif 'date' in account_lower or 'as of' in account_lower:
                bs_data['date'] = amount_str
        
        # Calculate totals if not provided
        if bs_data['assets']['total'] == 0:
            bs_data['assets']['total'] = sum(bs_data['assets']['current'].values()) + sum(bs_data['assets']['non_current'].values())
        
        if bs_data['liabilities']['total'] == 0:
            bs_data['liabilities']['total'] = sum(bs_data['liabilities']['current'].values()) + sum(bs_data['liabilities']['long_term'].values())
        
        total_equity = sum(bs_data['equity'].values())
        
        # Calculate metrics
        bs_data['metrics'] = self._calculate_bs_metrics(bs_data)
        
        return bs_data
    
    def parse_pink_slip(self, content: str) -> Dict[str, Any]:
        """
        Parse Pink Slip / Trade Confirmation
        Expected format:
        - Symbol, Shares, Price, Commission, Date, Type (Buy/Sell)
        """
        csv_reader = csv.DictReader(io.StringIO(content))
        rows = list(csv_reader)

        def _norm_key(k: Any) -> str:
            if k is None:
                return ''
            return str(k).lower().strip()
        def _norm_val(v: Any) -> str:
            if v is None:
                return ''
            return str(v).strip()

        rows_normalized = [{_norm_key(k): _norm_val(v) for k, v in row.items() if k is not None} for row in rows]
        
        trades = []
        
        for row in rows_normalized:
            trade = {
                'symbol': row.get('symbol', row.get('ticker', '')).upper(),
                'shares': float(row.get('shares', row.get('quantity', row.get('qty', 0)))),
                'price': self._parse_amount(row.get('price', row.get('execution_price', '0'))),
                'commission': self._parse_amount(row.get('commission', row.get('fee', '0'))),
                'date': row.get('date', row.get('trade_date', row.get('execution_date', ''))),
                'type': row.get('type', row.get('action', 'buy')).lower(),
                'total_value': 0
            }
            
            # Calculate total value
            trade['total_value'] = trade['shares'] * trade['price'] + trade['commission']
            
            # Determine if buy or sell
            if trade['type'] in ['sell', 'sale', 'sold']:
                trade['type'] = 'sell'
                trade['total_value'] = -trade['total_value']
            else:
                trade['type'] = 'buy'
            
            trades.append(trade)
        
        # Aggregate by symbol
        portfolio_summary = self._aggregate_trades(trades)
        
        return {
            'trades': trades,
            'portfolio_summary': portfolio_summary,
            'total_invested': sum(t['total_value'] for t in trades if t['type'] == 'buy'),
            'total_proceeds': abs(sum(t['total_value'] for t in trades if t['type'] == 'sell')),
            'net_position_value': sum(p['total_value'] for p in portfolio_summary.values())
        }
    
    def parse_portfolio(self, content: str) -> List[Dict[str, Any]]:
        """Parse simple portfolio CSV (Symbol, Quantity, Cost Basis)"""
        csv_reader = csv.DictReader(io.StringIO(content))
        
        portfolio_items = []
        for row in csv_reader:
            row_lower = {k.lower(): v for k, v in row.items()}
            if 'symbol' in row_lower:
                portfolio_items.append({
                    "symbol": row_lower['symbol'].strip().upper(),
                    "quantity": float(row_lower.get('quantity', 0)),
                    "cost_basis": self._parse_amount(row_lower.get('costbasis', row_lower.get('cost basis', '0')))
                })
        
        return portfolio_items
    
    def _parse_amount(self, amount_str: str) -> float:
        """Parse currency/number string to float"""
        if not amount_str or amount_str == '':
            return 0.0
        
        # Remove currency symbols, commas, spaces
        cleaned = re.sub(r'[$,€£¥\s]', '', str(amount_str))

        # Treat common placeholder tokens as zero
        if cleaned.lower() in {'nan', 'n/a', 'na', '-', '—', '--'}:
            return 0.0
        
        # Handle parentheses for negative numbers
        if '(' in cleaned and ')' in cleaned:
            cleaned = '-' + cleaned.replace('(', '').replace(')', '')
        
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
    
    def _aggregate_trades(self, trades: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        """Aggregate trades by symbol to get current positions"""
        positions = {}
        
        for trade in trades:
            symbol = trade['symbol']
            
            if symbol not in positions:
                positions[symbol] = {
                    'symbol': symbol,
                    'shares': 0,
                    'total_cost': 0,
                    'avg_price': 0,
                    'total_value': 0
                }
            
            if trade['type'] == 'buy':
                positions[symbol]['shares'] += trade['shares']
                positions[symbol]['total_cost'] += trade['total_value']
            else:  # sell
                positions[symbol]['shares'] -= trade['shares']
                positions[symbol]['total_cost'] -= abs(trade['total_value'])
            
            # Calculate average price
            if positions[symbol]['shares'] > 0:
                positions[symbol]['avg_price'] = positions[symbol]['total_cost'] / positions[symbol]['shares']
                positions[symbol]['total_value'] = positions[symbol]['total_cost']
        
        # Remove closed positions (shares = 0)
        positions = {k: v for k, v in positions.items() if v['shares'] != 0}
        
        return positions
    
    def _calculate_pl_metrics(self, pl_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate profit & loss metrics"""
        # Replace NaN values with zero before aggregation
        rev_values = [0.0 if (isinstance(v, float) and math.isnan(v)) else v for v in pl_data['revenue'].values()]
        exp_values = [0.0 if (isinstance(v, float) and math.isnan(v)) else v for v in pl_data['expenses'].values()]
        total_revenue = sum(rev_values)
        total_expenses = sum(exp_values)
        gross_profit = pl_data.get('gross_profit', 0.0)
        if isinstance(gross_profit, float) and math.isnan(gross_profit):
            gross_profit = total_revenue - total_expenses if total_revenue > 0 else 0.0
        net_income = pl_data.get('net_income', 0.0)
        if isinstance(net_income, float) and math.isnan(net_income):
            net_income = gross_profit - total_expenses if total_revenue > 0 else 0.0
        operating_income = pl_data.get('operating_income', 0.0)
        if isinstance(operating_income, float) and math.isnan(operating_income):
            operating_income = net_income  # fallback
        
        metrics = {
            'total_revenue': total_revenue,
            'total_expenses': total_expenses,
            'gross_profit_margin': (gross_profit / total_revenue * 100) if total_revenue > 0 else 0,
            'net_profit_margin': (net_income / total_revenue * 100) if total_revenue > 0 else 0,
            'operating_margin': (operating_income / total_revenue * 100) if total_revenue > 0 else 0,
            'profitability': 'profitable' if net_income > 0 else 'unprofitable',
            'expense_ratio': (total_expenses / total_revenue * 100) if total_revenue > 0 else 0
        }
        
        return metrics
    
    def _calculate_bs_metrics(self, bs_data: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate balance sheet metrics"""
        current_assets = sum(bs_data['assets']['current'].values())
        current_liabilities = sum(bs_data['liabilities']['current'].values())
        total_assets = bs_data['assets']['total']
        total_liabilities = bs_data['liabilities']['total']
        total_equity = sum(bs_data['equity'].values())
        
        metrics = {
            'current_ratio': (current_assets / current_liabilities) if current_liabilities > 0 else 0,
            'quick_ratio': ((current_assets - bs_data['assets']['current'].get('Inventory', 0)) / current_liabilities) if current_liabilities > 0 else 0,
            'debt_to_equity': (total_liabilities / total_equity) if total_equity > 0 else 0,
            'debt_to_assets': (total_liabilities / total_assets) if total_assets > 0 else 0,
            'equity_ratio': (total_equity / total_assets * 100) if total_assets > 0 else 0,
            'working_capital': current_assets - current_liabilities,
            'financial_health': 'strong' if (current_assets / current_liabilities if current_liabilities > 0 else 0) > 1.5 else 'moderate' if (current_assets / current_liabilities if current_liabilities > 0 else 0) > 1 else 'weak'
        }
        
        return metrics


# Initialize parser
document_parser = FinancialDocumentParser()
