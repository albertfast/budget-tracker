# How to Test Company Screening Feature 🧪

## 📋 Prerequisites

### 1. Backend Must Be Running
```bash
# In a terminal, navigate to backend directory
cd C:\Users\Student\Downloads\Documents\GitHub\budget-tracker\backend

# Start the backend server
uvicorn app.main:app --reload

# You should see:
# INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

### 2. Mobile App Must Be Running
```bash
# In another terminal, navigate to mobile directory
cd C:\Users\Student\Downloads\Documents\GitHub\budget-tracker\mobile

# Start Expo
npx expo start

# Open in:
# - Press 'w' for web browser
# - Scan QR code with Expo Go app
# - Press 'a' for Android emulator (if installed)
# - Press 'i' for iOS simulator (Mac only)
```

---

## 🎯 Step-by-Step Testing Guide

### **Test 1: Create a Sample CSV File**

Create a file named `test-companies.csv` with this content:

```csv
ticker,shares,cost_basis,current_value
AAPL,100,15000,18500
MSFT,50,12500,16000
GOOGL,25,7500,9200
TSLA,30,8000,7500
NVDA,40,10000,14000
AMZN,20,6000,7500
META,35,9000,11000
```

**Save this file** to an easily accessible location (Desktop, Downloads, etc.)

---

### **Test 2: Navigate to Company Screening**

**Option A: From Home Screen**
1. Open the app
2. You'll see the Home screen
3. Look for the **"Company Screening"** card with a **NEW** badge
4. It has a 📊 icon and blue border
5. **Tap the card** to navigate

**Option B: Direct Navigation**
1. If you have navigation visible
2. Look for the "Screening" tab
3. Tap it to go directly to the screening screen

---

### **Test 3: Upload the CSV File**

1. **On the Company Screening screen**, you'll see:
   - Info card explaining what it analyzes
   - File format requirements
   - Example CSV format
   - Blue dashed button: **"Select CSV/Excel File"**

2. **Tap "Select CSV/Excel File"**
   - File picker will open
   - Navigate to where you saved `test-companies.csv`
   - Select the file

3. **File Selected Confirmation**
   - You'll see a green box with ✅
   - Shows the file name: `test-companies.csv`
   - New button appears: **"Screen Companies"**

---

### **Test 4: Screen the Companies**

1. **Tap "Screen Companies"** button
   - Loading spinner appears
   - Text changes to "Screening Companies..."
   - Wait 2-5 seconds

2. **Success!** Results screen appears showing:
   - Summary statistics
   - Top 3 performers
   - Key insights
   - Full company list

---

### **Test 5: Explore the Results**

#### **Summary Card** (Top of screen)
- 📊 Screening Summary
- Total companies screened: 7
- Average score
- Highest score
- 🏆 Top 3 performers with badges

#### **Company Cards** (Main section)
Each card shows:
- **Rank** (#1, #2, #3, etc.)
- **Ticker** (AAPL, MSFT, etc.)
- **Grade** (A, B+, etc.) with color
- **Score** (85.2%, etc.)
- **Recommendation** badge:
  - 🟢 STRONG BUY (green)
  - 🟢 BUY (lime)
  - 🟡 HOLD (yellow)
  - 🟠 WATCH (orange)
  - 🔴 AVOID (red)

#### **Expand a Company Card**
1. **Tap any company card**
2. Card expands to show:
   - **📈 Predictability**
     - QoQ Score: 88%
     - QoY Score: 94%
     - Overall: 92% (excellent)
     - Trend: improving 📈
   
   - **📄 10-K Report Depth**
     - Depth Score: 85% (excellent)
     - Expansion: expanding 🔼
     - 5 metrics with YoY changes
   
   - **🎯 Quality Components**
     - 4 progress bars showing contributions
   
   - **💭 Recommendation Reasons**
     - Bullet points explaining why

3. **Tap again to collapse**

---

### **Test 6: Sort & Browse**

1. **Sort Controls** (below summary)
   - Tap **"Score"** → Sorts highest to lowest
   - Tap **"Ticker"** → Sorts alphabetically

2. **Scroll through all companies**
   - Swipe up/down to browse
   - Each ranked by quality

3. **Close Results**
   - Scroll to bottom
   - Tap **"Close Results"** button
   - Returns to upload screen

---

## 🧪 Additional Test Cases

### **Test 7: Excel File Upload**

Create `test-companies.xlsx` in Excel with same data:
| ticker | shares | cost_basis | current_value |
|--------|--------|------------|---------------|
| AAPL   | 100    | 15000      | 18500         |
| MSFT   | 50     | 12500      | 16000         |

- Upload this file instead of CSV
- Should work identically

---

### **Test 8: Error Handling**

#### **A. Invalid File Type**
1. Try to select a .txt or .pdf file
2. **Expected**: Alert "Invalid File Type"
3. Prompts you to select CSV/Excel

#### **B. Empty File**
1. Create empty `empty.csv` with only headers
2. Upload it
3. **Expected**: Error "File contains no data rows"

#### **C. No Ticker Column**
1. Create CSV without ticker/symbol column
```csv
company_name,value
Apple,1000
Microsoft,2000
```
2. Upload it
3. **Expected**: Error "No ticker column found in file"

#### **D. Backend Down**
1. Stop the backend server (Ctrl+C)
2. Try to upload file
3. **Expected**: "Network error: Unable to connect to server"
4. Restart backend to continue testing

---

## 📊 What to Look For

### ✅ **Success Indicators**
- File picker opens smoothly
- File name displays after selection
- Loading spinner shows during processing
- Results appear within 5 seconds
- All companies listed with scores
- Cards expand/collapse smoothly
- Colors match recommendations
- No crashes or freezes

### ⚠️ **Potential Issues**
- "Network error" → Backend not running
- "Authentication Required" → Need to log in first
- "Invalid response" → Backend error (check backend terminal)
- File picker doesn't open → Permission issue

---

## 🎥 Visual Testing Checklist

### Upload Screen
- [ ] Info cards display correctly
- [ ] File format requirements visible
- [ ] Example CSV code block shows
- [ ] "Select File" button works
- [ ] Selected file shows with ✅
- [ ] "Screen Companies" button appears
- [ ] Loading spinner shows during upload

### Results Screen
- [ ] Summary stats accurate
- [ ] Top 3 performers highlighted
- [ ] Key insights display
- [ ] All companies listed
- [ ] Rank numbers correct
- [ ] Scores formatted as percentages
- [ ] Grades color-coded
- [ ] Recommendation badges correct colors

### Expanded Card
- [ ] Predictability section complete
- [ ] All scores visible
- [ ] Trend icon shows
- [ ] 10-K depth section complete
- [ ] 5 metrics with YoY changes
- [ ] Quality bars render
- [ ] All 4 components shown
- [ ] Recommendation reasons listed

### Interactions
- [ ] Tap to expand works
- [ ] Tap to collapse works
- [ ] Only one card expands at a time
- [ ] Sort buttons toggle
- [ ] Scrolling smooth
- [ ] Close button returns to upload

---

## 🐛 Troubleshooting

### Problem: "Network error: Unable to connect to server"
**Solution**: 
```bash
# Ensure backend is running
cd backend
uvicorn app.main:app --reload

# Check it's accessible at http://localhost:8000
```

### Problem: "Authentication Required"
**Solution**: 
- You need to be logged in
- This is a protected endpoint
- For testing, you might need to implement a test user login
- Or temporarily remove authentication requirement

### Problem: File picker doesn't open
**Solution**:
- Check permissions in device settings
- Try restarting the app
- For web: Browser must support file picker API

### Problem: Expo not connecting
**Solution**:
```bash
# Clear Expo cache
cd mobile
npx expo start -c

# Or reinstall packages
npm install
npx expo start
```

### Problem: Backend can't parse file
**Solution**:
- Ensure pandas, openpyxl, numpy are installed:
  ```bash
  cd backend
  pip install pandas openpyxl numpy
  ```
- Check backend terminal for specific error

---

## 📱 Testing on Different Platforms

### **Web Browser (Easiest)**
1. Press 'w' in Expo terminal
2. Opens in browser automatically
3. Use browser's file picker
4. Full functionality works

### **Android Emulator**
1. Have Android Studio installed
2. Press 'a' in Expo terminal
3. Emulator opens
4. Use Android file picker
5. Test with files in emulator's storage

### **iOS Simulator (Mac Only)**
1. Have Xcode installed
2. Press 'i' in Expo terminal
3. Simulator opens
4. Use iOS file picker

### **Physical Device**
1. Install Expo Go app
2. Scan QR code from terminal
3. **Important**: Update API_BASE_URL in `screeningApi.ts`:
   ```typescript
   // Find your computer's IP (ipconfig on Windows)
   const API_BASE_URL = 'http://192.168.1.XXX:8000/api';
   ```
4. Ensure device on same network as computer

---

## 📸 Expected Screenshots

### 1. Upload Screen
```
┌─────────────────────────────────┐
│ 📊 Company Screening            │
│ Upload a CSV or Excel file...   │
│                                  │
│ ℹ️  What This Analyzes:         │
│ • Predictability                 │
│ • Transparency                   │
│ • Quality Score                  │
│                                  │
│ ┌─────────────────────────────┐ │
│ │   📁 Select CSV/Excel File  │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### 2. File Selected
```
┌─────────────────────────────────┐
│ ✅ test-companies.csv            │
│    Selected file                 │
│                                  │
│ ┌─────────────────────────────┐ │
│ │  🔍 Screen Companies        │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

### 3. Results
```
┌─────────────────────────────────┐
│ 📊 Screening Summary             │
│ 7 Companies | Avg: 74.3%        │
│                                  │
│ 🏆 Top Performers:               │
│ #1 AAPL  87.5%  [STRONG BUY]    │
│ #2 MSFT  85.2%  [STRONG BUY]    │
│ #3 GOOGL 82.8%  [STRONG BUY]    │
│                                  │
│ Sort by: [Score] [Ticker]       │
│                                  │
│ ┌─────────────────────────────┐ │
│ │ #1 AAPL    [A]     87.5% ▶  │ │
│ │     STRONG BUY (95% conf)   │ │
│ └─────────────────────────────┘ │
│ ┌─────────────────────────────┐ │
│ │ #2 MSFT    [A-]    85.2% ▶  │ │
│ │     STRONG BUY (95% conf)   │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

---

## 🎯 Quick Test (30 seconds)

**Fastest way to verify it works:**

1. Create `quick-test.csv`:
```csv
ticker,shares
AAPL,100
MSFT,50
GOOGL,25
```

2. Start backend: `uvicorn app.main:app --reload`
3. Start mobile: `npx expo start` → press 'w'
4. Navigate to Company Screening
5. Upload `quick-test.csv`
6. See results in 3 seconds! ✅

---

## 📝 Sample Test Files

You can use the existing sample files in the repo:
- `sample-portfolio.csv` (root directory)
- `sample-balance-sheet.csv` (root directory)
- `sample-profit-loss.csv` (root directory)

These are already formatted correctly and ready to test!

---

## ✅ Test Completion Checklist

- [ ] Backend started successfully
- [ ] Mobile app running
- [ ] Can navigate to Company Screening screen
- [ ] File picker opens
- [ ] Can select CSV file
- [ ] File name displays after selection
- [ ] "Screen Companies" button appears
- [ ] Loading spinner shows
- [ ] Results display within 5 seconds
- [ ] All companies listed
- [ ] Can expand/collapse cards
- [ ] Detailed metrics visible
- [ ] Can sort by score/ticker
- [ ] Can close results
- [ ] Can upload another file

---

## 🚀 Next Steps After Testing

If everything works:
1. ✅ Feature is production-ready
2. 📊 Try with real company data
3. 🎨 Customize if needed
4. 📱 Deploy to app stores

If issues occur:
1. Check backend logs for errors
2. Check browser console for frontend errors
3. Verify dependencies installed
4. See troubleshooting section above

---

**Happy Testing!** 🎉

For questions or issues, check:
- `docs/COMPANY_SCREENING_FIXES.md` - Bug fixes
- `docs/FRONTEND_HEALTH_CHECK.md` - Status report
- `docs/FUNDAMENTAL_SCREENING.md` - Feature details
