#!/usr/bin/env python3
"""THE WORLD TODAY - front page summing up world news of Monday 23 November 2026.

Draws a 1024x1024 newspaper front page from code, Python 3.13 stdlib only.
No network, no clock, no randomness: the same input always renders the same
bytes. Writes a single PNG to /output/entry.png (falls back to ./output/).

News (all as reported on 23 November 2026, verified from public sources):
  1. NATO holds an emergency North Atlantic Council meeting in Brussels after
     Polish prosecutors confirmed the three objects that fell in south-east
     Poland on 20 Nov were Russian Kh-101 cruise missiles.
  2. COP31 climate talks in Antalya collapse without a main deal after record
     overtime, deadlocked over fossil fuels and finance.
  Also: tankers struck in the Strait of Hormuz; a Russian drone hits a flat
  in Dymer near Kyiv (2 dead, 11 missing); Democrats win control of the US
  Congress; FIFA set to confirm the UK as 2035 Women's World Cup host;
  Marc Marquez wins a record-tying 8th MotoGP title; Carlos Alcaraz wins
  his first ATP Finals title.
"""

import hashlib
import os
import struct
import sys
import zlib

W, H = 1024, 1024
PAPER = (247, 243, 234)
INK = (17, 17, 17)
RED = (185, 28, 28)
GREY = (85, 85, 85)

# 5x7 bitmap font: each glyph is 7 rows of 5 bits ("1" = ink).
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    "X": ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ",": ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ":": ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ";": ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "/": ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    "(": ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ")": ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    "%": ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    "$": ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    "&": ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    "+": ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
    "=": ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '"': ("01010", "01010", "00000", "00000", "00000", "00000", "00000"),
}
BLANK = ("00000",) * 7

NORMALIZE = {"\u2014": "-", "\u2013": "-", "\u2019": "'", "\u2018": "'",
             "\u201c": '"', "\u201d": '"'}


def clean(text):
    out = []
    for ch in text:
        ch = NORMALIZE.get(ch, ch)
        out.append(ch if ch in FONT else " ")
    return "".join(out)


class Canvas:
    def __init__(self, w, h, bg):
        self.w, self.h = w, h
        self.px = bytearray(bg[0] for _ in range(w * h))
        self.px = bytearray()
        for _ in range(w * h):
            self.px += bytes(bg)
        self.px = bytearray(self.px)

    def rect(self, x, y, w, h, color):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.px[i:i + 3] = bytes(color)

    def text(self, x, y, s, scale, color):
        s = clean(s)
        for ci, ch in enumerate(s):
            glyph = FONT.get(ch, BLANK)
            ox = x + ci * 6 * scale
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        self.rect(ox + col * scale, y + row * scale,
                                  scale, scale, color)

    def text_width(self, s, scale):
        return len(clean(s)) * 6 * scale - scale

    def text_center(self, y, s, scale, color):
        self.text((self.w - self.text_width(s, scale)) // 2, y, s, scale, color)

    def wrap(self, s, width, scale):
        """Greedy word wrap; returns list of lines fitting width px."""
        s = clean(s)
        max_chars = max(1, width // (6 * scale))
        lines, cur = [], ""
        for word in s.split(" "):
            cand = word if not cur else cur + " " + word
            if len(cand) <= max_chars:
                cur = cand
            else:
                if cur:
                    lines.append(cur)
                while len(word) > max_chars:
                    lines.append(word[:max_chars])
                    word = word[max_chars:]
                cur = word
        if cur:
            lines.append(cur)
        return lines

    def para(self, x, y, s, width, scale, color, leading):
        lines = self.wrap(s, width, scale)
        for i, line in enumerate(lines):
            self.text(x, y + i * leading, line, scale, color)
        return y + len(lines) * leading


def chunk(typ, data):
    out = struct.pack(">I", len(data)) + typ + data
    return out + struct.pack(">I", zlib.crc32(typ + data) & 0xFFFFFFFF)


def encode_png(canvas):
    raw = bytearray()
    stride = canvas.w * 3
    for yy in range(canvas.h):
        raw.append(0)
        raw += canvas.px[yy * stride:(yy + 1) * stride]
    ihdr = struct.pack(">IIBBBBB", canvas.w, canvas.h, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def build():
    c = Canvas(W, H, PAPER)
    # ---- Masthead -------------------------------------------------------
    c.text_center(34, "THE WORLD TODAY", 10, INK)
    c.rect(36, 118, 952, 4, INK)
    c.text_center(132, "MONDAY 23 NOVEMBER 2026", 4, RED)
    c.rect(36, 170, 952, 2, INK)
    c.text_center(184, "TWO BIGGEST STORIES OF 23 NOVEMBER 2026", 3, INK)

    # ---- Panel 1: NATO / Poland ----------------------------------------
    x0, y0, pw, ph = 36, 222, 464, 420
    c.rect(x0, y0, pw, 3, RED)
    c.rect(x0, y0 + ph - 3, pw, 3, INK)
    ix, iw = x0 + 18, pw - 36
    y = y0 + 18
    c.text(ix, y, "NATO - POLAND", 2, RED)
    y += 26
    y = c.para(ix, y,
               "NATO HOLDS EMERGENCY TALKS AFTER RUSSIAN MISSILES LAND IN POLAND",
               iw, 4, INK, 32)
    y += 10
    c.para(ix, y,
           "POLAND SAID ALL THREE OBJECTS THAT FELL IN ITS SOUTH-EAST ON "
           "20 NOVEMBER WERE RUSSIAN KH-101 CRUISE MISSILES. THE NORTH "
           "ATLANTIC COUNCIL MEETS IN BRUSSELS TODAY. NATO CHIEF MARK RUTTE "
           "SAID THE ALLIANCE WILL DEFEND EVERY INCH OF POLISH TERRITORY. "
           "WARSAW SEEKS STRONGER AIR DEFENCE ON ITS EASTERN FLANK. "
           "POLAND DID NOT INVOKE ARTICLE 4.",
           iw, 2, INK, 17)

    # ---- Panel 2: COP31 -------------------------------------------------
    x0 = 524
    c.rect(x0, y0, pw, 3, RED)
    c.rect(x0, y0 + ph - 3, pw, 3, INK)
    ix = x0 + 18
    y = y0 + 18
    c.text(ix, y, "CLIMATE - COP31", 2, RED)
    y += 26
    y = c.para(ix, y,
               "COP31 COLLAPSES WITHOUT A DEAL AS FOSSIL-FUEL ROW DEADLOCKS",
               iw, 4, INK, 32)
    y += 10
    c.para(ix, y,
           "TALKS IN ANTALYA ENDED ON SUNDAY WITHOUT A MAIN DEAL AFTER "
           "RECORD OVERTIME. NEGOTIATORS DEADLOCKED OVER FOSSIL-FUEL "
           "LANGUAGE AND FINANCE COMMITMENTS. DIPLOMATS NOW ASK WHAT, IF "
           "ANYTHING, CLIMATE DIPLOMACY CAN BUILD ON THE COLLAPSE.",
           iw, 2, INK, 17)
    c.text(ix, y0 + ph - 28, "ANTALYA - RECORD OVERTIME, NO DEAL", 2, RED)

    # ---- Strip: also in the news ---------------------------------------
    c.text(36, 656, "ALSO IN THE NEWS", 3, INK)
    c.rect(36, 686, 952, 2, INK)
    cols = [
        (36, [("STRAIT OF HORMUZ",
                "AT LEAST THREE OIL TANKERS WERE STRUCK ON FRIDAY AND "
                "SATURDAY. TWO MORE CAUGHT FIRE ON SUNDAY AFTER HITTING "
                "NAVAL MINES. SHIPPING ATTACKS ARE AT THEIR HIGHEST LEVEL "
                "SINCE THE WAR BEGAN."),
               ("KYIV REGION",
                "A RUSSIAN DRONE HIT A FLAT IN DYMER: 2 DEAD, 11 MISSING.")]),
        (362, [("USA - CONGRESS",
                "DEMOCRATS WON CONTROL OF CONGRESS, FLIPPING A NORTH "
                "CAROLINA SEAT FOR THEIR LARGEST HOUSE MAJORITY SINCE 1992. "
                "A FUNDING DEADLINE LOOMS ON 11 DECEMBER."),
               ("FOOTBALL",
                "FIFA IS SET TO CONFIRM THE UK AS HOST OF THE 2035 WOMEN'S "
                "WORLD CUP TODAY.")]),
        (688, [("MOTOGP",
                "MARC MARQUEZ WON A RECORD-TYING EIGHTH MOTOGP TITLE AT THE "
                "PORTUGUESE GRAND PRIX."),
               ("TENNIS",
                "CARLOS ALCARAZ WON HIS FIRST ATP FINALS TITLE, BEATING "
                "ALEXANDER ZVEREV.")]),
    ]
    for cx, items in cols:
        y = 698
        for heading, body in items:
            c.text(cx, y, heading, 2, RED)
            y += 20
            y = c.para(cx, y, body, 300, 2, INK, 17)
            y += 12

    # ---- Footer ----------------------------------------------------------
    c.rect(36, 966, 952, 2, INK)
    c.text_center(978, "MONDAY 23 NOVEMBER 2026 - ALL STORIES AS REPORTED ON 23 NOVEMBER 2026",
                  2, INK)
    return c


def main():
    canvas = build()
    data = encode_png(canvas)
    try:
        os.makedirs("/output", exist_ok=True)
        path = "/output/entry.png"
        with open(path, "wb") as f:
            f.write(data)
    except OSError:
        os.makedirs("output", exist_ok=True)
        path = os.path.join("output", "entry.png")
        with open(path, "wb") as f:
            f.write(data)
    print("wrote %s %d bytes %dx%d sha256=%s"
          % (path, len(data), W, H, hashlib.sha256(data).hexdigest()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
