#!/usr/bin/env python3
"""pwgen - cryptographically secure passwords and passphrases (uses `secrets`).

Usage:
    python pwgen.py                 # one 20-char password
    python pwgen.py -l 32 -c 5      # five 32-char passwords
    python pwgen.py --words 5       # passphrase like: tiger-lamp-ocean-brisk-mango
    python pwgen.py --no-symbols
"""
import argparse
import math
import secrets
import string

WORDS = """able acid aged also area army away baby back bake ball band bank base bath bear beat bell
belt best bike bird blue boat body bold bone book boot born boss both bowl brave bread brisk
cake calm camp card care cart cash cave chef chip city clay clock cloud coal coat code coin cold
cook cool corn crab crew crow cube dark dawn deer desk dice dish dock door dove drum duck dust
east echo edge epic fair farm fast fern film fire fish flag flat fork fox frog fuel game gate
gift glow goat gold golf grape grass hand harp hawk heat hero hill horn iron jade jazz jump kite
king lake lamp leaf lime lion loud mango maple mars mild mint moon moss nest note oak ocean
olive owl palm park pear pine plum pond quiz rain reef rice ring river road rock rose ruby salt
sand ship silk snow sock solar star stone storm sun swan tiger toast tree tulip vast wave wolf
wood yarn zinc zoom""".split()


def password(length=20, symbols=True):
    pools = [string.ascii_lowercase, string.ascii_uppercase, string.digits]
    if symbols:
        pools.append("!@#$%^&*-_=+?")
    alphabet = "".join(pools)
    while True:  # guarantee at least one char from each pool
        pw = "".join(secrets.choice(alphabet) for _ in range(length))
        if length < len(pools) or all(any(c in p for c in pw) for p in pools):
            return pw


def passphrase(n=5, sep="-"):
    return sep.join(secrets.choice(WORDS) for _ in range(n))


def main():
    ap = argparse.ArgumentParser(description="Generate secure passwords / passphrases.")
    ap.add_argument("-l", "--length", type=int, default=20)
    ap.add_argument("-c", "--count", type=int, default=1)
    ap.add_argument("--words", type=int, metavar="N", help="passphrase with N words instead")
    ap.add_argument("--no-symbols", action="store_true")
    args = ap.parse_args()
    for _ in range(args.count):
        print(passphrase(args.words) if args.words else password(args.length, not args.no_symbols))
    pool = len(WORDS) if args.words else (75 if not args.no_symbols else 62)
    bits = (args.words or args.length) * math.log2(pool)
    print(f"\n~{bits:.0f} bits of entropy each")


if __name__ == "__main__":
    main()
