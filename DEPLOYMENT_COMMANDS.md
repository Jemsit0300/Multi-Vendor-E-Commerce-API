# Step-by-Step Deployment Commands

## 📋 Adım-Adım Deployment Komutu Referans

Bu belge, sunucunuza uygulamanızı deploy etmek için adım adım izlemeniz gereken komutları içerir.

---

## **BÖLÜM 1: Sunucu Hazırlığı** (15-20 dakika)

```bash
# 1. Sunucuya SSH ile bağlan
ssh root@YOUR_SERVER_IP

# 2. Terminal güvenliğini sağla
sudo -i  # Root ol
export HISTFILE=/dev/null  # Komutları log etme

# 3. Sistem paketlerini güncelle
sudo apt update
sudo apt upgrade -y
sudo apt install -y \
    curl \
    wget \
    git \
    python3-pip \
    python3-venv \
    python3-dev \
    build-essential \
    libpq-dev \
    postgresql-client \
    nginx \
    certbot \
    python3-certbot-nginx

# 4. Docker Yükle
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# 5. Docker Compose Yükle
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 6. Doğrula
docker --version
docker-compose --version

# 7. Yeni terminal aç ve SSH'e geri bağlan
# (docker group permission'ı almak için)
exit
ssh root@YOUR_SERVER_IP
```

---

## **BÖLÜM 2: Proje Dizinini Hazırla** (5 dakika)

```bash
# 8. Proje klasörü oluştur
sudo mkdir -p /opt/ecommerce
cd /opt/ecommerce

# 9. GitHub'dan projeyi indir
sudo git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git .

# 10. Sahipliği ayarla
sudo chown -R $USER:$USER /opt/ecommerce
chmod 755 /opt/ecommerce

# 11. Gerekli klasörleri oluştur
mkdir -p logs media staticfiles backups
chmod 755 logs media staticfiles backups
```

---

## **BÖLÜM 3: Environment Variables Konfigürasyonu** (10 dakika)

```bash
# 12. .env.example dosyasını gördür
cat .env.example

# 13. .env dosyasını oluştur (.env.example'i kopyala)
cp .env.example .env

# 14. Güçlü SECRET_KEY oluştur
python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
# Çıktıyı kopyala

# 15. Güçlü database password oluştur
openssl rand -base64 32
# Çıktıyı kopyala

# 16. .env dosyasını düzenle
nano .env

# Aşağıdaki satırları güncelle:
# SECRET_KEY=<PASTE_YOUR_GENERATED_SECRET_KEY>
# DB_PASSWORD=<PASTE_YOUR_GENERATED_PASSWORD>
# ALLOWED_HOSTS=your-domain.com,www.your-domain.com,YOUR_SERVER_IP
# CORS_ALLOWED_ORIGINS=https://frontend-domain.com

# Ctrl+X, Y, Enter ile kaydet

# 17. .env dosyasını protekt et
chmod 600 .env
```

---

## **BÖLÜM 4: Docker Konfigürasyonu** (5 dakika)

```bash
# 18. docker-compose.prod.yml dosyasının olup olmadığını kontrol et
ls -la docker-compose.prod.yml

# 19. Dockerfile.prod dosyasının olup olmadığını kontrol et
ls -la Dockerfile.prod

# Eğer dosyalar yoksa DEPLOYMENT_GUIDE.md'den kopyala
```

---

## **BÖLÜM 5: Nginx ve SSL Yükleme** (15 dakika)

```bash
# 20. backup.sh dosyasını executable yap
chmod +x backup.sh

# 21. Nginx konfigürasyonunu oluştur
sudo cp nginx.conf /etc/nginx/sites-available/ecommerce

# 22. Nginx konfigürasyonunu düzenle
sudo nano /etc/nginx/sites-available/ecommerce

# Şu satırları değiştir:
# - your-domain.com → gerçek domain adın
# - your-frontend-domain.com → frontend domain'in (varsa)

# 23. sites-enabled'e symlink oluştur
sudo ln -s /etc/nginx/sites-available/ecommerce /etc/nginx/sites-enabled/

# 24. default sitesini deaktif et (opsiyonel ama önerilir)
sudo rm /etc/nginx/sites-enabled/default

# 25. Nginx syntax'ini kontrol et
sudo nginx -t
# Sonuç: "syntax is ok" olmalı

# 26. Nginx'i yeniden başlat
sudo systemctl restart nginx

# 27. Let's Encrypt SSL sertifikası al
# DNS'inde domain'ini sunucu IP'sine yönlendir (A record)
# Sonra:
sudo certbot certonly --nginx -d your-domain.com -d www.your-domain.com

# Sertifikat otomatik yenilenecek

# 28. Auto-renewal'i test et
sudo certbot renew --dry-run
```

---

## **BÖLÜM 6: Docker Containers Başlat** (20-30 dakika)

```bash
# 29. Docker image'ını build et
cd /opt/ecommerce
docker-compose -f docker-compose.prod.yml build --no-cache

# Bu işlem 5-10 dakika alabilir... Bekle

# 30. Containerları başlat
docker-compose -f docker-compose.prod.yml up -d

# 31. Birkaç saniye bekle
sleep 5

# 32. Container status'unu kontrol et
docker-compose -f docker-compose.prod.yml ps

# Tüm containerlar "Up" durumunda olmalı

# 33. Database migrations'ı çalıştır
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --noinput

# 34. Static files topla
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# 35. Superuser oluştur (opsiyonel)
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# 36. Logs kontrol et (ilk 20 satır)
docker-compose -f docker-compose.prod.yml logs --tail=20 web
```

---

## **BÖLÜM 7: Application Health Checks** (5 dakika)

```bash
# 37. API health check
curl https://your-domain.com/api/health/

# Sonuç olarak JSON döndürmelidir:
# {"status":"healthy","message":"API is running"}

# 38. SSL sertifikasını kontrol et
curl -I https://your-domain.com | grep "SSL"

# 39. Docker container'ları list et
docker ps

# 40. Log'ları gerçek zamanda takip et
docker-compose -f docker-compose.prod.yml logs -f web

# (Durdurmak için Ctrl+C)
```

---

## **BÖLÜM 8: Systemd Service Kurulum** (Auto-start) (5 dakika)

```bash
# 41. Systemd service dosyasını kopyala
sudo cp ecommerce.service /etc/systemd/system/

# 42. Systemd'yi reload et
sudo systemctl daemon-reload

# 43. Service'i enable et (otomatik başlama)
sudo systemctl enable ecommerce.service

# 44. Service'i başlat
sudo systemctl start ecommerce.service

# 45. Service status'unu kontrol et
sudo systemctl status ecommerce.service

# Devre dışı bırakmak istersen:
# sudo systemctl disable ecommerce.service
```

---

## **BÖLÜM 9: Backup ve Monitoring** (5 dakika)

```bash
# 46. Cron job için backup script'i setup et
sudo crontab -e

# Şu satırı ekle (her gün saat 2'de backup):
# 0 2 * * * cd /opt/ecommerce && bash backup.sh >> /var/log/ecommerce_backup.log 2>&1

# Ctrl+X, Y, Enter ile kaydet

# 47. Bir backup deneme
cd /opt/ecommerce
bash backup.sh

# 48. Backup dosyasının oluşup oluşmadığını kontrol et
ls -lh backups/ | head -5
```

---

## **BÖLÜM 10: İlk Dışarıdan Test** (Tarayıcıdan) (5 dakika)

```
1. Tarayıcı aç
2. https://your-domain.com/api/health/ git
3. JSON response görmelisin
4. Django admin panelini test et: https://your-domain.com/admin/
5. API documentation (varsa): https://your-domain.com/api/docs/
```

---

## **BÖLÜM 11: Post-Deployment Checks** (10 dakika)

```bash
# 49. Tüm running container'ları kontrol et
docker ps
# Hepsi "Up" durumunda olmalı

# 50. Database bağlantısını test et
docker-compose -f docker-compose.prod.yml exec db psql -U ecommerce_user -d ecommerce_prod -c "SELECT version();"

# 51. Redis'i test et
docker-compose -f docker-compose.prod.yml exec redis redis-cli ping
# PONG döndürmelidir

# 52. Static files yüklü mü kontrol et
curl -I https://your-domain.com/static/
# HTTP 200 görmelisin

# 53. Logs'ta hata var mı kontrol et
docker-compose -f docker-compose.prod.yml logs --tail=50 web | grep -i error

# 54. Nginx error logs'unu kontrol et
sudo tail -20 /var/log/nginx/ecommerce_error.log

# 55. SSL sertifikası kada kaldı
sudo certbot certificates
```

---

## **BÖLÜM 12: Firewall ve Security** (5 dakika)

```bash
# 56. UFW Firewall'u etkinleştir (opsiyonel ama önerilir)
sudo ufw enable

# 57. SSH portunu aç (önemli!)
sudo ufw allow 22/tcp

# 58. HTTP ve HTTPS portlarını aç
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 59. Firewall status'unu kontrol et
sudo ufw status

# 60. SSH key-based authentication'ı setup et (advanced)
# (password authentication'ı disable et)
```

---

## **BÖLÜM 13: Monitoring ve Logging** (İsteğe bağlı) (10 dakika)

```bash
# 61. Log rotation'ı setup et
sudo nano /etc/logrotate.d/ecommerce

# Aşağıdaki içeriği paste et:
# /opt/ecommerce/logs/*.log {
#     daily
#     rotate 30
#     compress
#     delaycompress
#     missingok
#     notifempty
#     create 0640 appuser appuser
#     sharedscripts
# }

# 62. Deployment logs'unu sakla
docker-compose -f docker-compose.prod.yml logs > /opt/ecommerce/deployment_logs_$(date +%Y%m%d).txt

# 63. Uptime monitoring'i setup et
# İsteğe bağlı: UptimeRobot, Pingdom, NewRelic, vb.
```

---

## **TAMAMLAMA & DOĞRULAMA** 

```bash
# 64. Final status check
sudo systemctl status ecommerce.service

# 65. Docker containers
docker ps

# 66. API health
curl https://your-domain.com/api/health/

# 67. Logs
docker-compose -f docker-compose.prod.yml logs --tail=10 web

# 68. Certificate status
echo | openssl s_client -connect your-domain.com:443 2>/dev/null | grep "Not After"
```

---

## 🎉 **Deployment Tamamlandı!**

### Sonraki Adımlar:

**Frontend'i ayarla:**
- Frontend CORS_ALLOWED_ORIGINS'ına API domain'ini ekle
- Frontend environment'ini production'a ayarla
- Frontend'i deploy et

**Monitoring:**
- Error tracking tool'u setup et (Sentry, Rollbar, vb.)
- Log monitoring'i setup et (ELK, Papertrail, vb.)
- Regular backup'ları test et
- Database performance'ını monitor et

**Güvenlik:**
- SQL injection testleri yap
- XSS testleri yap
- Regular security updates'i kontrol et
- SSH key'lerini rosette et

---

## 🆘 **Sorun Olursa:**

1. TROUBLESHOOTING.md'yi oku
2. Logs'ları kontrol et: `docker-compose -f docker-compose.prod.yml logs -f web`
3. Health check'i test et: `curl https://your-domain.com/api/health/`
4. GitHub Issues'ye bak

---

## 📝 **Başarı Kriterleri:**

- [ ] API `/api/health/` endpoint'i 200 dönüyor
- [ ] All Docker containers "Up" durumunda
- [ ] Database migrations başarılı
- [ ] SSL sertifikası geçerli
- [ ] Nginx reverse proxy çalışıyor
- [ ] WebSocket bağlantılar çalışıyor (eğer chat varsa)
- [ ] Static files yükleniyor
- [ ] Daily backup'lar oluşuluyor
- [ ] Application otomatik olarak başlıyor (systemd)
- [ ] Logs monitoring etmeyi seçtin

---

**Sonuç:** Tüm kontrol listeleri tamamlanırsa, production'da hazırız! 🚀
