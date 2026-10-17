#!/usr/bin/env python3
"""
deep_rename.py - remove the remaining upstream "dopamine" identities from the
Solstice tree (everything the brand-layer-only `rebrand.py` pass left behind).

One consistent pass, because a half-renamed internal is worse than either
extreme. This touches only names that are either user-visible or entirely
closed within this tree:

  * Debian package IDs and artifact filenames      (visible in Sileo / Zebra)
  * the `dopamine` payload binary and its directory (visible in /var/jb/basebin)
  * jbserver domain / action enums, handlers and client stubs
  * the launchd-hook process marker environment variables
  * the dyld LC_UUID magic written by basebin_gen.m and parsed by systemhook
  * the transient /private/preboot staging directory used during install
  * the generated jailbreak-root directory name (`dopamine-<uuid>`)
  * build-system targets and app-side local variables

Deliberately NOT renamed - these are the on-device interop layer, invisible to
the user, and renaming them has real failure modes:

  * `.installed_dopamine` - we write it into our own root, *and* the root
    locator reads it as evidence that a legacy `jb-<uuid>` directory belongs to
    an upstream Dopamine 1.x install worth adopting. Renaming it silently
    disables that migration path.
  * upstream-history comments ("Dopamine 3.0 changed ...") - accurate, this
    tree forks from Dopamine.
  * attribution in LICENSE.md / Resources/*.md / Credits.plist.

Usage:
    python3 deep_rename.py --root /path/to/solstice --dry-run
    python3 deep_rename.py --root /path/to/solstice
    python3 deep_rename.py --root /path/to/solstice --verify
"""

import argparse
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", ".build", "build", "DerivedData"}
SKIP_PREFIXES = ("Tools/",)  # tooling is not project source; never rewrite it

# --------------------------------------------------------------------------
# Ordered (search, replace) pairs. Order matters where one token is a prefix
# of another, e.g. /private/preboot/dopamine_tmp before /private/preboot/dopamine.
# --------------------------------------------------------------------------
CONTENT_RULES = [
    # -- Debian package IDs -------------------------------------------------
    ("libkrw0-dopamine", "libkrw0-solstice"),
    ("libroot-dopamine", "libroot-solstice"),
    ("dopamine-basebin-link", "solstice-basebin-link"),
    # -- package artifacts (dylib + deb filenames) --------------------------
    ("libkrw-dopamine", "libkrw-solstice"),

    # -- bundled-version macros in the app ---------------------------------
    ("LIBKRW_DOPAMINE_BUNDLED_VERSION", "LIBKRW_SOLSTICE_BUNDLED_VERSION"),
    ("LIBROOT_DOPAMINE_BUNDLED_VERSION", "LIBROOT_SOLSTICE_BUNDLED_VERSION"),

    # -- jbserver domain id + action enums (single definition, value kept) --
    ("JBS_DOMAIN_DOPAMINE", "JBS_DOMAIN_SOLSTICE"),
    ("JBS_DOPAMINE_IS_JAILBROKEN", "JBS_SOLSTICE_IS_JAILBROKEN"),
    ("JBS_DOPAMINE_GET_ROOT", "JBS_SOLSTICE_GET_ROOT"),
    ("JBS_DOPAMINE_DROP_ROOT", "JBS_SOLSTICE_DROP_ROOT"),

    # -- jbserver domain implementation, registration and client stubs -----
    #    (jbclient_* first: it is a prefix of the handler names below)
    ("jbclient_dopamine_", "jbclient_solstice_"),
    ("gDopamineDomain", "gSolsticeDomain"),
    ("dopamine_domain_allowed", "solstice_domain_allowed"),
    ("dopamine_is_jailbroken", "solstice_is_jailbroken"),
    ("dopamine_get_root", "solstice_get_root"),
    ("dopamine_drop_root", "solstice_drop_root"),
    ("is_dopamine_app", "is_solstice_app"),

    # -- launchd-hook process markers --------------------------------------
    ("DOPAMINE_INITIALIZED", "SOLSTICE_INITIALIZED"),
    ("DOPAMINE_IS_HIDDEN", "SOLSTICE_IS_HIDDEN"),

    # -- payload binary entry points ---------------------------------------
    ("install_dopamine_from_tarball", "install_solstice_from_tarball"),
    ("install_dopamine", "install_solstice"),
    ("activate_dopamine", "activate_solstice"),

    # -- dyld LC_UUID magic: writer (basebin_gen.m) and reader (systemhook)
    #    must carry the same 4-byte prefix -----------------------------------
    ('[@"DOPA" stringByAppendingString:dopamineVersion]',
     '[@"SOLS" stringByAppendingString:solsticeVersion]'),
    ('string_has_prefix((char *)dyldUUID, "DOPA")',
     'string_has_prefix((char *)dyldUUID, "SOLS")'),
    ("DOPA<dopamine version>", "SOLS<solstice version>"),
    ("dopamineVersion", "solsticeVersion"),

    # -- transient install staging directory (created + removed in one call)
    ('"/private/preboot/dopamine_tmp/dopamine"', '"/private/preboot/solstice_tmp/solstice"'),
    ('"/private/preboot/dopamine_tmp"', '"/private/preboot/solstice_tmp"'),
    ("/private/preboot/dopamine", "/private/preboot/solstice"),

    # -- generated jailbreak-root directory name + its comments ------------
    ("/private/preboot/UUID/dopamine-<UUID>", "/private/preboot/UUID/solstice-<UUID>"),
    ('[NSString stringWithFormat:@"dopamine-%@", randomString]',
     '[NSString stringWithFormat:@"solstice-%@", randomString]'),
    ('[subItem hasPrefix:@"dopamine-"]', '[subItem hasPrefix:@"solstice-"]'),
    ("look for Dopamine 2.x path", "look for an existing Solstice root"),
    ("rename it so all Dopamine 2.x users will have the same path",
     "rename it so all Solstice users will have the same path"),
    ("DOPACLEAN logic to move a corrupted dopamine directory",
     "DOPACLEAN logic to move a corrupted jailbreak root directory"),

    # -- remaining comments that describe *our own* behaviour, not upstream
    #    history (rebrand.py's history guard wrongly preserved one of these) --
    ("it being patched by Dopamine is identifiable later",
     "it being patched by Solstice is identifiable later"),
    ("Check if dyld LC_UUID contains dopamine magic",
     "Check if dyld LC_UUID contains Solstice magic"),
    ("figure out which process is the dopamine app",
     "figure out which process is the Solstice app"),

    # -- app-side local variables ------------------------------------------
    ("dopamineInstalledAppIds", "solsticeInstalledAppIds"),
    ("dopamineApp", "solsticeApp"),

    # -- build system: payload target / artifact name ----------------------
    ("rootlesshooks dopamine", "rootlesshooks solstice"),
    ("dopamine: .build .include libjailbreak XPF ChOma",
     "solstice: .build .include libjailbreak XPF ChOma"),
    ("$(MAKE) -C dopamine", "$(MAKE) -C solstice"),
    ("@cp dopamine/dopamine .build", "@cp solstice/solstice .build"),
    ("TARGET = dopamine", "TARGET = solstice"),
    ("dopamine/dopamine", "solstice/solstice"),
    (".build/dopamine", ".build/solstice"),
    ("/var/jb/basebin/dopamine", "/var/jb/basebin/solstice"),
    ("Executing dopamine", "Executing Solstice"),
]

# Paths renamed after the content pass (files first, then the directory).
FILE_RENAMES = [
    ("BaseBin/launchdhook/src/jbserver/jbdomain_dopamine.c",
     "BaseBin/launchdhook/src/jbserver/jbdomain_solstice.c"),
]
DIR_RENAMES = [
    ("BaseBin/dopamine", "BaseBin/solstice"),
]

# --------------------------------------------------------------------------
# --verify: lines that are *expected* to still mention the upstream name.
# --------------------------------------------------------------------------
ALLOWED_LINE_PATTERNS = [
    r"\.installed_dopamine\b",          # on-device install / migration marker
    r"\binstalledDopamine\b",           # local naming the legacy marker above
    r"\(original Dopamine\)",           # apt control attribution
    r"rebranded fork of Dopamine",      # apt control description
    r"Dopamine\s*(<=)?\s*\d",           # upstream version history comments
    r"earlier Dopamine versions",       # upstream version history comments
    r"called by Dopamine 1\.x",         # upstream version history comments
    r"\bDOPACLEAN\b",                   # name of an upstream debug mode, dead code
]
ALLOWED_LINE_RE = re.compile("|".join(f"(?:{p})" for p in ALLOWED_LINE_PATTERNS))

# Non-source files whose upstream references are intentional.
ALLOWED_FILES = re.compile(
    r"(^|/)(LICENSE[^/]*\.md|README\.md|REBRAND\.md)$"
    r"|^Tools/"
    r"|^Application/Solstice/Resources/"
    r"|^Application/Solstice/UI/Settings/Credits\.plist$"
)
TOKEN_RE = re.compile(r"dopamine|Dopamine|DOPAMINE|DOPA")


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


def walk(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for name in filenames:
            path = os.path.join(dirpath, name)
            rel = os.path.relpath(path, root)
            if rel.startswith(SKIP_PREFIXES):
                continue
            yield path, rel


def run(root, dry_run):
    hits = {src: 0 for src, _ in CONTENT_RULES}
    edited = 0

    for path, rel in walk(root):
        if ALLOWED_FILES.search(rel) or is_binary(path):
            continue
        text, enc = read_text(path)
        if text is None or not TOKEN_RE.search(text):
            continue

        original = text
        for src, dst in CONTENT_RULES:
            n = text.count(src)
            if n:
                hits[src] += n
                text = text.replace(src, dst)

        if text != original:
            edited += 1
            if not dry_run:
                with open(path, "wb") as fh:
                    fh.write(text.encode(enc))

    renamed = 0
    for old, new in FILE_RENAMES:
        src, dst = os.path.join(root, old), os.path.join(root, new)
        if os.path.exists(src):
            if not dry_run:
                os.rename(src, dst)
            renamed += 1
    for old, new in DIR_RENAMES:
        src, dst = os.path.join(root, old), os.path.join(root, new)
        if os.path.exists(src) and not os.path.exists(dst):
            if not dry_run:
                os.rename(src, dst)
            renamed += 1

    if not edited and not renamed and not dry_run:
        print("nothing to do - tree is already renamed")
        return 0

    print(f"files edited  : {edited}")
    print(f"paths renamed : {renamed}")
    unused = [src for src, n in hits.items() if n == 0]
    if unused:
        print("\nWARNING: these rules matched nothing (upstream drift?):")
        for src in unused:
            print(f"  - {src}")
    if dry_run:
        print("(dry run - nothing written)")
    return 1 if unused else 0


def verify(root):
    unexpected = []
    informational = []
    for path, rel in walk(root):
        if ALLOWED_FILES.search(rel) or is_binary(path):
            continue
        text, _ = read_text(path)
        if text is None:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if not TOKEN_RE.search(line):
                continue
            if ALLOWED_LINE_RE.search(line):
                informational.append(f"{rel}:{lineno}: {line.strip()}")
            else:
                unexpected.append(f"{rel}:{lineno}: {line.strip()}")

    print(f"expected upstream references : {len(informational)}")
    for line in informational:
        print(f"  ok   {line}")
    print(f"\nUNEXPECTED remaining refs    : {len(unexpected)}")
    for line in unexpected:
        print(f"  BAD  {line}")
    return 1 if unexpected else 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--verify", action="store_true")
    args = ap.parse_args()

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        sys.exit(f"no such directory: {root}")

    sys.exit(verify(root) if args.verify else run(root, args.dry_run))


if __name__ == "__main__":
    main()
