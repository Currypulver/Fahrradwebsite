# Rennradkasko – Auslege-Flyer

Klappbarer Flyer zum Auslegen in Fahrradläden. Greift das Branding der Website
(rennradkasko.de) 1:1 auf: gleiche Schriften (Archivo, Instrument Sans, IBM Plex Mono),
Farben (Asphalt-Schwarz, ERGO-Rot) und der „Night Ride"-Look.

Es gibt **zwei Faltvarianten** – beide werden auf einem A4-quer-Bogen beidseitig gedruckt:

### Variante 1 · Wickelfalz DIN lang (6 Panels)
- A4 quer, in 3 Teile gefaltet · Endformat **99 × 210 mm** (passt in Prospektständer)
- Panels 100 / 100 / 97 mm – die einrollende Klappe ist bewusst 3 mm schmaler
- Außen: Titel · Kontakt · Falzklappe · Innen: Leistungen · Ein Vertrag · Preis+CTA

### Variante 2 · Einbruchfalz A5 (4 Panels)
- A4 quer, **einmal mittig** gefaltet · Endformat **A5 (148,5 × 210 mm)**
- Außen: Rückseite/Kontakt · Titel · Innen: Leistungen · Beitrag+CTA
- E-Mail und Telefonnummer stehen direkt **neben den QR-Codes**

## Dateien

| Datei | Zweck |
|-------|-------|
| `rennradkasko-flyer.html` / `rennradkasko-flyer-a5.html` | Quelldateien (editierbar) |
| `rennradkasko-flyer-druck.pdf` · `rennradkasko-flyer-a5-druck.pdf` | **Für die Druckerei** – 303 × 216 mm, 3 mm Beschnitt, Schnitt- & Falzmarken |
| `rennradkasko-flyer-a4.pdf` · `rennradkasko-flyer-a5-a4.pdf` | **Zum Selberdrucken** – A4 quer, ohne Beschnitt, dezente Falzhilfen |
| `build-flyer.mjs` | Baut QR-Codes + alle PDFs neu |

## QR-Codes

- **Website-QR →** `https://rennradkasko.de`
- **WhatsApp-QR →** `https://wa.me/4915224827997` (öffnet direkt den Chat mit 0152 24827997,
  vorausgefüllte Nachricht). Beide offline erzeugt (kein externer Dienst), geprüft dekodierbar.

## Drucken

- **Beidseitig (Duplex)**, Wenden **über die kurze Kante** – nur so liegen Vorder- und
  Rückseite deckungsgleich übereinander.
- **Druckerei:** die `*-druck.pdf` der gewünschten Variante verwenden (randabfallende Farben + Marken).
- **Selbstdruck:** die `*-a4.pdf` auf A4 quer, Skalierung 100 % / „tatsächliche Größe".
- Danach falten: Variante 1 an den zwei Falzlinien zur Rolle (rechte Klappe zuerst),
  Variante 2 einmal mittig.

## Neu bauen

```bash
cd flyer
npm install          # installiert 'qrcode' (QR-Erzeugung, offline)
npm run build        # erzeugt QR-Codes + beide PDFs + Vorschau-PNGs
```

Playwright/Chromium wird für das PDF-Rendering genutzt (global vorhanden).

## Hinweise zum Inhalt

- Der Preis **125–195 €/Jahr** ist ein **Beispiel** für ein Rennrad im Wert von 3.000 €
  im Komplettpaket inkl. Hausrat Best und als solches gekennzeichnet (Marketinginformation).
- Vor dem finalen Druck bitte kurz prüfen: Calendly-Link (`calendly.com/rennradkasko`)
  und die Angabe „über 120 Google-Bewertungen" – Print lässt sich nachträglich nicht korrigieren.
