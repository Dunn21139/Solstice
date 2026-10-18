# Rebrand notes

This tree is a **rebranded fork of [Dopamine](https://github.com/opa334/Dopamine)**
(MIT, (c) 2023-2024 Lars Fröder / opa334). It was produced by applying
`rebrand.py` to an upstream checkout, generating new visual assets with
`gen_assets.py`, then running `deep_rename.py` to clear the remaining upstream
internals. All three scripts live in `Tools/rebrand/` and are re-runnable:
`deep_rename.py --verify` is the audit for the last one, and its allowlist is
the authoritative list of places that still say "Dopamine" on purpose.

Brand: **Solstice** · bundle-id prefix: `com.solstice.jb`

## What was changed

| Area | Detail |
| --- | --- |
| Product name | `Dopamine` → `Solstice` (target, scheme, `CFBundleDisplayName`, folder, `.xcodeproj`, `.entitlements`) |
| Bundle IDs | `com.opa334.Dopamine` → `com.solstice.jb`; exploit helper apps → `com.solstice.jb.*`; `idownloadd`/`startup` launchd labels and their plists |
| Settings domain | `com.opa334.Dopamine.plist` → `com.solstice.jb.plist` |
| Update feed | GitHub releases API → `Dunn21139/Solstice` releases |
| UI strings | every `Dopamine` occurrence in all 26 `Localizable.strings` files, incl. their keys |
| Credits | upstream contributor credits retained with an explicit "Upstream" group; the Discord button was removed because it pointed at opa334's server |
| Assets | app icon + 4 alternate icons, in-app wordmark, boot-logo mark (PDF), 5 theme backgrounds, all regenerated |
| Docs / CI | README, Corellium guide, GitHub Actions workflow name + artifact names |
| Licence | upstream MIT notice retained and a second copyright line added for the fork's modifications |

## Internal rename ("deep pass")

The first pass deliberately kept the internal ABI intact. A second pass
(`Tools/rebrand/deep_rename.py`) then removed the remaining upstream
identities, because a half-renamed internal is worse than either extreme. It
only touched names that are user-visible or entirely closed within this tree:

| Area | Detail |
| --- | --- |
| Debian package IDs | `libroot-dopamine` → `libroot-solstice`, `libkrw0-dopamine` → `libkrw0-solstice`, `dopamine-basebin-link` → `solstice-basebin-link` |
| Package artifacts | `libkrw-dopamine.{dylib,deb}` → `libkrw-solstice.*` (incl. the Xcode resource reference and `DOBootstrapper.m`) |
| Payload binary | `BaseBin/dopamine/` → `BaseBin/solstice/`, `TARGET = dopamine` → `solstice`, ending up as `/var/jb/basebin/solstice` |
| jbserver | `JBS_DOMAIN_DOPAMINE` / `JBS_DOPAMINE_*` → `…SOLSTICE…`, `gDopamineDomain` → `gSolsticeDomain`, `jbclient_dopamine_*` → `jbclient_solstice_*`, `is_dopamine_app` → `is_solstice_app`, `jbdomain_dopamine.c` → `jbdomain_solstice.c`. The domain id (`5`) is unchanged, so the wire ABI is identical |
| launchd-hook markers | `DOPAMINE_INITIALIZED` → `SOLSTICE_INITIALIZED`, `DOPAMINE_IS_HIDDEN` → `SOLSTICE_IS_HIDDEN` |
| dyld patch magic | `DOPA<version>` → `SOLS<version>`, with writer (`basebin_gen.m`) and reader (`systemhook`) changed together |
| Jailbreak root | generated root directory `dopamine-<uuid>` → `solstice-<uuid>` (the `length == 15` locator check still holds: `"solstice-"` is 9 chars) |
| Staging directory | `/private/preboot/dopamine_tmp` → `/private/preboot/solstice_tmp` |
| App locals / comments | `dopamineApp*` locals, "which process is the dopamine app", "dyld LC_UUID contains dopamine magic" |

## What is still deliberately NOT changed

- **`.installed_dopamine`** — we write it into our own root, *and* the root
  locator reads it as evidence that a legacy `jb-<uuid>` directory is an
  upstream Dopamine 1.x install worth adopting. Renaming it silently disables
  that migration path, so it needs a deliberate decision rather than a blanket
  rename (see below).
- `DOPACLEAN` — the name of an upstream debug mode, in commented-out code.
- The **`DO` Objective-C class prefix** (`DOBootstrapper`, `DOEnvironmentManager`,
  …). It derives from Dopamine but is not a user-visible brand string, and
  renaming 77 files' worth of class names would touch every XIB/storyboard
  reference for no gain.
- Third-party / upstream daemon identities: `com.opa334.TrollStore`,
  `com.opa334.jailbreakd`, `com.opa334.bootstrapper.background-session`.
- Upstream version-history comments (e.g. "Dopamine 3.0 changed …") and all
  `LICENSE_*.md` texts — accurate, this tree is a fork of Dopamine.
- Deb metadata attribution: `Author: opa334 (original Dopamine)`.

### To cut all upstream continuity

If you would rather **not** adopt an existing upstream Dopamine root, change
`.installed_dopamine` to `.installed_solstice` in
`Application/Solstice/Jailbreak/DOBootstrapper.m` (3 sites) and
`Application/Solstice/Jailbreak/DOEnvironmentManager.m` (1 site), then re-run
`deep_rename.py --verify`. After that a pre-existing `jb-`/`.installed_dopamine`
root is treated as a foreign jailbreak and a fresh root is created instead.

## Follow-up

**Repo wiring is done.** The update feed, credits link, release page and
package metadata all point at `Dunn21139/Solstice`:

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/Dunn21139/Solstice` |
| Release feed | `https://api.github.com/repos/Dunn21139/Solstice/releases` |
| Package maintainer | `Dunn21139 <Dunn21139@users.noreply.github.com>` |

`Packages/*/control` `Homepage:` fields point at the repository **root**, not a
`tree/<branch>/...` deep link, so they stay valid on any branch.

The fork is published at `Dunn21139/Solstice` on `main` (the repo's default
branch), built green by the `Solstice: build and upload` workflow.

Still to do:

1. **Set your signing team** - `DEVELOPMENT_TEAM` is empty in
   `Application/Solstice.xcodeproj`; the Makefiles ad-hoc sign with `ldid`.
2. Replace the generated icon if you want original artwork - the current mark
   is a placeholder "radiant sun" designed to be legible from 40px up.
3. **Decide on apt continuity.** The rebranded packages have new IDs, so a
   device that previously had upstream Dopamine packages would end up with
   both sets (and two libkrw plug-ins) installed. If you care about that,
   add `Replaces:`/`Conflicts:` on the old names in the `Packages/*/control`
   files. Nothing in this tree needs it today - there are no Solstice
   installs yet.
4. **Rebuild everything after the internal rename.** The payload binary,
   basebin tarball and package artifacts all change name, so a stale
   `BaseBin/.build`, `BaseBin/basebin.tar` or `Packages/*/*.deb` from before
   the rename must not be reused: `make -C BaseBin clean && make -C BaseBin`,
   then `make -C Packages`, then `make -C Standalone`.
5. **Publish releases the way upstream does** - the update feed depends on it.
   `DOUIManager.m` reads `.../releases` from the GitHub API and
   `NSString+Version` parses a tag as `major<<16 | minor<<8 | patch`, compared
   against the running `CFBundleShortVersionString`. Therefore:

   - the version lives in **two places that must match**, and both have to move
     in the same commit: `MARKETING_VERSION` on the app target in
     `Application/Solstice.xcodeproj`, and `BaseBin/_external/basebin/.version`
     (the basebin's own version, written into the jailbreak root on device).
     Solstice stopped following upstream's numbering at `1.0`, which is based on
     Dopamine 3.0.11;
   - the **tag must equal `CFBundleShortVersionString`** (currently `1.0`; see
     `MARKETING_VERSION` in `Application/Solstice.xcodeproj`). Tagging `1.0.1`
     while the app still reports `1.0` would show an update prompt that can
     never be satisfied;
   - the release must not be a **prerelease**, or `getLatestReleaseTag` skips it
     and the feed looks empty;
   - the feed downloads **`assets[0]`**, so upload `Solstice.ipa` *before*
     `Solstice.tipa`. The `.tipa` is a byte-identical copy of the `.ipa` (that
     is how upstream ships the TrollStore variant as well);
   - the CI artifact `Solstice` contains `Application/Solstice.ipa`, so rebuild
     before releasing if the tree changed, and bump `MARKETING_VERSION` in the
     same commit that you tag.
