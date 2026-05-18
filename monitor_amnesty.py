import feedparser
import smtplib
import json
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- CONFIG ---
SOURCES = [
    {
        "name": "Amnesty International",
        "url": "https://www.amnesty.org/fr/latest/news/feed/"
    },
    {
        "name": "Human Rights Watch",
        "url": "https://www.hrw.org/rss/news"
    },
    {
        "name": "ONU Info",
        "url": "https://news.un.org/feed/subscribe/fr/news/topic/peace-and-security/feed/rss.xml"
    },
]
KEYWORDS = ["Congo", "DRC", "RDC", "Kivu", "M23", "ADF", "FARDC", "MONUSCO"]
SEEN_FILE = "seen_articles.json"

EMAIL_FROM = "luca.alu1512@gmail.com"   # ← remplace ici
EMAIL_TO   = "luca.alu@lesoir.com"   # ← et ici
SMTP_HOST  = "smtp.gmail.com"
SMTP_PORT  = 587
SMTP_PASS  = os.environ["EMAIL_PASSWORD"]

# --- FONCTIONS ---
def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)

def send_email(title, link, summary, source_name):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = f"🔔 {source_name} – Nouveau rapport RDC : {title}"
    msg["From"]    = EMAIL_FROM
    msg["To"]      = EMAIL_TO
    body = f"""
    <h2>{title}</h2>
    <p><strong>Source :</strong> {source_name}</p>
    <p>{summary}</p>
    <p><a href="{link}">Lire le rapport complet →</a></p>
    """
    msg.attach(MIMEText(body, "html"))
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as s:
        s.starttls()
        s.login(EMAIL_FROM, SMTP_PASS)
        s.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())
    print(f"✅ Email envoyé : [{source_name}] {title}")

def check_feed():
    seen     = load_seen()
    new_seen = set(seen)
    for source in SOURCES:
        print(f"🔍 Vérification : {source['name']}")
        feed = feedparser.parse(source["url"])
        for entry in feed.entries:
            if entry.link in seen:
                continue
            text = (entry.title + " " + entry.get("summary", "")).lower()
            if any(kw.lower() in text for kw in KEYWORDS):
                send_email(entry.title, entry.link, entry.get("summary", ""), source["name"])
            new_seen.add(entry.link)
    save_seen(new_seen)

if __name__ == "__main__":
    check_feed()
