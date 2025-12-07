import sys
from app.services.document_parser_service import document_parser

def summarize_multi_financials(data: dict):
    inc = data.get('income_statement', {})
    bs = data.get('balance_sheet', {})
    cf = data.get('cash_flow_statement', {})
    periods = inc.get('periods', {})
    inc_metrics = inc.get('metrics', {})
    bs_metrics = bs.get('metrics', {})
    cf_metrics = cf.get('metrics', {})
    lines = []
    for yr in sorted(periods.keys()):
        im = inc_metrics.get(yr, {})
        bm = bs_metrics.get(yr, {})
        cm = cf_metrics.get(yr, {})
        ptype = periods[yr].get('period_type','annual')
        lines.append(
            f"Year {yr} ({ptype}): Rev={im.get('total_revenue',0):,.0f} Exp={im.get('total_expenses',0):,.0f} "
            f"GP%={im.get('gross_profit_margin',0):.1f} NM%={im.get('net_profit_margin',0):.1f} "
            f"CR={bm.get('current_ratio',0):.2f} D/E={bm.get('debt_to_equity',0):.2f} EQ%={bm.get('equity_ratio',0):.1f} "
            f"OpCF={cm.get('operating_cash_flow',0):,.0f} NetCashChg={cm.get('net_change',0):,.0f}"
        )
    return "\n".join(lines)

if __name__ == "__main__":
    with open("test-edgar-10k.html", "rb") as f:
        file_content = f.read()
    try:
        doc_type, parsed = document_parser.parse_csv(file_content, filename="test-edgar-10k.html")
        print(f"Document type detected: {doc_type}\n")
        if doc_type == 'multi_financials':
            print("Multi-period financial summary:\n")
            print(summarize_multi_financials(parsed))
            # Basic assertions for sanity
            inc_periods = parsed['income_statement']['periods']
            assert len(inc_periods) >= 1, "Expected at least one income statement period"
            # At least one period should have non-zero revenue (after fallback)
            assert any(parsed['income_statement']['metrics'][yr]['total_revenue'] > 0 for yr in inc_periods.keys()), "No revenue detected in any period"
            # If more than one period, ensure at least one has expenses > 0
            if len(inc_periods) > 1:
                assert any(parsed['income_statement']['metrics'][yr]['total_expenses'] > 0 for yr in inc_periods.keys()), "No expenses detected across periods"
        else:
            print("Parsed data (truncated):\n")
            import pprint
            pprint.pprint(parsed if isinstance(parsed, dict) else parsed[:5])
    except Exception as e:
        print(f"Error parsing file: {e}", file=sys.stderr)
        sys.exit(1)
