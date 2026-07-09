# Fahrradwebsite – Rennradkasko-Landingpage

Statische Landingpage (`index.html`) für die Rennradkasko-Beratung von Ludwig Siebenbürgen.

Live unter: https://rennradkasko.de

## Deployment (GitHub Pages)

Jeder Push auf `main` wird automatisch über GitHub Actions
(`.github/workflows/deploy.yml`) zu GitHub Pages deployt:

- Standard-Adresse: https://currypulver.github.io/Fahrradwebsite/
- Eigene Domain verbinden: In den Repo-Einstellungen unter
  **Settings → Pages → Custom domain** die Domain `rennradkasko.de` eintragen
  und beim Domain-Anbieter folgende DNS-Einträge setzen:
  - `rennradkasko.de` (Apex): `A`-Records auf `185.199.108.153`,
    `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
  - `www.rennradkasko.de`: `CNAME` auf `currypulver.github.io`
  - Danach in den Pages-Einstellungen **Enforce HTTPS** aktivieren.

## Aufbau

- `index.html` – die komplette Startseite (HTML, CSS und JS in einer Datei)
- `impressum.html`, `datenschutz.html`, `erstinformation.html` – Rechtsseiten
- `dokumente/` – Versicherungsbedingungen und Produkt-Infoblatt (PDF)
- `assets/motion.js` – Framer Motion als Vanilla-JS-Bundle (eingecheckt, wird von `index.html` geladen)
- `assets/fonts/` + `assets/fonts.css` – lokal gehostete Schriften (Archivo, IBM Plex Mono, Instrument Sans)
- `assets/favicon*` / `assets/og-image.jpg` – Icons und Social-Media-Vorschaubild
- `src/motion-entry.js` – Einstiegsdatei für das Motion-Bundle

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
