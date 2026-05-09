برای استفاده از سرویس‌های ایمیل حرفه‌ای مثل **SendGrid، Mailgun، Amazon SES، Brevo** دو روش اصلی داری:

1️⃣ **SMTP** (ساده‌ترین – مشابه Gmail)  
2️⃣ **API** (حرفه‌ای‌تر و سریع‌تر)

در Django معمولاً **SMTP** راحت‌تر است.

---

# 1️⃣ استفاده از SendGrid

### مرحله 1: ساخت اکانت
برو:

```
https://sendgrid.com
```

ثبت‌نام کن.

---

### مرحله 2: ساخت API Key

از داشبورد:

```
Settings → API Keys → Create API Key
```

یک API Key می‌گیری.

---

### مرحله 3: SMTP Settings

SendGrid SMTP:

```
EMAIL_HOST = smtp.sendgrid.net
EMAIL_PORT = 587
EMAIL_HOST_USER = apikey
EMAIL_HOST_PASSWORD = YOUR_SENDGRID_API_KEY
```

---

### تنظیم در Django

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.sendgrid.net"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "apikey"
EMAIL_HOST_PASSWORD = "YOUR_SENDGRID_API_KEY"

DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"
```

---

# 2️⃣ استفاده از Mailgun

### مرحله 1: ساخت اکانت

```
https://mailgun.com
```

---

### مرحله 2: گرفتن SMTP credentials

در داشبورد:

```
Sending → Domain settings → SMTP credentials
```

---

### تنظیم Django

```python
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

EMAIL_HOST = "smtp.mailgun.org"
EMAIL_PORT = 587
EMAIL_USE_TLS = True

EMAIL_HOST_USER = "postmaster@yourdomain.mailgun.org"
EMAIL_HOST_PASSWORD = "your_mailgun_password"

DEFAULT_FROM_EMAIL = "noreply@yourdomain.com"
```

---

# 3️⃣ استفاده از Brevo (Sendinblue)

ثبت‌نام:

```
https://brevo.com
```

SMTP:

```python
EMAIL_HOST = "smtp-relay.brevo.com"
EMAIL_PORT = 587

EMAIL_HOST_USER = "your_brevo_email"
EMAIL_HOST_PASSWORD = "your_smtp_key"
```

---

# 4️⃣ استفاده از Amazon SES

این حرفه‌ای‌ترین است ولی setup سخت‌تر است.

مراحل:

1️⃣ ساخت اکانت AWS  
2️⃣ فعال کردن **SES**  
3️⃣ Verify کردن domain یا email  
4️⃣ گرفتن SMTP credentials

تنظیم:

```python
EMAIL_HOST = "email-smtp.us-east-1.amazonaws.com"
EMAIL_PORT = 587

EMAIL_HOST_USER = "SMTP_USERNAME"
EMAIL_HOST_PASSWORD = "SMTP_PASSWORD"
```

---

# مثال ارسال ایمیل در Django

```python
from django.core.mail import send_mail

send_mail(
    "OTP Code",
    "Your OTP code is: 123456",
    "noreply@yourdomain.com",
    ["user@gmail.com"],
)
```

---

# برای OTP

می‌توانی این را داخل Celery بگذاری:

```python
@shared_task
def send_otp_email(email, code):
    send_mail(
        "Verification Code",
        f"Your verification code is {code}",
        "noreply@yourdomain.com",
        [email],
    )
```

---

✅ پیشنهاد واقعی برای پروژه‌ها:

- **شروع:** Brevo یا SendGrid (خیلی ساده)  
- **Production بزرگ:** Amazon SES

---

اگر بخواهی می‌توانم یک **سیستم کامل OTP ایمیل در Django (Production‑Ready)** هم برایت بنویسم که شامل:

- Redis OTP storage  
- Celery async email  
- Rate limit  
- OTP attempt limit  
- Anti‑spam  

باشد.