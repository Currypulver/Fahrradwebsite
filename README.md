# Fahrradwebsite – Fahrradkasko-Landingpage

Statische Landingpage (`index.html`) für die Fahrradkasko-Beratung von Ludwig Siebenbürgen.

## Aufbau

- `index.html` – die komplette Seite (HTML, CSS und JS in einer Datei)
- `impressum.html` – Impressum (Anbieterkennzeichnung)
- `assets/motion.js` – Framer Motion als Vanilla-JS-Bundle (eingecheckt, wird von `index.html` geladen)
- `src/motion-entry.js` – Einstiegsdatei für das Bundle

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
