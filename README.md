# Fahrradwebsite – Rennradkasko-Landingpage

Statische Landingpage (`index.html`) für die Rennradkasko-Beratung von Ludwig Siebenbürgen.

Live unter: https://rennradkasko.de

## Deployment (Hostinger + GitHub)

Das GitHub-Repository ist mit Hostinger verbunden (hPanel → **Erweitert → GIT**).
Hostinger deployt den `main`-Branch: Jeder Merge nach `main` wird über den
Auto-Deploy-Webhook auf den Webspace übernommen und ist danach unter
https://rennradkasko.de erreichbar.

- Deploy-Branch: `main`
- Ausgeliefert wird der Repo-Inhalt (Root mit `index.html`) – kein Build-Schritt
  nötig, die Seite ist rein statisch.
- Manuell neu ausrollen: in hPanel unter GIT auf **Deploy** klicken bzw. den
  Webhook auslösen.

## Aufbau

- `index.html` – die komplette Startseite (HTML, CSS und JS in einer Datei)
- `impressum.html`, `datenschutz.html`, `erstinformation.html` – Rechtsseiten
- `dokumente/` – Versicherungsbedingungen und Produkt-Infoblatt (PDF)
- `assets/motion.js` – Framer Motion als Vanilla-JS-Bundle (eingecheckt, wird von `index.html` geladen)
- `assets/fonts/` + `assets/fonts.css` – lokal gehostete Schriften (Archivo, IBM Plex Mono, Instrument Sans)
- `assets/favicon*` / `assets/og-image.jpg` – Icons und Social-Media-Vorschaubild
- `src/motion-entry.js` – Einstiegsdatei für das Motion-Bundle

## Berater-Fotos (Look & Export)

`tools/foto-look.py` macht aus einem Originalfoto (Handy oder Kamera) die Bild-Assets
der Berater-Karte und des runden Avatars – mit einem festen Editorial-Look, wie er bei
Sport-Shootings üblich ist (Lichter zurücknehmen, Schatten öffnen, weiche Kontrastkurve,
gedämpftes Grün, warme Lichter / kühle Schatten, Klarheit, Vignette, feines Korn,
Schärfung nach dem Verkleinern). EXIF-Daten inklusive GPS-Position werden dabei entfernt.

```bash
python3 -m pip install pillow numpy
python3 tools/foto-look.py fotos-original/ludwig-rennen.jpg --fokus 0.5,0.33 --avatar-fokus 0.33,0.2 --avatar-groesse 0.31 --vergleich
```

Erzeugt in `assets/`:

- `berater-ludwig-gross.jpg` + `.webp` – Berater-Karte, 4:3, 1600 × 1200 px (anderes Verhältnis mit `--ausschnitt 3:2` oder `1:1`, dann `aspect-ratio` und `width`/`height` der `berater-portraet` in `index.html` mit anpassen)
- `berater-ludwig.jpg` + `.webp` – rundes Avatar, 512 × 512 px
- mit `--vergleich` zusätzlich ein Vorher/Nachher-Bild zum Gegenchecken (nicht einchecken)

`--fokus x,y` legt den Bildschwerpunkt für den 3:2-Ausschnitt fest, `--avatar-fokus x,y`
die Gesichtsmitte (Werte 0–1, x von links, y von oben). Looks: `--look editorial`
(Standard), `film` (weicher, mehr Korn) oder `clean` (neutral, ohne Tönung). Einzelne
Werte lassen sich mit `--set vignette=0.4` überschreiben; `--help` listet alle.
Originalfotos nicht dauerhaft im Repository lassen – alles im Repo wird mit deployt.

## Framer Motion

Die Seite nutzt [Framer Motion](https://motion.dev) (Vanilla-Einstieg `framer-motion/dom`) für:

- das Bergetappen-Profil im Hintergrund (Parallax beim Scrollen, inkl. Fahrer-Punkt)
- das federnde Zurückschnappen der magnetischen Buttons

Das fertige Bundle liegt unter `assets/motion.js` – die Seite funktioniert also ohne Build-Schritt.
Nur wenn `framer-motion` aktualisiert oder `src/motion-entry.js` geändert wird, neu bündeln:

```bash
npm install
npm run build:motion
```
