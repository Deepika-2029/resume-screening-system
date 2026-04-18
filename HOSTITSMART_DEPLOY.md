# HostItSmart Deployment Guide

## Files jo upload karne hain:
```
app.py
requirements.txt
Procfile
admin.json
applicants.json
companies.json
templates/  (poori folder)
static/     (poori folder)
```

## Environment Variables (HostItSmart Panel mein set karo):
```
SECRET_KEY=koi_bhi_random_string_likho_yahan
SENDER_EMAIL=tumhara@gmail.com
SENDER_PASSWORD=gmail_app_password_16_digit
FLASK_DEBUG=false
```

## Startup Command:
```
gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

## Admin Login:
- Username: admin
- Password: admin123
