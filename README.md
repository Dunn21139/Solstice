# Solstice

A rootless semi-untethered jailbreak. These are upstream's support boundaries,
which this fork inherits unchanged:

| iOS / iPadOS | Devices |
| --- | --- |
| 15.0 - 17.3.1 | every supported device (A8 - A17, M1 - M2) |
| 17.4 - 18.7.1 | A13 and earlier only |
| 26.0 - 26.0.1 | A13 and earlier only |

Nothing above 26.0.1 is supported, so do not update past it. For the exact
device-by-device matrix see
[AppleDB](https://appledb.dev/device-selection/), the same reference upstream
points at. Note that the support tables on `ellekit.space` describe Dopamine,
not this fork, but the boundaries are identical.

Solstice is a **rebranded fork of [Dopamine](https://github.com/opa334/Dopamine)**.
Every piece of jailbreak technology in this project - the kernel exploits, the
BaseBin, libjailbreak, systemhook, the bootstrap handling - is the work of
opa334 and the other contributors credited in the app's Credits screen. This
fork changes the product identity only.

Please note that all issues related to version support will be deleted without
response.

Official website / download: <https://github.com/Dunn21139/Solstice>

## Attribution

Distributed under the MIT licence. The original copyright notice is retained
in [LICENSE.md](LICENSE.md), the `LICENSE_*.md` files in
`Application/Solstice/Resources/` cover the bundled third-party components, and
the in-app Credits screen lists every upstream contributor.

- Upstream project: https://github.com/opa334/Dopamine

## Installing

Download the `.tipa`/`.ipa` from the
[releases page](https://github.com/Dunn21139/Solstice/releases). Which route you
need depends on your iOS version.

### TrollStore - iOS 15.0 to 16.6.1, 16.7 RC (20H18), 17.0

This is the route to prefer. The install is permanent (no re-signing), and
TrollStore preserves the entitlements the app is ad-hoc signed with, which is
why the release is signed with `ldid` rather than shipped unsigned.

Install [TrollStore](https://ios.cfw.guide/installing-trollstore) first, then
open this **on the device**:

    apple-magnifier://install?url=https://github.com/Dunn21139/Solstice/releases/latest/download/Solstice.tipa

That is TrollStore's install URL scheme (it replaces `apple-magnifier`), and it
offers to install straight from the release. Alternatively, save the `.tipa` to
Files and open it via the `+` button in TrollStore's Apps tab.

### Sideloading - any supported version

Use this for 16.7 through 16.7.16, 17.0.1 through 18.7.1 and 26.0 to 26.0.1,
where TrollStore cannot work because the CoreTrust bug it relies on was fixed in
17.0.1. Install the `.ipa` with
[PlumeImpactor](https://github.com/khcrysalis/PlumeImpactor),
[AltStore](https://altstore.io) or Sideloadly, signed in with your own Apple
Account - the tool re-signs the app, so the bundled entitlements are dropped and
replaced.

1. Plug the device into a computer and install the `.ipa` with one of those tools.
2. Trust the profile: Settings -> General -> VPN & Device Management.
3. On iOS 16 and later, also enable Settings -> Privacy & Security -> Developer
   Mode.
4. Re-sign every 7 days - a free certificate expires after a week, and a
   semi-untethered jailbreak has to be re-applied from the app after any reboot.

`ios.cfw.guide` documents the surrounding process in detail (installing
TrollStore, the exact per-version steps, and the caveat that a device still on
the iOS build it shipped with has to use the TrollStore route); substitute this
fork's release for the download step in
[those guides](https://ios.cfw.guide/installing-dopamine/).

### After installing

Open Solstice from the home screen and tap **Jailbreak**. Sileo appears once the
jailbreak has taken effect. From then on, updates are applied in-app: the app
reads the release feed, downloads the asset and hands it to `jbctl update tipa`,
so a jailbroken device never needs to be reinstalled by hand.

## Versioning

Solstice's version number is its own; the first release, **1.0**, is based on
upstream **Dopamine 3.0.11**. The number lives in two places that must always
move together - `MARKETING_VERSION` on the app target in
`Application/Solstice.xcodeproj` and `BaseBin/_external/basebin/.version`, which
is the basebin's own version written into the jailbreak root - and the update
feed requires the release tag to equal it. See [REBRAND.md](REBRAND.md) for the
release checklist.

## Repo wiring

The update feed, credits link, release page and package metadata point at this
fork's own repository:

| Setting | Value |
| --- | --- |
| Repository | `https://github.com/Dunn21139/Solstice` |
| Release feed | `https://api.github.com/repos/Dunn21139/Solstice/releases` |
| Package maintainer | `Dunn21139 <Dunn21139@users.noreply.github.com>` |

The package `Homepage:` fields point at the repository **root** rather than a
`tree/<branch>/...` deep link, so they cannot 404 whichever branch you push.
See [REBRAND.md](REBRAND.md) for what still needs doing by hand (signing team,
artwork, release checklist).

## Building

Requires a full Xcode install, [Theos](https://theos.dev) with the
`iPhoneOS16.5.sdk`, GNU make, `ldid` and `libarchive`.

```sh
gmake -j$(sysctl -n hw.logicalcpu)              # release build
gmake -j$(sysctl -n hw.logicalcpu) NIGHTLY=1    # nightly build (adds commit hash)
```

Outputs:

- `Application/Solstice.tipa` - signed/adhoc IPA for TrollStore or sideloading
- `BaseBin/basebin.tar` - the on-device base binaries
- `Standalone/Solstice.tar` - Corellium standalone bundle

`make update DEVICE=<host>` pushes a build to a jailbroken device over SSH.
