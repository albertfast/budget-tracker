# SmartBudget - AI Destekli Transaction Analizi ve Yatırım Tavsiyeleri

## 🎉 Yeni Özellikler

### 1. Özel Plaid Sandbox Kullanıcıları
Custom transaction ve hesap verileriyle test kullanıcıları oluşturabilirsiniz.

### 2. Otomatik Transaction Senkronizasyonu
Plaid'den çekilen transaction'lar otomatik olarak Supabase'e kaydedilir.

### 3. AI Destekli Harcama Analizi
Transaction'larınızı analiz edip:
- Kategori bazında harcama dağılımı
- En çok harcama yaptığınız kategoriler
- Tasarruf önerileri
- Abonelik tespiti ve uyarılar

### 4. Kişiselleştirilmiş Yatırım Tavsiyeleri
Gelir, gider ve risk profilinize göre:
- Acil durum fonu önerileri
- Yatırım dağılım stratejileri (hisse, tahvil, nakit)
- Aylık yatırım tutarı önerileri
- Yıllık tasarruf projeksiyonları

## 📋 Backend API Endpoints

### 1. Custom Sandbox User (POST `/api/plaid/sandbox/custom_user`)

**Kullanım:**
```bash
curl -X POST http://localhost:8001/api/plaid/sandbox/custom_user \
  -H 'Content-Type: application/json' \
  -d '{
    "username": "user_custom",
    "password": "pass_good",
    "institution_id": "ins_109508",
    "config": {
      "seed": "my-custom-seed",
      "override_accounts": [
        {
          "type": "depository",
          "subtype": "checking",
          "starting_balance": 5000,
          "transactions": [
            {
              "date_transacted": "2023-10-01",
              "amount": 100,
              "description": "Netflix subscription",
              "currency": "USD"
            }
          ]
        }
      ]
    }
  }'
```

**Response:**
```json
{
  "public_token": "public-sandbox-...",
  "request_id": "...",
  "username": "user_custom",
  "config_applied": true
}
```

### 2. Transaction Senkronizasyonu (POST `/api/plaid/sync_transactions`)

**Kullanım:**
```bash
curl -X POST http://localhost:8001/api/plaid/sync_transactions \
  -H 'Content-Type: application/json' \
  -d '{
    "access_token": "access-sandbox-..."
  }'
```

**Response:**
```json
{
  "transactions": [...],
  "accounts": [...],
  "total_transactions": 25
}
```

### 3. AI Harcama Analizi (POST `/api/ai/analyze_spending`)

**Kullanım:**
```bash
curl -X POST http://localhost:8001/api/ai/analyze_spending \
  -H 'Content-Type: application/json' \
  -d '[
    {
      "amount": 100,
      "name": "Netflix",
      "category": ["Entertainment"],
      "date": "2023-10-01"
    },
    {
      "amount": 50,
      "name": "Grocery Store",
      "category": ["Food and Drink"],
      "date": "2023-10-02"
    }
  ]'
```

**Response:**
```json
{
  "total_spending": 150,
  "category_breakdown": {
    "Entertainment": 100,
    "Food and Drink": 50
  },
  "top_categories": [
    ["Entertainment", 100],
    ["Food and Drink", 50]
  ],
  "recommendations": [
    {
      "type": "info",
      "category": "Subscriptions",
      "message": "Abonelik harcamalarınız: $100.00...",
      "potential_savings": 30
    }
  ],
  "analysis_period": "Last 30 days"
}
```

### 4. AI Yatırım Tavsiyeleri (POST `/api/ai/investment_advice`)

**Kullanım:**
```bash
curl -X POST http://localhost:8001/api/ai/investment_advice \
  -H 'Content-Type: application/json' \
  -d '{
    "monthly_income": 5000,
    "monthly_expenses": 3000,
    "current_savings": 10000,
    "risk_profile": "moderate"
  }'
```

**Response:**
```json
{
  "disposable_income": 2000,
  "recommended_monthly_investment": 1400,
  "risk_profile": "moderate",
  "allocation": {
    "stocks": 0.5,
    "bonds": 0.4,
    "cash": 0.1
  },
  "recommendations": [
    {
      "type": "investment",
      "category": "Stocks",
      "message": "Stocks için aylık $700.00 yatırım yapın",
      "percentage": 50,
      "monthly_amount": 700
    }
  ],
  "projected_annual_savings": 16800
}
```

## 📱 Mobile App Kullanımı

### 1. Custom User ile Giriş

Expo Go'da:
```
Email: custom_albertfast@test
Password: abc123
```

Email'de "custom" kelimesi varsa, otomatik olarak zengin test verisi oluşturulur.

### 2. Banka Hesabı Bağlama

1. "Connect Account" ekranına gidin
2. "Connect Bank Account" butonuna basın
3. Uygulama otomatik olarak:
   - Sandbox token oluşturur
   - Access token alır
   - Hesapları getirir
   - Transaction'ları senkronize eder
   - Supabase'e kaydeder

### 3. Transaction'ları Görüntüleme

"Transactions" ekranında:
- Tüm transaction'lar kategori bazında listelenir
- Manuel transaction ekleyebilirsiniz
- Plaid'den gelen transaction'lar otomatik gösterilir

### 4. AI Analizi Görüntüleme

Ana ekranda (Home Screen):
- Harcama analizi kartı
- Kategori dağılımı
- Tasarruf önerileri
- Yatırım tavsiyeleri

## 🔧 Teknik Detaylar

### Mobile Services

#### `plaidTransactionService.ts`
```typescript
// Transaction'ları senkronize et
await syncPlaidTransactions(accessToken);

// AI analizi al
await analyzeSpending(transactions);

// Yatırım tavsiyesi al
await getInvestmentAdvice({
  monthly_income: 5000,
  monthly_expenses: 3000,
  current_savings: 10000,
  risk_profile: 'moderate'
});

// Supabase'e kaydet
await savePlaidTransactionsToSupabase(userId, bankAccountId, transactions);
```

### Backend Logic

#### Harcama Analizi Algoritması
1. Transaction'ları kategorilere ayır
2. Toplam harcamayı hesapla
3. En çok harcanan kategorileri bul
4. %40'ın üzerindeki kategoriler için uyarı ver
5. Abonelik benzeri harcamaları tespit et
6. Potansiyel tasarruf önerileri oluştur

#### Yatırım Tavsiyesi Algoritması
1. Harcanabilir geliri hesapla (gelir - gider)
2. Acil durum fonu ihtiyacını belirle (6 aylık gider)
3. Risk profiline göre varlık dağılımı öner:
   - Conservative: %60 tahvil, %30 hisse, %10 nakit
   - Moderate: %50 hisse, %40 tahvil, %10 nakit
   - Aggressive: %70 hisse, %20 tahvil, %10 alternatif
4. Aylık yatırım tutarlarını hesapla

## 🧪 Test Senaryoları

### Senaryo 1: Basit Kullanıcı

```bash
# 1. Token oluştur
curl -X POST http://localhost:8001/api/plaid/sandbox/public_token \
  -d '{"email": "user_good@good", "password": "pass_good"}'

# 2. Token exchange
curl -X POST http://localhost:8001/api/plaid/exchange-token \
  -d '{"public_token": "public-sandbox-..."}'

# 3. Transaction'ları çek
curl -X POST http://localhost:8001/api/plaid/sync_transactions \
  -d '{"access_token": "access-sandbox-..."}'
```

### Senaryo 2: Custom User

```bash
# 1. Custom user oluştur (backend/custom_user_config.json kullanarak)
curl -X POST http://localhost:8001/api/plaid/sandbox/custom_user \
  -d @backend/custom_user_config.json

# 2-3. Aynı adımlar...
```

### Senaryo 3: AI Analizi

```bash
# Transaction'ları al ve analiz et
TRANSACTIONS=$(curl -X POST http://localhost:8001/api/plaid/sync_transactions \
  -d '{"access_token": "access-sandbox-..."}' | jq '.transactions')

# Harcama analizi
curl -X POST http://localhost:8001/api/ai/analyze_spending \
  -d "$TRANSACTIONS"

# Yatırım tavsiyesi
curl -X POST http://localhost:8001/api/ai/investment_advice \
  -d '{
    "monthly_income": 5000,
    "monthly_expenses": 3000,
    "current_savings": 10000,
    "risk_profile": "moderate"
  }'
```

## 🎯 Özellikler ve Yetenekler

✅ **Tamamlanan:**
- Custom Plaid Sandbox kullanıcı oluşturma
- Otomatik transaction senkronizasyonu
- Supabase entegrasyonu
- AI harcama analizi
- AI yatırım tavsiyeleri
- Kategori bazında harcama takibi
- Abonelik tespiti
- Risk bazlı yatırım dağılımı

🚧 **Geliştirilebilir:**
- Gerçek zamanlı bildirimler
- Bütçe oluşturma ve takip
- Grafik ve görselleştirmeler
- Export / CSV indirme
- Multi-currency desteği
- Hedef bazlı tasarruf planları

## 📚 Kaynaklar

- [Plaid Sandbox Documentation](https://plaid.com/docs/sandbox/)
- [Plaid Custom User Config](https://plaid.com/docs/sandbox/user-custom/)
- [Supabase Documentation](https://supabase.com/docs)

## 🐛 Troubleshooting

### Transaction'lar görünmüyor
- Backend'in çalıştığından emin olun: `docker-compose ps`
- Plaid access token'ın geçerli olduğunu kontrol edin
- Supabase bağlantısını test edin

### AI analizi hata veriyor
- Transaction verisi formatını kontrol edin
- Backend log'larına bakın: `docker-compose logs backend`

### Network hatası
- LAN IP'nin doğru olduğunu kontrol edin: `ifconfig`
- `PlaidConnection.tsx` içindeki `API_BASE_URL` değerini güncelleyin
