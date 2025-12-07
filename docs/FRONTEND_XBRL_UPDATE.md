# Frontend XBRL/SEC EDGAR Support Update

## Summary
Updated the mobile frontend to support the new SEC EDGAR file format parsing capabilities added to the backend. Users can now upload XBRL, HTML, JSON, and text files from SEC EDGAR in addition to traditional CSV and Excel formats.

## Changes Made

### 1. CompanyScreeningScreen.tsx (`mobile/src/screens/CompanyScreeningScreen.tsx`)

#### File Picker Updates (Lines 29-71)
**Added MIME types for SEC formats:**
- `text/xml` - XML files
- `application/xml` - XBRL files
- `text/html` - HTML SEC filings
- `application/json` - JSON SEC data
- `text/plain` - Text filings

**Added file extension validation:**
- `.xml` - SEC XML filings
- `.xbrl` - XBRL financial data
- `.htm` - HTML SEC reports
- `.html` - HTML SEC reports
- `.txt` - Text-based filings
- `.json` - JSON formatted SEC data

#### UI Text Updates

**Header Subtitle (Line 138):**
```tsx
// Before
Upload a CSV or Excel file with company tickers

// After
Upload CSV, Excel, or SEC EDGAR filings (XBRL)
```

**File Picker Button (Line 224):**
```tsx
// Before
Select CSV/Excel File

// After
Select File (CSV/Excel/XBRL)
```

**Format Guide Section (Lines 171-210):**
Added comprehensive multi-format guide:
- **Traditional Formats** section showing CSV/Excel usage
- **SEC EDGAR Formats** section with NEW badge showing:
  - XBRL (.xml, .xbrl) - SEC's standard financial format
  - HTML (.htm, .html) - 10-K, 10-Q reports
  - JSON (.json) - SEC API format
  - Text (.txt) - Plain text filings
  - Download link: sec.gov/edgar
- **Example CSV** - Original CSV format example
- **Example XBRL** - New XBRL structure example

**Sample Files Tip (Lines 260-266):**
```tsx
// Before
Use sample files from the repository root to test:
• sample-portfolio.csv
• sample-balance-sheet.csv
• sample-profit-loss.csv

// After
Test with sample files from the repository:
• sample-portfolio.csv (Traditional format)
• test_xbrl_sample.xml (XBRL format)
Or download 10-K/10-Q from sec.gov/edgar
```

#### Styles Updates (Lines 384-390)
**Added new style:**
```tsx
formatSubtitle: {
  fontSize: 14,
  fontWeight: 'bold',
  color: '#2196F3',
  marginTop: 12,
  marginBottom: 6,
}
```

### 2. screeningApi.ts (`mobile/src/services/screeningApi.ts`)

#### MIME Type Detection (Lines 102-119)
**Enhanced file type detection:**
```typescript
// Before
let mimeType = 'text/csv';
if (fileName.endsWith('.xlsx')) {
  mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
} else if (fileName.endsWith('.xls')) {
  mimeType = 'application/vnd.ms-excel';
}

// After
let mimeType = 'text/csv';
if (fileName.endsWith('.xlsx')) {
  mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
} else if (fileName.endsWith('.xls')) {
  mimeType = 'application/vnd.ms-excel';
} else if (fileName.endsWith('.xml') || fileName.endsWith('.xbrl')) {
  mimeType = 'application/xml';
} else if (fileName.endsWith('.htm') || fileName.endsWith('.html')) {
  mimeType = 'text/html';
} else if (fileName.endsWith('.json')) {
  mimeType = 'application/json';
} else if (fileName.endsWith('.txt')) {
  mimeType = 'text/plain';
}
```

## Supported File Formats

### Traditional Formats
| Extension | MIME Type | Description |
|-----------|-----------|-------------|
| `.csv` | `text/csv` | Comma-separated values |
| `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | Excel 2007+ |
| `.xls` | `application/vnd.ms-excel` | Excel 97-2003 |

### SEC EDGAR Formats (NEW)
| Extension | MIME Type | Description |
|-----------|-----------|-------------|
| `.xml` | `application/xml` | SEC XML filings |
| `.xbrl` | `application/xml` | XBRL financial data |
| `.htm` | `text/html` | HTML 10-K/10-Q reports |
| `.html` | `text/html` | HTML SEC filings |
| `.json` | `application/json` | SEC API JSON responses |
| `.txt` | `text/plain` | Plain text filings |

## User Experience Improvements

### 1. Clear Format Guidance
- Users now see organized format guide with emoji icons
- Traditional and SEC formats separated into distinct sections
- "NEW!" badge highlights recently added SEC EDGAR support
- Direct link to sec.gov/edgar for downloading filings

### 2. Format Examples
- **CSV Example**: Shows traditional ticker list format
- **XBRL Example**: Shows SEC filing structure with US-GAAP elements
- Both examples help users understand expected file structure

### 3. Better Error Messages
- File validation shows all supported formats in organized list
- Format-agnostic error messages ("Please select a file first")
- Clear indication of what formats are accepted

### 4. Test File References
- Points users to `test_xbrl_sample.xml` for XBRL testing
- Maintains reference to traditional CSV samples
- Provides sec.gov download instructions

## Testing Recommendations

### 1. File Picker Testing
Test file selection with each format:
```bash
# Traditional formats
- sample-portfolio.csv
- sample-balance-sheet.xlsx

# SEC EDGAR formats
- test_xbrl_sample.xml (Apple Inc. 10-K)
- Download 10-K from sec.gov/edgar
```

### 2. Upload Flow Testing
1. Open Company Screening screen
2. Tap "Select File (CSV/Excel/XBRL)" button
3. Verify file picker shows all MIME types
4. Select XBRL file (test_xbrl_sample.xml)
5. Verify file name displays with checkmark
6. Tap "Screen Companies" button
7. Verify backend parses XBRL correctly
8. Verify screening results display

### 3. Error Handling Testing
1. Try selecting unsupported file format (.pdf, .doc)
2. Verify error message shows supported formats
3. Try uploading corrupted XBRL file
4. Verify backend error message displayed

### 4. Visual Testing
1. Verify format guide displays properly on different screen sizes
2. Check emoji icons render correctly
3. Verify code blocks are readable
4. Test scrolling through long format guide

## Backend Integration

### API Endpoint
```
POST /api/insights/screen-companies
```

**Request:**
```typescript
FormData {
  file: {
    uri: string,
    type: string, // MIME type (now includes XML, HTML, JSON, text)
    name: string
  }
}
```

**Response:**
```typescript
{
  screening_results: {
    companies: Company[],
    summary: Summary
  }
}
```

### Data Flow
1. **Frontend**: User selects file → DocumentPicker validates extension
2. **Frontend**: screeningApi.ts determines MIME type based on extension
3. **Frontend**: FormData created with file and correct MIME type
4. **Backend**: insights.py receives file → routes to sec_edgar_parser for SEC formats
5. **Backend**: sec_edgar_parser.py detects filing type → extracts data
6. **Backend**: fundamental_analysis_service.py processes extracted data
7. **Backend**: Returns screening results with company analysis
8. **Frontend**: Displays results in ScreeningResults component

## Related Documentation
- `docs/EDGAR_XBRL_SUPPORT.md` - Backend XBRL implementation details
- `docs/SEC_EDGAR_IMPLEMENTATION_COMPLETE.md` - Implementation summary
- `backend/test_xbrl_sample.xml` - Sample XBRL file for testing
- `backend/test_xbrl_parser.py` - Backend parser test script

## Next Steps

### Recommended Enhancements
1. **Format Detection UI**
   - Show detected file type after selection
   - Display preview of parsed company info

2. **Download Helper**
   - Add button to open sec.gov/edgar in browser
   - Provide step-by-step SEC filing download guide

3. **File Validation Feedback**
   - Show parsing status indicator
   - Display number of companies detected before screening

4. **Format-Specific Instructions**
   - Expandable sections for each format type
   - Screenshots of where to find SEC filings
   - Common troubleshooting tips

### Future Features
1. **Direct SEC Integration**
   - Search companies by ticker within app
   - Download 10-K/10-Q directly from SEC API
   - Cache recently accessed filings

2. **Multi-File Upload**
   - Upload multiple SEC filings at once
   - Batch process companies from different sources
   - Compare data across filing periods

3. **Format Conversion**
   - Convert CSV to XBRL format
   - Export screening results as SEC-compatible JSON
   - Generate XBRL from manual inputs

## Verification Checklist

- [✅] File picker accepts all SEC EDGAR formats
- [✅] MIME type detection handles all extensions correctly
- [✅] Format guide shows traditional and SEC formats
- [✅] Examples provided for CSV and XBRL
- [✅] Button text updated to be format-agnostic
- [✅] Sample file references include XBRL
- [✅] Error messages updated for all formats
- [✅] Styles added for formatSubtitle
- [✅] No TypeScript compilation errors
- [ ] End-to-end testing with real XBRL files
- [ ] Visual testing on iOS and Android
- [ ] Performance testing with large XBRL files

## Notes

### Known Limitations
- File picker UI varies by platform (iOS/Android)
- Large XBRL files (>5MB) may take time to upload
- Internet connection required for sec.gov links
- Some older SEC filings may not be in XBRL format

### Platform Considerations
- **iOS**: Native file picker with all MIME types
- **Android**: May show "All files" or specific types
- **Web**: Browser file input with accept attribute

### Performance
- XBRL parsing handled on backend (no client-side overhead)
- FormData upload uses multipart/form-data
- No preprocessing required before upload

---

**Last Updated:** 2025-01-XX  
**Related PRs:** #XXX (Backend XBRL), #XXX (Frontend Update)  
**Status:** ✅ Ready for Testing
