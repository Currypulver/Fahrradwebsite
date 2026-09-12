#!/usr/bin/env python3
"""
foto-look.py – Editorial-Look und Web-Export für die Berater-Fotos auf rennradkasko.de

Macht aus einem Originalfoto (Handy oder Kamera) die fertigen Bild-Assets der Seite:

  * Berater-Karte   assets/berater-ludwig-gross.jpg + .webp   (3:2, 1600 × 1067 px)
  * rundes Avatar   assets/berater-ludwig.jpg + .webp         (1:1, 512 × 512 px)
  * optional        Vorher/Nachher-Vergleich zum Gegenchecken (--vergleich)

Der Look ist eine feste, reproduzierbare Farbkorrektur, wie sie bei Sport- und
Editorial-Shootings üblich ist – bewusst zurückhaltend, damit es nicht nach
Instagram-Filter aussieht:

  Lichter zurücknehmen · Schatten öffnen · weiche Kontrastkurve · leicht
  angehobenes Schwarz (matt) · gedämpftes, olivfarbenes Grün · warme Lichter,
  kühle Schatten · etwas Klarheit (lokaler Kontrast) · Vignette · feines Korn ·
  Schärfung nach dem Verkleinern

Aufruf (aus dem Projektordner):

  python3 tools/foto-look.py fotos-original/ludwig-rennen.jpg --vergleich
  python3 tools/foto-look.py foto.jpg --look film --fokus 0.5,0.3 --avatar-fokus 0.35,0.2

--fokus / --avatar-fokus sind Bildkoordinaten von 0 bis 1 (x von links, y von oben).
Einzelne Look-Werte lassen sich mit --set überschreiben, z. B. --set vignette=0.4.

Alle EXIF-Daten (auch die GPS-Position des Handys) werden beim Export verworfen.
Benötigt: python3 -m pip install pillow numpy
"""
from __future__ import annotations

import argparse
import os
import sys

import numpy as np
from PIL import Image, ImageFilter, ImageOps

KARTE_GROESSE = (1600, 1067)   # passt zu width/height der <img class="berater-portraet">
AVATAR_GROESSE = (512, 512)    # wird auf 46 px rund angezeigt, 512 reicht für jedes Display

# ---------------------------------------------------------------------------
# Looks – alle Werte sind Anteile (0–1) bzw. Grad; „mehr“ kippt schnell ins Künstliche.
# ---------------------------------------------------------------------------
LOOKS = {
    # Sportlich-editorial: kräftig, aber natürlich. Standard für die Seite.
    "editorial": dict(
        ev=0.0,               # Belichtung in Blendenstufen
        lichter=0.30,         # Lichter zurücknehmen (Helm, Sonne auf der Haut)
        schatten=0.30,        # Schatten öffnen (Gesicht unter dem Helm, schwarzes Trikot)
        kontrast=0.20,        # Mittelton-Kontrast (S-Kurve)
        schwarz=0.03,         # Schwarzpunkt anheben (matt)
        weiss=1.0,            # Weißpunkt
        saettigung=-0.05,     # globale Sättigung
        vibrance=0.14,        # schwache Farben stärker anheben als kräftige
        gruen_daempfen=0.42,  # Laub und Wiese entsättigen
        gruen_drehen=-9.0,    # Grün Richtung Oliv drehen (Grad, negativ = gelber)
        blau_daempfen=0.20,   # Himmel entsättigen
        waerme=0.02,          # Weißabgleich, positiv = wärmer
        split=0.025,          # Split-Toning: kühle Schatten / warme Lichter
        klarheit=0.22,        # lokaler Kontrast
        vignette=0.26,        # Abdunklung der Ecken
        korn=0.009,           # Filmkorn
        schaerfe=0.6,         # Schärfung nach dem Verkleinern
    ),
    # Filmischer, weicher: mehr Matt, mehr Korn, wärmer. Für ein ruhigeres Bild.
    "film": dict(
        ev=0.05, lichter=0.40, schatten=0.35, kontrast=0.13, schwarz=0.055, weiss=0.985,
        saettigung=-0.10, vibrance=0.10, gruen_daempfen=0.50, gruen_drehen=-14.0,
        blau_daempfen=0.30, waerme=0.04, split=0.04, klarheit=0.15, vignette=0.30,
        korn=0.016, schaerfe=0.5,
    ),
    # Sauber und neutral: keine Tönung, kaum Vignette, kein Korn.
    "clean": dict(
        ev=0.0, lichter=0.30, schatten=0.25, kontrast=0.15, schwarz=0.0, weiss=1.0,
        saettigung=0.0, vibrance=0.10, gruen_daempfen=0.25, gruen_drehen=-5.0,
        blau_daempfen=0.10, waerme=0.01, split=0.0, klarheit=0.18, vignette=0.14,
        korn=0.0, schaerfe=0.6,
    ),
}


# ---------------------------------------------------------------------------
# Hilfsfunktionen (alles float32, Werte 0–1)
# ---------------------------------------------------------------------------
def smoothstep(a: float, b: float, x: np.ndarray) -> np.ndarray:
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3.0 - 2.0 * t)


def luma(rgb: np.ndarray) -> np.ndarray:
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def box_blur(a: np.ndarray, r: int, durchlaeufe: int = 3) -> np.ndarray:
    """Mehrfacher Box-Blur über Summentabellen ≈ Gauß-Weichzeichner, ohne SciPy."""

    def achse(x: np.ndarray, axis: int) -> np.ndarray:
        pad = [(0, 0)] * x.ndim
        pad[axis] = (r, r)
        xp = np.pad(x, pad, mode="edge")
        c = np.cumsum(xp, axis=axis, dtype=np.float64)
        null = np.zeros_like(np.take(c, [0], axis=axis))
        c = np.concatenate([null, c], axis=axis)
        n = x.shape[axis]
        oben = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=axis)
        unten = np.take(c, np.arange(0, n), axis=axis)
        return ((oben - unten) / (2 * r + 1)).astype(np.float32)

    for _ in range(durchlaeufe):
        a = achse(achse(a, 0), 1)
    return a


def rgb_zu_hsv(rgb: np.ndarray):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(axis=-1)
    mn = rgb.min(axis=-1)
    d = mx - mn
    bunt = d > 1e-6
    ds = np.where(bunt, d, 1.0)
    rc, gc, bc = (mx - r) / ds, (mx - g) / ds, (mx - b) / ds
    h = np.where(mx == r, bc - gc, np.where(mx == g, 2.0 + rc - bc, 4.0 + gc - rc))
    h = np.where(bunt, (h / 6.0) % 1.0, 0.0)
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0.0)
    return h.astype(np.float32), s.astype(np.float32), mx.astype(np.float32)


def hsv_zu_rgb(h: np.ndarray, s: np.ndarray, v: np.ndarray) -> np.ndarray:
    i = np.floor(h * 6.0).astype(np.int64) % 6
    f = h * 6.0 - np.floor(h * 6.0)
    p, q, t = v * (1 - s), v * (1 - s * f), v * (1 - s * (1 - f))
    r = np.choose(i, [v, q, p, p, t, v])
    g = np.choose(i, [t, v, v, q, p, p])
    b = np.choose(i, [p, p, t, v, v, q])
    return np.stack([r, g, b], axis=-1)


def farbton_gewicht(h: np.ndarray, mitte_grad: float, breite_grad: float) -> np.ndarray:
    """1 in der Mitte des Farbtonbereichs, weich auf 0 am Rand (kreisförmiger Abstand)."""
    d = np.abs(((h - mitte_grad / 360.0 + 0.5) % 1.0) - 0.5) * 360.0
    t = np.clip(d / breite_grad, 0.0, 1.0)
    return 0.5 * (1.0 + np.cos(np.pi * t))


# ---------------------------------------------------------------------------
# Die eigentlichen Bearbeitungsschritte
# ---------------------------------------------------------------------------
def tonwerte(rgb: np.ndarray, p: dict) -> np.ndarray:
    """Belichtung, Lichter, Schatten, Kontrast – über die Luminanz, damit Farben nicht kippen."""
    L = luma(rgb)
    L1 = L * (2.0 ** p["ev"])
    # Lichter über 0.55 sanft stauchen
    L2 = L1 - p["lichter"] * smoothstep(0.55, 1.0, L1) * (L1 - 0.55)
    # Schatten öffnen, ohne reines Schwarz mit anzuheben
    m = 1.0 - smoothstep(0.0, 0.45, L2)
    L3 = L2 + p["schatten"] * m * L2 * (1.0 - L2) * 2.0
    # S-Kurve um 0.45 – die Gewichtung 4·L·(1−L) lässt Schwarz und Weiß in Ruhe
    L4 = L3 + p["kontrast"] * (L3 - 0.45) * 4.0 * L3 * (1.0 - L3)
    L4 = np.clip(L4, 0.0, 1.0)
    faktor = L4 / np.maximum(L, 1e-4)
    out = np.clip(rgb * faktor[..., None], 0.0, 1.0)
    # Schwarz-/Weißpunkt additiv (matt)
    return p["schwarz"] + out * (p["weiss"] - p["schwarz"])


def farbe(rgb: np.ndarray, p: dict) -> np.ndarray:
    w = p["waerme"]
    rgb = np.clip(rgb * np.array([1.0 + w, 1.0, 1.0 - w], dtype=np.float32), 0.0, 1.0)
    h, s, v = rgb_zu_hsv(rgb)
    haut = farbton_gewicht(h, 22.0, 35.0)     # Hauttöne weitgehend schützen
    gruen = farbton_gewicht(h, 105.0, 55.0)
    blau = farbton_gewicht(h, 215.0, 45.0)
    s = s * (1.0 + p["saettigung"] * (1.0 - 0.7 * haut))
    s = s + p["vibrance"] * s * (1.0 - s) * (1.0 - 0.6 * haut)
    s = s * (1.0 - p["gruen_daempfen"] * gruen) * (1.0 - p["blau_daempfen"] * blau)
    h = (h + (p["gruen_drehen"] / 360.0) * gruen) % 1.0
    rgb = hsv_zu_rgb(h, np.clip(s, 0.0, 1.0), v)
    # Split-Toning: Schatten leicht Richtung Petrol, Lichter leicht warm
    if p["split"] > 0:
        L = luma(rgb)
        sch = (1.0 - smoothstep(0.0, 0.5, L))[..., None]
        li = smoothstep(0.5, 1.0, L)[..., None]
        kuehl = np.array([-0.5, 0.15, 1.0], dtype=np.float32)
        warm = np.array([1.0, 0.45, -0.6], dtype=np.float32)
        rgb = rgb + p["split"] * (sch * kuehl + li * warm)
    return np.clip(rgb, 0.0, 1.0)


def klarheit(rgb: np.ndarray, p: dict, breite: int) -> np.ndarray:
    """Lokaler Kontrast (großer Radius), Lichter und tiefe Schatten ausgenommen – kein HDR-Look."""
    if p["klarheit"] <= 0:
        return rgb
    L = luma(rgb)
    r = max(2, int(round(breite * 0.012)))
    detail = L - box_blur(L, r)
    m = 1.0 - 0.7 * smoothstep(0.75, 1.0, L) - 0.7 * (1.0 - smoothstep(0.0, 0.12, L))
    Ln = np.clip(L + p["klarheit"] * detail * m, 0.0, 1.0)
    faktor = Ln / np.maximum(L, 1e-4)
    return np.clip(rgb * faktor[..., None], 0.0, 1.0)


def vignette(rgb: np.ndarray, staerke: float) -> np.ndarray:
    if staerke <= 0:
        return rgb
    h, w = rgb.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (x - (w - 1) / 2.0) / (w / 2.0)
    dy = (y - (h - 1) / 2.0) / (h / 2.0)
    d = np.sqrt(dx * dx + dy * dy)          # 0 Mitte, 1 Kantenmitte, ~1.41 Ecke
    v = 1.0 - staerke * smoothstep(0.5, 1.5, d)
    return rgb * v[..., None]


def korn(rgb: np.ndarray, staerke: float, seed: int = 7) -> np.ndarray:
    if staerke <= 0:
        return rgb
    rng = np.random.default_rng(seed)
    n = rng.normal(0.0, staerke, rgb.shape[:2]).astype(np.float32)
    n = n * (1.0 - 0.5 * luma(rgb))         # in den Lichtern weniger Korn
    return np.clip(rgb + n[..., None], 0.0, 1.0)


# ---------------------------------------------------------------------------
# Ausschnitt, Pipeline, Export
# ---------------------------------------------------------------------------
def ausschnitt(im: Image.Image, verhaeltnis: tuple[int, int], fokus: tuple[float, float],
               zoom: float = 1.0) -> Image.Image:
    """Größtmögliches Fenster im Seitenverhältnis, so gelegt, dass der Fokuspunkt mittig sitzt."""
    W, H = im.size
    rw, rh = verhaeltnis
    if W / H > rw / rh:
        ch, cw = H, int(round(H * rw / rh))
    else:
        cw, ch = W, int(round(W * rh / rw))
    cw, ch = max(16, int(round(cw * zoom))), max(16, int(round(ch * zoom)))
    fx, fy = fokus
    x0 = min(max(int(round(fx * W - cw / 2)), 0), W - cw)
    y0 = min(max(int(round(fy * H - ch / 2)), 0), H - ch)
    return im.crop((x0, y0, x0 + cw, y0 + ch))


def quadrat(im: Image.Image, fokus: tuple[float, float], anteil: float) -> Image.Image:
    """Quadratischer Ausschnitt ums Gesicht; Kantenlänge = Anteil der kürzeren Bildseite."""
    W, H = im.size
    k = max(16, int(round(min(W, H) * anteil)))
    fx, fy = fokus
    x0 = min(max(int(round(fx * W - k / 2)), 0), W - k)
    y0 = min(max(int(round(fy * H - k / 2)), 0), H - k)
    return im.crop((x0, y0, x0 + k, y0 + k))


def bearbeiten(crop: Image.Image, p: dict, ziel: tuple[int, int]) -> Image.Image:
    zb, zh = ziel
    # Arbeitsgröße: 1,5-fache Zielgröße reicht als Reserve und spart Speicher bei 48-MP-Handyfotos
    ab = min(crop.width, int(zb * 1.5))
    ah = max(1, int(round(ab * zh / zb)))
    arbeit = crop.resize((ab, ah), Image.LANCZOS)
    rgb = np.asarray(arbeit, dtype=np.float32) / 255.0
    rgb = tonwerte(rgb, p)
    rgb = farbe(rgb, p)
    rgb = klarheit(rgb, p, ab)
    rgb = vignette(rgb, p["vignette"])
    im = Image.fromarray((rgb * 255.0 + 0.5).astype(np.uint8), "RGB")
    im = im.resize((zb, zh), Image.LANCZOS)
    if p["schaerfe"] > 0:
        im = im.filter(ImageFilter.UnsharpMask(radius=0.9, percent=int(p["schaerfe"] * 100), threshold=2))
    if p["korn"] > 0:
        rgb = np.asarray(im, dtype=np.float32) / 255.0
        im = Image.fromarray((korn(rgb, p["korn"]) * 255.0 + 0.5).astype(np.uint8), "RGB")
    return im


def speichern(im: Image.Image, basis: str) -> list[str]:
    pfade = []
    im.save(basis + ".jpg", "JPEG", quality=84, optimize=True, progressive=True)
    pfade.append(basis + ".jpg")
    im.save(basis + ".webp", "WEBP", quality=82, method=6)
    pfade.append(basis + ".webp")
    return pfade


def vergleich(vorher: Image.Image, nachher: Image.Image, pfad: str, breite: int = 900) -> None:
    h = int(round(breite * nachher.height / nachher.width))
    a = vorher.resize((breite, h), Image.LANCZOS)
    b = nachher.resize((breite, h), Image.LANCZOS)
    out = Image.new("RGB", (2 * breite + 12, h), (11, 10, 15))
    out.paste(a, (0, 0))
    out.paste(b, (breite + 12, 0))
    out.save(pfad, "JPEG", quality=88)


def punkt(text: str) -> tuple[float, float]:
    try:
        x, y = (float(t) for t in text.split(","))
    except ValueError:
        raise argparse.ArgumentTypeError(f"erwartet x,y zwischen 0 und 1, bekommen: {text!r}")
    if not (0 <= x <= 1 and 0 <= y <= 1):
        raise argparse.ArgumentTypeError(f"x,y müssen zwischen 0 und 1 liegen: {text!r}")
    return x, y


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("quelle", help="Originalfoto (JPEG/PNG/HEIC-Export)")
    ap.add_argument("--look", choices=sorted(LOOKS), default="editorial")
    ap.add_argument("--fokus", type=punkt, default=(0.5, 0.35),
                    help="Bildschwerpunkt für die 3:2-Karte als x,y (0–1), Standard 0.5,0.35")
    ap.add_argument("--zoom", type=float, default=1.0, help="Karte enger beschneiden (z. B. 0.9)")
    ap.add_argument("--avatar-fokus", type=punkt, default=None,
                    help="Gesichtsmitte für das runde Avatar als x,y (0–1), Standard wie --fokus")
    ap.add_argument("--avatar-groesse", type=float, default=0.30,
                    help="Kantenlänge des Avatar-Ausschnitts als Anteil der kürzeren Bildseite (Standard 0.30)")
    ap.add_argument("--out", default="assets", help="Zielordner (Standard: assets)")
    ap.add_argument("--basis", default="berater-ludwig", help="Dateiname ohne Endung (Standard: berater-ludwig)")
    ap.add_argument("--vergleich", action="store_true", help="zusätzlich Vorher/Nachher-Bild schreiben")
    ap.add_argument("--set", action="append", default=[], metavar="WERT=ZAHL",
                    help="einzelnen Look-Wert überschreiben, z. B. --set vignette=0.4 (mehrfach möglich)")
    args = ap.parse_args(argv)

    p = dict(LOOKS[args.look])
    for s in args.set:
        k, _, v = s.partition("=")
        if k not in p:
            ap.error(f"unbekannter Look-Wert {k!r}; möglich: {', '.join(p)}")
        try:
            p[k] = float(v)
        except ValueError:
            ap.error(f"{s!r}: Zahl erwartet")

    try:
        im = ImageOps.exif_transpose(Image.open(args.quelle)).convert("RGB")
    except (OSError, FileNotFoundError) as e:
        ap.error(f"Foto kann nicht geöffnet werden: {e}")
    os.makedirs(args.out, exist_ok=True)
    print(f"Quelle: {args.quelle} ({im.width}×{im.height}), Look: {args.look}")

    # Berater-Karte, 3:2
    karte_crop = ausschnitt(im, (3, 2), args.fokus, args.zoom)
    karte = bearbeiten(karte_crop, p, KARTE_GROESSE)
    for pfad in speichern(karte, os.path.join(args.out, args.basis + "-gross")):
        print(f"  Karte   {pfad}  {karte.width}×{karte.height}  {os.path.getsize(pfad) // 1024} KB")

    # rundes Avatar, 1:1 – gleicher Look, aber leichtere Vignette, kein Korn (wird sehr klein angezeigt)
    pa = dict(p, vignette=min(p["vignette"], 0.12), korn=0.0, klarheit=p["klarheit"] * 0.7)
    avatar_crop = quadrat(im, args.avatar_fokus or args.fokus, args.avatar_groesse)
    avatar = bearbeiten(avatar_crop, pa, AVATAR_GROESSE)
    for pfad in speichern(avatar, os.path.join(args.out, args.basis)):
        print(f"  Avatar  {pfad}  {avatar.width}×{avatar.height}  {os.path.getsize(pfad) // 1024} KB")

    if args.vergleich:
        pfad = os.path.join(args.out, f"vergleich-{args.basis}-{args.look}.jpg")
        vergleich(karte_crop, karte, pfad)
        print(f"  Vergleich {pfad} (links Original, rechts Look)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
