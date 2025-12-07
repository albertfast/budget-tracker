# Company Screening Upload/Parse Fixes

## 🔧 Issues Found & Fixed

### Issue #1: ✅ Incorrect MIME Type Detection
**Problem**: Frontend always sent `type: 'text/csv'` regardless of actual file type, which could cause Excel files to fail parsing.

**Fix**: Added dynamic MIME type detection based on file extension:
```typescript
let mimeType = 'text/csv';
if (fileName.endsWith('.xlsx')) {
  mimeType = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet';
} else if (fileName.endsWith('.xls')) {
  mimeType = 'application/vnd.ms-excel';
}
```

**File**: `mobile/src/services/screeningApi.ts`

---

### Issue #2: ✅ Missing Required Python Dependencies
**Problem**: `pandas`, `openpyxl`, and `numpy` were not in `requirements.txt`, causing import errors when trying to parse files.

**Fix**: Added required packages:
```python
# Data Analysis & File Parsing
pandas==2.1.4
openpyxl==3.1.2  # Required for Excel files
numpy==1.26.2
```

**File**: `backend/requirements.txt`

**Action Required**: Run `pip install -r requirements.txt` in backend directory

---

### Issue #3: ✅ Poor Error Handling in Backend
**Problem**: Generic error messages didn't help diagnose file parsing issues.

**Fix**: Added comprehensive error handling:
- Empty file detection
- Parse error handling with specific messages
- DataFrame validation
- Separate handling for CSV vs Excel parsing
- ImportError handling for missing libraries
- Better logging

**File**: `backend/app/api/insights.py`

**Improvements**:
```python
# Now handles:
- Empty files → "File is empty or contains no data"
- Parse errors → "Failed to parse file: {error}. Please ensure file is properly formatted."
- Read errors → "Failed to read file: {error}. Ensure file is a valid CSV or Excel file."
- Empty DataFrame → "File contains no data rows"
- Missing libraries → "Server configuration error: required data analysis libraries not installed"
```

---

### Issue #4: ✅ Frontend Response Validation
**Problem**: No validation of server response structure, could crash on unexpected responses.

**Fix**: Added response validation and better error messages:
```typescript
// Validate response structure
if (!data.screening_results || !data.screening_results.companies) {
  throw new Error('Invalid response format from server');
}

// Better network error messages
if (error instanceof TypeError && error.message.includes('fetch')) {
  throw new Error('Network error: Unable to connect to server. Please check your connection.');
}
```

**File**: `mobile/src/services/screeningApi.ts`

---

### Issue #5: ✅ File Picker Validation
**Problem**: No client-side validation of file type before upload attempt.

**Fix**: Added file extension validation in picker:
```typescript
const fileName = asset.name.toLowerCase();
if (!fileName.endsWith('.csv') && !fileName.endsWith('.xlsx') && !fileName.endsWith('.xls')) {
  Alert.alert(
    'Invalid File Type',
    'Please select a CSV or Excel file (.csv, .xlsx, .xls)'
  );
  return;
}
```

**File**: `mobile/src/screens/CompanyScreeningScreen.tsx`

---

## 🚀 Installation & Testing

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
```

**What this installs**:
- `pandas==2.1.4` - DataFrame operations for CSV/Excel parsing
- `openpyxl==3.1.2` - Excel file support (.xlsx, .xls)
- `numpy==1.26.2` - Numerical operations for analysis

### 2. Restart Backend Server
```bash
uvicorn app.main:app --reload
```

### 3. Test File Upload

#### Test Case 1: CSV File
1. Create `test.csv`:
```csv
ticker,shares,cost_basis
AAPL,100,15000
MSFT,50,12500
GOOGL,25,7500
```

2. Upload via mobile app
3. Expected: Successfully screens 3 companies

#### Test Case 2: Excel File
1. Create `test.xlsx` with same data
2. Upload via mobile app
3. Expected: Successfully screens 3 companies

#### Test Case 3: Invalid File
1. Try to select a .txt or .pdf file
2. Expected: Alert "Invalid File Type" before upload

#### Test Case 4: Empty File
1. Upload empty CSV
2. Expected: Error "File is empty or contains no data"

#### Test Case 5: Missing Ticker Column
1. Upload CSV without ticker/symbol column
2. Expected: Error from fundamental analysis service

---

## 📊 Error Messages Guide

### Client-Side Errors (Before Upload)
| Error | Cause | Solution |
|-------|-------|----------|
| "Invalid File Type" | Wrong file extension | Select .csv, .xlsx, or .xls file |
| "Failed to pick document" | Picker error | Try again, check permissions |

### Server-Side Errors (After Upload)
| Error | Cause | Solution |
|-------|-------|----------|
| "Empty file uploaded" | File has 0 bytes | Check file isn't corrupted |
| "File is empty or contains no data" | File has no rows | Ensure file contains data |
| "Failed to parse file" | Invalid format | Check CSV/Excel structure |
| "File contains no data rows" | Only headers, no data | Add data rows to file |
| "No ticker column found" | Missing required column | Add ticker/symbol column |
| "Server configuration error" | Missing pandas/openpyxl | Run pip install -r requirements.txt |

### Network Errors
| Error | Cause | Solution |
|-------|-------|----------|
| "Network error: Unable to connect" | Server down or wrong URL | Check backend is running |
| "Authentication Required" | No auth token | Log in to app |
| "Invalid response format" | Server error | Check backend logs |

---

## 🧪 Testing Checklist

### File Upload Tests
- [ ] Upload valid CSV file (3-5 companies)
- [ ] Upload valid Excel .xlsx file
- [ ] Upload valid Excel .xls file
- [ ] Try to upload .txt file (should be blocked)
- [ ] Upload empty file (should error gracefully)
- [ ] Upload file with only headers (should error)
- [ ] Upload large file (50+ companies)

### Error Handling Tests
- [ ] Upload with no auth token (should prompt login)
- [ ] Upload while backend is down (should show network error)
- [ ] Upload malformed CSV (should show parse error)
- [ ] Upload file missing ticker column (should show specific error)

### Success Path Tests
- [ ] Successful upload shows loading spinner
- [ ] Results display correctly
- [ ] All companies parsed
- [ ] Scores calculated properly
- [ ] Recommendations displayed
- [ ] Can expand/collapse cards
- [ ] Can close results and upload again

---

## 🔍 Debugging Tips

### Check Backend Logs
```bash
# Backend should log:
INFO:     127.0.0.1:XXXX - "POST /api/insights/screen-companies HTTP/1.1" 200 OK
```

### Check Frontend Console
```javascript
// Should log on success:
"Screening companies..."
"Response received: {status: 'success', ...}"

// Should log on error:
"Error screening companies: {error message}"
```

### Common Issues

**Issue**: "Server configuration error"
**Solution**: 
```bash
cd backend
pip install pandas openpyxl numpy
```

**Issue**: "Failed to parse file"
**Solution**: Ensure CSV has proper structure:
- Comma-separated values
- First row is headers
- Contains ticker/symbol column

**Issue**: "Network error"
**Solution**: 
- Check backend is running (`uvicorn app.main:app --reload`)
- Verify API_BASE_URL in screeningApi.ts matches backend address
- For physical device testing, update to actual IP address

---

## 📝 Code Changes Summary

### Files Modified
1. ✅ `mobile/src/services/screeningApi.ts`
   - Dynamic MIME type detection
   - Response validation
   - Better error messages

2. ✅ `mobile/src/screens/CompanyScreeningScreen.tsx`
   - File extension validation
   - Better error alerts

3. ✅ `backend/requirements.txt`
   - Added pandas, openpyxl, numpy

4. ✅ `backend/app/api/insights.py`
   - Comprehensive error handling
   - Better logging
   - Parse validation
   - Empty file checks

### Lines Changed
- Frontend: ~40 lines modified
- Backend: ~60 lines modified
- Dependencies: 3 packages added

---

## ✅ Verification

All files compile with **zero errors**:
- ✅ screeningApi.ts - No TypeScript errors
- ✅ CompanyScreeningScreen.tsx - No TypeScript errors
- ✅ insights.py - No Python errors

**Status**: Ready for testing after installing dependencies!

---

## 🚀 Next Steps

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Restart Backend**:
   ```bash
   uvicorn app.main:app --reload
   ```

3. **Test Upload Flow**:
   - Use sample-portfolio.csv
   - Verify successful screening
   - Check results display

4. **If Issues Persist**:
   - Check backend logs
   - Check frontend console
   - Verify file format
   - Ensure backend is accessible from mobile device

---

**Version**: 5.0.1 (Bug Fix Release)  
**Status**: ✅ All Issues Resolved  
**Ready For**: Production Testing
