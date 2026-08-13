"""
Skript per te plotesuar ofertat e "kevin" (Demo Anbieter) ne 18 gjithsej
(3 faqe x PAGE_SIZE=6), duke i shtuar foto ofertave ekzistuese dhe
duke krijuar 15 oferta te reja me foto + 3 "details" (basic/standard/premium).

Perdorim (nga /home/rpi-deploy-prod/projects/coderr_backend):
    venv/bin/python add_demo_offers.py
"""
import os
import shutil
import sys
import urllib.request
from decimal import Decimal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")

import django  # noqa: E402
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402
from django.core.files.base import ContentFile  # noqa: E402
from django.db import transaction  # noqa: E402

from marketplace_app.models import Offer, OfferDetail  # noqa: E402

User = get_user_model()

BUSINESS_USERNAME = "kevin"

# --- 1. Backup i databazes para se te prekim gje ---
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db.sqlite3")
if os.path.exists(DB_PATH):
    backup_path = DB_PATH.replace("db.sqlite3", "db_manual_backup_pre_offers.sqlite3")
    shutil.copy2(DB_PATH, backup_path)
    print(f"Backup i krijuar: {backup_path}")


def download_image(seed, size="800/600"):
    """Shkarkon nje foto deterministike nga Lorem Picsum sipas 'seed'."""
    url = f"https://picsum.photos/seed/{seed}/{size}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = resp.read()
    return ContentFile(data, name=f"{seed}.jpg")


# --- 2. Perditeso ofertat ekzistuese te kevin me foto ---
EXISTING_IMAGE_SEEDS = {
    "Web Development": "web-development",
    "Logo Design": "logo-design",
    "SEO Optimierung": "seo-optimierung",
}

kevin = User.objects.get(username=BUSINESS_USERNAME)

for title, seed in EXISTING_IMAGE_SEEDS.items():
    try:
        offer = Offer.objects.get(user=kevin, title=title)
    except Offer.DoesNotExist:
        print(f"[SKIP] Nuk u gjet oferta ekzistuese '{title}'")
        continue
    if offer.image:
        print(f"[OK] '{title}' ka tashme foto, s'e prek.")
        continue
    try:
        img = download_image(seed)
        offer.image.save(img.name, img, save=True)
        print(f"[UPDATE] Foto e shtuar per '{title}'")
    except Exception as e:
        print(f"[ERROR] Deshtoi shkarkimi i fotos per '{title}': {e}")


# --- 3. Oferta te reja (deri sa kevin te kete 18 gjithsej) ---
NEW_OFFERS = [
    dict(
        title="Content Erstellung",
        seed="content-erstellung",
        description="Hochwertige Inhalte für Blog, Website und Social Media. Überzeuge deine Zielgruppe mit professionellen Texten.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=2, delivery_time_in_days=5, price="79.00",
                 features=["1 Blogartikel (500 Wörter)", "SEO-optimiert"]),
            dict(offer_type="standard", title="Standard", revisions=4, delivery_time_in_days=7, price="199.00",
                 features=["3 Blogartikel", "SEO-optimiert", "Keyword-Recherche"]),
            dict(offer_type="premium", title="Premium", revisions=8, delivery_time_in_days=14, price="449.00",
                 features=["8 Blogartikel", "SEO-optimiert", "Content-Strategie", "Monatlicher Redaktionsplan"]),
        ],
    ),
    dict(
        title="Social Media Marketing",
        seed="social-media-marketing",
        description="Professionelles Management deiner Social-Media-Kanäle. Mehr Reichweite und Engagement für deine Marke.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=1, delivery_time_in_days=7, price="149.00",
                 features=["1 Plattform", "8 Posts/Monat"]),
            dict(offer_type="standard", title="Standard", revisions=3, delivery_time_in_days=7, price="349.00",
                 features=["2 Plattformen", "16 Posts/Monat", "Community Management"]),
            dict(offer_type="premium", title="Premium", revisions=6, delivery_time_in_days=14, price="699.00",
                 features=["3 Plattformen", "30 Posts/Monat", "Community Management", "Monatlicher Report"]),
        ],
    ),
    dict(
        title="App Entwicklung",
        seed="app-entwicklung",
        description="Native und plattformübergreifende Apps für iOS und Android. Von der Idee bis zum App Store.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=2, delivery_time_in_days=21, price="999.00",
                 features=["Einfache App (3 Screens)", "iOS oder Android"]),
            dict(offer_type="standard", title="Standard", revisions=5, delivery_time_in_days=45, price="2499.00",
                 features=["Mittlere App (8 Screens)", "iOS und Android", "Backend Anbindung"]),
            dict(offer_type="premium", title="Premium", revisions=10, delivery_time_in_days=90, price="5999.00",
                 features=["Komplexe App", "iOS und Android", "Backend Anbindung", "3 Monate Support"]),
        ],
    ),
    dict(
        title="E-Commerce Einrichtung",
        seed="ecommerce-einrichtung",
        description="Kompletter Online-Shop mit Zahlungsabwicklung und Produktkatalog. Starte noch heute mit dem Verkauf.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=2, delivery_time_in_days=10, price="399.00",
                 features=["Bis zu 20 Produkte", "Zahlungsanbindung"]),
            dict(offer_type="standard", title="Standard", revisions=4, delivery_time_in_days=14, price="799.00",
                 features=["Bis zu 100 Produkte", "Zahlungsanbindung", "Rabattcodes"]),
            dict(offer_type="premium", title="Premium", revisions=8, delivery_time_in_days=21, price="1599.00",
                 features=["Unbegrenzte Produkte", "Zahlungsanbindung", "Rabattcodes", "Mehrsprachigkeit"]),
        ],
    ),
    dict(
        title="Grafikdesign",
        seed="grafikdesign",
        description="Kreatives Grafikdesign für Flyer, Broschüren und Social-Media-Grafiken. Individuell und auffällig.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=2, delivery_time_in_days=3, price="59.00",
                 features=["1 Design", "PNG Format"]),
            dict(offer_type="standard", title="Standard", revisions=4, delivery_time_in_days=5, price="149.00",
                 features=["3 Designs", "PNG + PDF Format", "Druckvorlage"]),
            dict(offer_type="premium", title="Premium", revisions=8, delivery_time_in_days=7, price="299.00",
                 features=["5 Designs", "Alle Formate", "Druckvorlage", "Markenrichtlinien"]),
        ],
    ),
    dict(
        title="Videoproduktion",
        seed="videoproduktion",
        description="Professionelle Videobearbeitung für Werbung, YouTube und Social Media. Von Rohmaterial bis fertigem Schnitt.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=2, delivery_time_in_days=5, price="149.00",
                 features=["Video bis 2 Min", "Schnitt + Musik"]),
            dict(offer_type="standard", title="Standard", revisions=4, delivery_time_in_days=7, price="349.00",
                 features=["Video bis 5 Min", "Schnitt + Musik", "Farbkorrektur"]),
            dict(offer_type="premium", title="Premium", revisions=8, delivery_time_in_days=10, price="699.00",
                 features=["Video bis 10 Min", "Schnitt + Musik", "Farbkorrektur", "Motion Graphics"]),
        ],
    ),
    dict(
        title="Fotografie",
        seed="fotografie",
        description="Professionelle Produktfotografie für deinen Online-Shop oder deine Marke. Hochwertige Bilder, die verkaufen.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=1, delivery_time_in_days=3, price="99.00",
                 features=["5 Produktfotos", "Bildbearbeitung"]),
            dict(offer_type="standard", title="Standard", revisions=2, delivery_time_in_days=5, price="249.00",
                 features=["15 Produktfotos", "Bildbearbeitung", "Freisteller"]),
            dict(offer_type="premium", title="Premium", revisions=4, delivery_time_in_days=7, price="499.00",
                 features=["30 Produktfotos", "Bildbearbeitung", "Freisteller", "Lifestyle-Shooting"]),
        ],
    ),
    dict(
        title="UX/UI Design",
        seed="ux-ui-design",
        description="Nutzerfreundliches UX/UI Design für Web und App. Klar strukturiert und optisch überzeugend.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=2, delivery_time_in_days=7, price="249.00",
                 features=["3 Screens", "Wireframes"]),
            dict(offer_type="standard", title="Standard", revisions=4, delivery_time_in_days=10, price="599.00",
                 features=["8 Screens", "Wireframes", "Klickbarer Prototyp"]),
            dict(offer_type="premium", title="Premium", revisions=8, delivery_time_in_days=14, price="1199.00",
                 features=["15 Screens", "Wireframes", "Klickbarer Prototyp", "Design System"]),
        ],
    ),
    dict(
        title="WordPress Entwicklung",
        seed="wordpress-entwicklung",
        description="Individuelle WordPress-Websites mit modernen Themes und Plugins. Schnell, sicher und einfach zu pflegen.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=2, delivery_time_in_days=5, price="249.00",
                 features=["1 Seite", "Theme Anpassung"]),
            dict(offer_type="standard", title="Standard", revisions=4, delivery_time_in_days=10, price="549.00",
                 features=["5 Seiten", "Theme Anpassung", "Plugin Integration"]),
            dict(offer_type="premium", title="Premium", revisions=8, delivery_time_in_days=14, price="999.00",
                 features=["10 Seiten", "Theme Anpassung", "Plugin Integration", "Wartung 3 Monate"]),
        ],
    ),
    dict(
        title="Übersetzungen",
        seed="uebersetzungen",
        description="Professionelle Übersetzungen für Websites, Dokumente und Marketingmaterial. Präzise und kulturell angepasst.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=1, delivery_time_in_days=3, price="49.00",
                 features=["Bis 500 Wörter", "1 Sprachpaar"]),
            dict(offer_type="standard", title="Standard", revisions=2, delivery_time_in_days=5, price="129.00",
                 features=["Bis 2000 Wörter", "1 Sprachpaar", "Lektorat"]),
            dict(offer_type="premium", title="Premium", revisions=4, delivery_time_in_days=7, price="299.00",
                 features=["Bis 5000 Wörter", "2 Sprachpaare", "Lektorat", "Express Lieferung"]),
        ],
    ),
    dict(
        title="E-Mail Marketing",
        seed="email-marketing",
        description="Effektive E-Mail-Kampagnen, die Kunden binden und Umsatz steigern. Von der Strategie bis zum Versand.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=1, delivery_time_in_days=5, price="99.00",
                 features=["1 E-Mail Kampagne", "Template Design"]),
            dict(offer_type="standard", title="Standard", revisions=3, delivery_time_in_days=7, price="249.00",
                 features=["3 E-Mail Kampagnen", "Template Design", "A/B Testing"]),
            dict(offer_type="premium", title="Premium", revisions=6, delivery_time_in_days=10, price="499.00",
                 features=["6 E-Mail Kampagnen", "Template Design", "A/B Testing", "Automatisierung"]),
        ],
    ),
    dict(
        title="Datenanalyse",
        seed="datenanalyse",
        description="Datenanalyse und Visualisierung für fundierte Geschäftsentscheidungen. Klare Insights aus deinen Daten.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=1, delivery_time_in_days=5, price="199.00",
                 features=["Datenaufbereitung", "Basis-Report"]),
            dict(offer_type="standard", title="Standard", revisions=3, delivery_time_in_days=7, price="449.00",
                 features=["Datenaufbereitung", "Detaillierter Report", "Dashboard"]),
            dict(offer_type="premium", title="Premium", revisions=6, delivery_time_in_days=10, price="899.00",
                 features=["Datenaufbereitung", "Detaillierter Report", "Interaktives Dashboard", "Handlungsempfehlungen"]),
        ],
    ),
    dict(
        title="Virtuelle Assistenz",
        seed="virtuelle-assistenz",
        description="Zuverlässige Unterstützung bei administrativen Aufgaben. Mehr Zeit für dein Kerngeschäft.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=1, delivery_time_in_days=7, price="149.00",
                 features=["10 Stunden/Monat", "E-Mail Management"]),
            dict(offer_type="standard", title="Standard", revisions=2, delivery_time_in_days=7, price="349.00",
                 features=["25 Stunden/Monat", "E-Mail Management", "Terminplanung"]),
            dict(offer_type="premium", title="Premium", revisions=4, delivery_time_in_days=7, price="649.00",
                 features=["50 Stunden/Monat", "E-Mail Management", "Terminplanung", "Recherche"]),
        ],
    ),
    dict(
        title="IT-Beratung",
        seed="it-beratung",
        description="Strategische IT-Beratung für Digitalisierung und Prozessoptimierung. Individuell auf dein Unternehmen zugeschnitten.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=1, delivery_time_in_days=5, price="249.00",
                 features=["1 Stunde Beratung", "Schriftliche Zusammenfassung"]),
            dict(offer_type="standard", title="Standard", revisions=2, delivery_time_in_days=7, price="599.00",
                 features=["3 Stunden Beratung", "Schriftliche Zusammenfassung", "Handlungsplan"]),
            dict(offer_type="premium", title="Premium", revisions=4, delivery_time_in_days=10, price="1199.00",
                 features=["8 Stunden Beratung", "Schriftliche Zusammenfassung", "Handlungsplan", "Umsetzungsbegleitung"]),
        ],
    ),
    dict(
        title="Illustration",
        seed="illustration",
        description="Individuelle digitale Illustrationen für Marken, Bücher oder Social Media. Einzigartiger Stil, der auffällt.",
        details=[
            dict(offer_type="basic", title="Basic", revisions=2, delivery_time_in_days=5, price="89.00",
                 features=["1 Illustration", "Digitale Datei"]),
            dict(offer_type="standard", title="Standard", revisions=4, delivery_time_in_days=7, price="199.00",
                 features=["3 Illustrationen", "Digitale Datei", "Druckauflösung"]),
            dict(offer_type="premium", title="Premium", revisions=8, delivery_time_in_days=10, price="399.00",
                 features=["6 Illustrationen", "Digitale Datei", "Druckauflösung", "Kommerzielle Lizenz"]),
        ],
    ),
]

created_count = 0
for spec in NEW_OFFERS:
    if Offer.objects.filter(user=kevin, title=spec["title"]).exists():
        print(f"[SKIP] '{spec['title']}' ekziston tashme.")
        continue
    try:
        with transaction.atomic():
            offer = Offer.objects.create(
                user=kevin,
                title=spec["title"],
                description=spec["description"],
            )
            for d in spec["details"]:
                OfferDetail.objects.create(
                    offer=offer,
                    title=d["title"],
                    revisions=d["revisions"],
                    delivery_time_in_days=d["delivery_time_in_days"],
                    price=Decimal(d["price"]),
                    features=d["features"],
                    offer_type=d["offer_type"],
                )
            img = download_image(spec["seed"])
            offer.image.save(img.name, img, save=True)
        created_count += 1
        print(f"[CREATE] '{spec['title']}' u krijua me foto dhe 3 details.")
    except Exception as e:
        print(f"[ERROR] Deshtoi krijimi i '{spec['title']}': {e}")

total = Offer.objects.filter(user=kevin).count()
print(f"\nGjithsej oferta te reja te krijuara: {created_count}")
print(f"Gjithsej oferta te kevin tani: {total} (synim: 18 => 3 faqe x 6)")
