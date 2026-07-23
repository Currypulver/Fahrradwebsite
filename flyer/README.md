# Rennradkasko – Auslege-Flyer (Wickelfalz DIN lang)

Klappbarer Flyer zum Auslegen in Fahrradläden. Greift das Branding der Website
(rennradkasko.de) 1:1 auf: gleiche Schriften (Archivo, Instrument Sans, IBM Plex Mono),
Farben (Asphalt-Schwarz, ERGO-Rot) und der „Night Ride"-Look.

## Format

- **Faltung:** Wickelfalz (Rollenfalz) DIN lang – A4 quer, in 3 Teile gefaltet
- **Endformat gefaltet:** 99 × 210 mm (passt in Standard-Prospektständer)
- **Panels:** 100 / 100 / 97 mm – die einwärts einrollende Klappe ist bewusst 3 mm schmaler
- **6 Panels:** Titel · Kontakt · Falzklappe (außen) / Leistungen · Ein Vertrag · Preis+CTA (innen)

## Dateien

| Datei | Zweck |
|-------|-------|
| `rennradkasko-flyer.html` | Quelldatei (Layout, editierbar) |
| `rennradkasko-flyer-druck.pdf` | **Für die Druckerei** – 303 × 216 mm, 3 mm Beschnitt, Schnitt- & Falzmarken |
| `rennradkasko-flyer-a4.pdf` | **Zum Selberdrucken** – A4 quer, ohne Beschnitt, dezente Falzhilfen |
| `build-flyer.mjs` | Baut QR-Codes + beide PDFs neu |

## Drucken

- **Beidseitig (Duplex)**, Wenden **über die kurze Kante** – nur so liegen Vorder- und
  Rückseite deckungsgleich übereinander.
- **Druckerei:** `rennradkasko-flyer-druck.pdf` verwenden (randabfallende Farben + Marken).
- **Selbstdruck:** `rennradkasko-flyer-a4.pdf` auf A4 quer, Skalierung 100 % / „tatsächliche Größe".
- Danach an den beiden Falzlinien zur Rolle falten (rechte Klappe zuerst einschlagen).

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
