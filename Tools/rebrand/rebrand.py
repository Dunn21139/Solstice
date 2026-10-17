#!/usr/bin/env python3
"""
rebrand.py - retarget the Dopamine jailbreak codebase to a new brand.

Scope = "brand layer":
  * user-visible name, icons, assets, bundle IDs, update URLs, UI strings
  * keeps internal ABI intact (libjailbreak / basebin / jbctl symbols,
    the `dopamine` payload binary name, jailbreak root paths, apt package IDs)

Run on a fresh copy of the upstream tree:

    python3 rebrand.py --root /path/to/solstice --dry-run
    python3 rebrand.py --root /path/to/solstice

The brand constants live in main() so this can be re-targeted later.
"""

import argparse
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".build", "build", "DerivedData"}

# --------------------------------------------------------------------------
# Never touched by the generic brand rule.
#   * upstream attribution / licence texts must survive verbatim
# --------------------------------------------------------------------------
def is_manual(rel_path):
    base = os.path.basename(rel_path)
    if base.startswith("LICENSE"):
        return True
    if base in {"README.md", "REBRAND.md"}:
        return True
    return False


# --------------------------------------------------------------------------
# Capitalised "Dopamine" occurrences that describe UPSTREAM version history are
# accurate as-is (this tree is a fork of Dopamine) and must not be renamed.
# The matched word is swapped for a placeholder the generic rename cannot see,
# then restored verbatim.
# --------------------------------------------------------------------------
WORD_MARK = "\x01DOPAMINE\x01"

# Patterns that identify genuine upstream-history references in the source.
HISTORY_PATTERNS = [
    r"Dopamine (?=<=\s*\d)",   # "Dopamine <= 2.3"
    r"Dopamine (?=\d)",        # "Dopamine 1.x", "Dopamine 3.0 - 3.0.6"
    r"earlier Dopamine",       # "earlier Dopamine versions"
    r"patched by Dopamine",    # "it being patched by Dopamine is identifiable"
]


def text_rules(brand, prefix, repo_url, slug, site_url):
    """Ordered (search, replace) pairs applied to every text file."""
    helpers = [
        "momentarius", "Titan", "badRecovery", "dmaFail", "ClearSword",
        "weightBufs", "multicast-bytecopy", "kfd", "DarkSword",
    ]

    rules = [
        # URLs first: they contain the owner/repo pair we are replacing.
        ("https://api.github.com/repos/opa334/Dopamine/releases",
         f"https://api.github.com/repos/{slug}/releases"),
        ("https://github.com/opa334/Dopamine", repo_url),
        ("https://ellekit.space/dopamine/", site_url),
    ]

    # Bundle identifiers, longest / most specific first.
    rules += [
        ("com.opa334.Dopamine.idownloadd", f"{prefix}.idownloadd"),
        ("com.opa334.Dopamine.startup", f"{prefix}.startup"),
        ("com.opa334.Dopamine", prefix),
    ]
    rules += [(f"com.opa334.{h}", f"{prefix}.{h}") for h in helpers]

    # Deliberately NOT renamed:
    #   com.opa334.TrollStore                      third-party app
    #   com.opa334.jailbreakd                      jbserver daemon identity
    #   com.opa334.bootstrapper.background-session  internal URL session id

    rules += [
        ("dopamine-latest-upload", f"{brand.lower()}-latest-upload"),
        ("dopamine.js", f"{brand.lower()}.js"),
    ]
    return rules


def protect_history(text):
    for pat in HISTORY_PATTERNS:
        text = re.sub(pat, lambda m: m.group(0).replace("Dopamine", WORD_MARK), text)
    return text


def restore_history(text):
    return text.replace(WORD_MARK, "Dopamine")


def is_binary(path):
    try:
        with open(path, "rb") as fh:
            return b"\x00" in fh.read(8192)
    except OSError:
        return True


def read_text(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    for enc in ("utf-8", "utf-8-sig", "utf-16", "latin-1"):
        try:
            return raw.decode(enc), enc
        except (UnicodeDecodeError, UnicodeError):
            continue
    return None, None


# Files renamed wherever they appear (applied after the content pass).
FILENAME_RENAMES = [
    ("Dopamine.entitlements", "{brand}.entitlements"),
    ("Dopamine.png", "{brand}.png"),
    ("Dopamine@2x.png", "{brand}@2x.png"),
    ("Dopamine@3x.png", "{brand}@3x.png"),
    ("DopamineLogo.pdf", "{brand}Logo.pdf"),
    ("Dopamine.xcscheme", "{brand}.xcscheme"),
    ("com.opa334.Dopamine.idownloadd.plist", "{prefix}.idownloadd.plist"),
    ("com.opa334.Dopamine.startup.plist", "{prefix}.startup.plist"),
]

DIRNAME_RENAMES = [
    ("Dopamine.imageset", "{brand}.imageset"),
    ("DopamineLogo.imageset", "{brand}Logo.imageset"),
]

# Whole-project renames, deepest path first.
STRUCTURAL_RENAMES = [
    ("Application/Dopamine.xcodeproj", "Application/{brand}.xcodeproj"),
    ("Application/{brand}/Assets.xcassets/Dopamine.imageset",
     "Application/{brand}/Assets.xcassets/{brand}.imageset"),
    ("Application/{brand}/Assets.xcassets/DopamineLogo.imageset",
     "Application/{brand}/Assets.xcassets/{brand}Logo.imageset"),
    ("Application/Dopamine", "Application/{brand}"),
    ("BaseBin/_external/basebin/LaunchDaemons/com.opa334.Dopamine.idownloadd.plist",
     "BaseBin/_external/basebin/LaunchDaemons/{prefix}.idownloadd.plist"),
    ("BaseBin/_external/basebin/LaunchDaemons/com.opa334.Dopamine.startup.plist",
     "BaseBin/_external/basebin/LaunchDaemons/{prefix}.startup.plist"),
    ("Standalone/Corellium/dopamine.js", "Standalone/Corellium/{brandlower}.js"),
]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--brand", default="Solstice")
    ap.add_argument("--prefix", default="com.solstice.jb")
    ap.add_argument("--repo-url", default="https://github.com/CHANGE-ME/Solstice")
    ap.add_argument("--slug", default="CHANGE-ME/Solstice")
    ap.add_argument("--site-url", default="https://example.com/")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    brand = args.brand
    brandlower = brand.lower()
    prefix = args.prefix

    if not os.path.isdir(root):
        sys.exit(f"no such directory: {root}")

    rules = text_rules(brand, prefix, args.repo_url, args.slug, args.site_url)
    brand_re = re.compile(r"Dopamine")
    fmt = dict(brand=brand, brandlower=brandlower, prefix=prefix)

    edited = renamed = 0

    # ---------------- pass 1: file contents -----------------------------
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            if is_manual(rel) or is_binary(path):
                continue

            text, enc = read_text(path)
            if text is None:
                continue

            original = text
            for src, dst in rules:
                if src in text:
                    text = text.replace(src, dst)
            if brand_re.search(text):
                text = restore_history(brand_re.sub(brand, protect_history(text)))

            if text != original:
                edited += 1
                if not args.dry_run:
                    with open(path, "wb") as fh:
                        fh.write(text.encode(enc))

    # ---------------- pass 2: renames -----------------------------------
    for dirpath, dirnames, filenames in os.walk(root, topdown=False):
        if os.path.basename(dirpath) in SKIP_DIRS:
            continue
        for name in filenames:
            for old, new in FILENAME_RENAMES:
                if name == old:
                    src = os.path.join(dirpath, name)
                    dst = os.path.join(dirpath, new.format(**fmt))
                    if src != dst:
                        if not args.dry_run:
                            os.rename(src, dst)
                        renamed += 1
                    break
        for d in list(dirnames):
            for old, new in DIRNAME_RENAMES:
                if d == old:
                    src = os.path.join(dirpath, d)
                    dst = os.path.join(dirpath, new.format(**fmt))
                    if src != dst:
                        if not args.dry_run:
                            os.rename(src, dst)
                        renamed += 1
                    break

    for old, new in sorted(STRUCTURAL_RENAMES, key=lambda p: p[0].count("/"), reverse=True):
        src = os.path.join(root, old.format(**fmt))
        dst = os.path.join(root, new.format(**fmt))
        if os.path.exists(src) and src != dst:
            if not args.dry_run:
                os.rename(src, dst)
            renamed += 1

    print(f"brand         : {brand}   (bundle id prefix: {prefix})")
    print(f"files edited  : {edited}")
    print(f"paths renamed : {renamed}")
    if args.dry_run:
        print("(dry run - nothing written)")


if __name__ == "__main__":
    main()
