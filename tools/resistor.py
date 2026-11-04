#!/usr/bin/env python3
"""resistor - resistor color code <-> value, plus Ohm's law. For every
electronics student who forgot which color is violet.

Usage:
    python resistor.py brown black red gold          # -> 1 kOhm +/-5%
    python resistor.py yellow violet black brown brown
    python resistor.py 4.7k                          # -> yellow violet red gold
    python resistor.py --ohm V=12 R=470              # solve I and P
"""
import argparse
import math

COLORS = ["black", "brown", "red", "orange", "yellow", "green", "blue", "violet", "grey", "white"]
MULT = {**{c: 10 ** i for i, c in enumerate(COLORS)}, "gold": 0.1, "silver": 0.01}
TOL = {"brown": 1, "red": 2, "green": 0.5, "blue": 0.25, "violet": 0.1, "grey": 0.05, "gold": 5, "silver": 10}
PREFIX = {"": 1, "k": 1e3, "m": 1e6, "M": 1e6, "g": 1e9, "G": 1e9}
ALIAS = {"gray": "grey", "purple": "violet"}


def si(value, unit="Ohm"):
    for p, f in (("G", 1e9), ("M", 1e6), ("k", 1e3), ("", 1), ("m", 1e-3), ("u", 1e-6)):
        if abs(value) >= f or p == "u":
            return f"{value / f:.4g} {p}{unit}"


def decode(bands):
    bands = [ALIAS.get(b.lower(), b.lower()) for b in bands]
    *digits, mult, tol = bands if len(bands) > 3 else bands + ["none"]
    value = int("".join(str(COLORS.index(d)) for d in digits)) * MULT[mult]
    return round(value, 6), TOL.get(tol, 20)


def encode(text, bands=4):
    text = text.strip().replace("Ohm", "").replace("R", "")
    value = float(text[:-1]) * PREFIX[text[-1]] if text[-1] in PREFIX else float(text)
    n = bands - 2  # number of significant digits
    exp = math.floor(math.log10(value)) - (n - 1)
    digits = str(round(value / 10 ** exp)).zfill(n)
    if len(digits) > n:  # rounding overflow, e.g. 9.99 -> 10.0
        digits, exp = digits[:n], exp + 1
    mult = COLORS[exp] if 0 <= exp < 10 else {-1: "gold", -2: "silver"}[exp]
    return [COLORS[int(d)] for d in digits] + [mult, "gold" if bands == 4 else "brown"]


def ohm(**known):
    """Give any two of V, I, R (volts, amps, ohms); returns all four incl. P."""
    V, I, R = known.get("V"), known.get("I"), known.get("R")
    V = V if V is not None else I * R
    I = I if I is not None else V / R
    R = R if R is not None else V / I
    return {"V": V, "I": I, "R": R, "P": V * I}


def main():
    ap = argparse.ArgumentParser(description="Resistor color code & Ohm's law helper.")
    ap.add_argument("items", nargs="+", help="color bands, a value like 4.7k, or V=.. I=.. R=..")
    ap.add_argument("--ohm", action="store_true", help="solve Ohm's law from two of V/I/R")
    ap.add_argument("-b", "--bands", type=int, default=4, choices=(4, 5))
    args = ap.parse_args()
    if args.ohm:
        r = ohm(**{k.upper(): float(v) for k, v in (x.split("=") for x in args.items)})
        print(f"V = {si(r['V'], 'V')}   I = {si(r['I'], 'A')}   R = {si(r['R'])}   P = {si(r['P'], 'W')}")
    elif args.items[0][0].isdigit():
        print(" ".join(encode(args.items[0], args.bands)))
    else:
        value, tol = decode(args.items)
        print(f"{si(value)}  +/-{tol}%   (range {si(value * (1 - tol / 100))} .. {si(value * (1 + tol / 100))})")


if __name__ == "__main__":
    main()
