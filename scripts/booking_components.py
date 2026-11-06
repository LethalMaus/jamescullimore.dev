"""Booking choices shared by English and German service pages."""
from html import escape
from urllib.parse import quote

TOPMATE = 'https://topmate.io/james_cullimore/1585464'
FIVERR = 'https://www.fiverr.com/cullimorejames'

def enquiry_email(subject, prompt, lang='en'):
    intro = 'Hallo James,' if lang == 'de' else 'Hi James,'
    body = intro + '\n\n' + prompt + '\n\n'
    return 'mailto:info@jamescullimore.dev?subject=' + quote(subject) + '&amp;body=' + quote(body)

def booking_choices(email, lang='en'):
    de = lang == 'de'
    copy = [
      ('Projektanfrage' if de else 'Project enquiry', 'Projekt besprechen' if de else 'Discuss your project',
       'Für Entwicklung, Unterstützung im Team oder eine technische Bestandsaufnahme. Beschreiben Sie kurz Ihr Projekt und wo Sie Hilfe brauchen.' if de else 'For development, team support or a technical assessment. Tell me what you’re building and where you need help.',
       'Projektanfrage per E-Mail' if de else 'Email about your project', email, 'email',
       'Umfang und nächste Schritte klären wir gemeinsam.' if de else 'We’ll agree the scope and next steps together.'),
      ('Kostenlos · 15 Minuten' if de else 'Free · 15 minutes', 'Lernen wir uns kennen' if de else 'Let’s talk about your project',
       'Erzählen Sie uns von Ihrem Vorhaben. In einem kurzen Gespräch mit James klären wir, welche Unterstützung passt und ob wir zusammenarbeiten möchten.' if de else 'Tell James what you have in mind. We’ll discuss the help you need and whether we’re a good fit for your project.',
       'Kostenloses Erstgespräch buchen' if de else 'Book a free 15-minute chat', TOPMATE, 'topmate',
       'Unverbindliches Kennenlernen, keine technische Beratung.' if de else 'An introductory conversation, with no obligation. Technical advice is available in separate sessions.'),
      ('Definierte Leistung · Fiverr' if de else 'Defined scope · Fiverr', 'Passendes Angebot finden' if de else 'Find a service package',
       'Sehen Sie sich unsere Angebote auf Fiverr an und prüfen Sie Leistungsumfang, Preis und Lieferzeit.' if de else 'Browse our Fiverr services and compare what’s included, the price and the delivery time.',
       'Angebote auf Fiverr ansehen' if de else 'Browse services on Fiverr', FIVERR, 'fiverr',
       'Details und Bestellung auf Fiverr.' if de else 'Package details and ordering on Fiverr.')
    ]
    cards=[]
    for label,title,body,cta,url,route,note in copy:
        cards.append(f'<article class="booking-card booking-card--{route}"><span class="booking-label">{escape(label)}</span><h3>{escape(title)}</h3><p>{escape(body)}</p><a class="booking-button" data-booking-route="{route}" data-booking-action="{dict(email='project_email', topmate='discovery_call', fiverr='fiverr_services')[route]}" href="{url}">{escape(cta)}</a><p class="booking-note">{escape(note)}</p></article>')
    catalogue_label = 'Alle Topmate-Angebote ansehen (kostenlos und kostenpflichtig)' if de else 'Explore all Topmate sessions (free and paid)'
    catalogue = f'<p class="booking-catalogue"><a class="booking-inline" data-booking-route="topmate" data-booking-action="topmate_catalogue" href="https://topmate.io/james_cullimore">{escape(catalogue_label)}</a></p>'
    return '<div class="booking-grid">'+''.join(cards)+'</div>'+catalogue
