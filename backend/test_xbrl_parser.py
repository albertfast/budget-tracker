"""
Test SEC EDGAR XBRL Parser
"""
from app.services.sec_edgar_parser import sec_edgar_parser
import json

# Read test XBRL file
with open('test_xbrl_sample.xml', 'rb') as f:
    content = f.read()

# Parse the file
result = sec_edgar_parser.parse_file(content, 'test_xbrl_sample.xml')

# Print results
print("=" * 80)
print("XBRL PARSING TEST RESULTS")
print("=" * 80)
print(f"\n✅ Parsing Status: {'SUCCESS' if result.get('parsed_successfully') else 'FAILED'}")
print(f"📄 File Type: {result.get('filing_type')}")
print(f"📁 Filename: {result.get('filename')}")

if result.get('parsed_successfully'):
    print("\n" + "=" * 80)
    print("COMPANY INFORMATION")
    print("=" * 80)
    company_info = result.get('company_info', {})
    for key, value in company_info.items():
        print(f"  {key}: {value}")
    
    print("\n" + "=" * 80)
    print("FINANCIAL DATA EXTRACTED")
    print("=" * 80)
    financials = result.get('financials', {})
    
    if financials.get('income_statement'):
        print("\n  📊 Income Statement:")
        for key, data in financials['income_statement'].items():
            print(f"    {key}: ${data['value']:,.0f}")
            print(f"      Element: {data['element']}, Context: {data['context']}")
    
    if financials.get('balance_sheet'):
        print("\n  📋 Balance Sheet:")
        for key, data in financials['balance_sheet'].items():
            print(f"    {key}: ${data['value']:,.0f}")
            print(f"      Element: {data['element']}, Context: {data['context']}")
    
    if financials.get('cash_flow'):
        print("\n  💰 Cash Flow:")
        for key, data in financials['cash_flow'].items():
            print(f"    {key}: ${data['value']:,.0f}")
            print(f"      Element: {data['element']}, Context: {data['context']}")
    
    print("\n" + "=" * 80)
    print("CONTEXTS")
    print("=" * 80)
    contexts = result.get('contexts', {})
    for ctx_id, ctx_data in contexts.items():
        print(f"  {ctx_id}:")
        for key, value in ctx_data.items():
            print(f"    {key}: {value}")
    
    print("\n" + "=" * 80)
    print("UNITS")
    print("=" * 80)
    units = result.get('units', {})
    for unit_id, unit_value in units.items():
        print(f"  {unit_id}: {unit_value}")

else:
    print(f"\n❌ Error: {result.get('error')}")

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
