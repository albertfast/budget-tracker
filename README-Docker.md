# SmartBudget Mobile - Docker Kurulumu

Bu proje, hem backend (FastAPI) hem de mobil uygulama (Expo) için Docker konteynerleri içerir.

## Kurulum ve Çalıştırma

### Ön Koşullar
- Docker ve Docker Compose yüklü olmalı

### Adım 1: Servisleri Oluşturma ve Başlatma
```bash
# Proje dizininde olduğunuzdan emin olun
cd /data/projects/smart-tracker/budget-tracker/mobile

# Docker imajlarını oluşturun
docker-compose build

# Servisleri arka planda başlatın
docker-compose up -d
```

### Adım 2: Servislerin Durumunu Kontrol Etme
```bash
# Servislerin durumunu kontrol edin
docker-compose ps

# Backend loglarını görüntüleyin
docker-compose logs backend

# Mobil uygulama loglarını görüntüleyin
docker-compose logs mobile
```

### Adım 3: Erişim Noktaları
- **Backend API**: http://localhost:8001
  - API Dokümantasyonu: http://localhost:8001/docs
  - Sağlık Kontrolü: http://localhost:8001/health
  
- **Mobil Uygulama**:
  - Expo Development Server: http://localhost:19000 (tarayıcıda açın)
  - Tunnel URL'si için: `docker-compose logs mobile` komutunu çalıştırın
  - QR kodu görüntülemek için Expo Go uygulamasını kullanın

### Adım 4: Servisleri Durdurma
```bash
# Servisleri durdurun ve konteynerleri kaldırın
docker-compose down
```

## Yapılandırma

### Backend
- **Port**: 8001
- **Teknoloji**: FastAPI, Uvicorn
- **Dockerfile**: `backend/Dockerfile`
- **Ortam Değişkenleri**: `backend/.env`

### Mobil Uygulama
- **Portlar**: 19000, 19001, 19002
- **Teknoloji**: Expo, React Native
- **Dockerfile**: `Dockerfile.mobile`
- **Ortam Değişkenleri**: `.env`

## Geliştirme

### Backend Değişiklikleri
Backend kodunda değişiklik yaptığınızda, Docker konteyneri otomatik olarak yeniden başlatılacaktır (hot-reload).

### Mobil Uygulama Değişiklikleri
Mobil uygulama kodunda değişiklik yaptığınızda, Metro bundler otomatik olarak yeniden başlatılacaktır.

## Sorun Giderme

### Backend Çalışmıyor
```bash
# Backend loglarını kontrol edin
docker-compose logs backend

# Backend servisini yeniden başlatın
docker-compose restart backend
```

### Mobil Uygulama Çalışmıyor
```bash
# Mobil uygulama loglarını kontrol edin
docker-compose logs mobile

# Mobil uygulama servisini yeniden başlatın
docker-compose restart mobile
```

### Port Çakışmaları
Eğer portlar zaten kullanılıyorsa, `docker-compose.yml` dosyasındaki port ayarlarını değiştirebilirsiniz.