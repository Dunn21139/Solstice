# Rebrand notes

This tree is a **rebranded fork of [Dopamine](https://github.com/opa334/Dopamine)**
(MIT, (c) 2023-2024 Lars Fröder / opa334). It was produced by applying
`rebrand.py` to an upstream checkout, then generating new visual assets with
`gen_assets.py`.

Brand: **Solstice** · bundle-id prefix: `com.solstice.jb`

## What was changed

| Area | Detail |
| --- | --- |
| Product name | `Dopamine` → `Solstice` (target, scheme, `CFBundleDisplayName`, folder, `.xcodeproj`, `.entitlements`) |
| Bundle IDs | `com.opa334.Dopamine` → `com.solstice.jb`; exploit helper apps → `com.solstice.jb.*`; `idownloadd`/`startup` launchd labels and their plists |
| Settings domain | `com.opa334.Dopamine.plist` → `com.solstice.jb.plist` |
| Update feed | GitHub releases API → your repo (currently a placeholder) |
| UI strings | every `Dopamine` occurrence in all 27 `Localizable.strings` files, incl. their keys |
| Assets | app icon + 4 alternate icons, in-app wordmark, boot-logo mark (PDF), 5 theme backgrounds, all regenerated |
| Docs / CI | README, Corellium guide, GitHub Actions workflow name + artifact names |
| Licence | upstream MIT notice retained and a second copyright line added for the fork's modifications |

## What was deliberately NOT changed

These are internal ABI / interop identifiers. Renaming them breaks the
on-device contract between the app, the BaseBin and apt, for no user-visible
gain.

- C symbols: `is_dopamine_app`, `gDopamineDomain`, `dopamine_get_root`,
  `dopamine_drop_root`, `dopamine_is_jailbroken`, `jbclient_dopamine_*`,
  `JBS_DOMAIN_DOPAMINE`, `JBS_DOPAMINE_*`
- The `dopamine` payload binary and its `BaseBin/dopamine/` directory
- The `DO` Objective-C class prefix
- On-device paths: `/private/preboot/dopamine_tmp`, `dopamine-<UUID>`,
  `.installed_dopamine`
- Debian package IDs: `libroot-dopamine`, `libkrw0-dopamine`,
  `dopamine-basebin-link` and the `libkrw-dopamine.{dylib,deb}` filenames
  (also referenced from `DOBootstrapper.m`)
- Third-party identities: `com.opa334.TrollStore`, `com.opa334.jailbreakd`
- Upstream version-history comments (e.g. "Dopamine 3.0 changed …") and all
  `LICENSE_*.md` texts - these must stay verbatim

If you later want the internals renamed too, do it in one pass across
`BaseBin/`, `Packages/` and the matching app-side references, and rebuild the
basebin - a partial rename will stop the jailbreak from working.

## Required follow-up

1. **Point the URLs at your own repo.** `CHANGE-ME/Solstice` appears in:
   - `Application/Solstice/UI/DOUIManager.m` (release feed for update checks)
   - `Application/Solstice/UI/Settings/DOCreditsViewController.m` (source link)
   - `Application/Solstice/UI/Update/DOUpdateViewController.m` (release page)
   - `Packages/basebin-link/control`, `Packages/libkrw-provider/control`
2. **Set the website** (`https://example.com/`) in `README.md` and the
   `Packages/*/control` `Homepage:` fields.
3. **Replace the maintainer address** `maintainer@example.com` in
   `Packages/*/control`.
4. **Set your signing team** - `DEVELOPMENT_TEAM` is empty in
   `Application/Solstice.xcodeproj`; the Makefiles ad-hoc sign with `ldid`.
5. Replace the generated icon if you want original artwork - the current mark
   is a placeholder "radiant sun" designed to be legible from 40px up.
