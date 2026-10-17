# Solstice

A rootless semi-untethered jailbreak for iOS 15.0 - 17.3.1 (arm64e),
iOS 15.0 - 18.7.1 / 26.0 - 26.0.1 (A12/A13) and iOS 15.0 - 18.7.1 (arm64).

Solstice is a **rebranded fork of [Dopamine](https://github.com/opa334/Dopamine)**.
Every piece of jailbreak technology in this project - the kernel exploits, the
BaseBin, libjailbreak, systemhook, the bootstrap handling - is the work of
opa334 and the other contributors credited in the app's Credits screen. This
fork changes the product identity only.

Please note that all issues related to version support will be deleted without
response.

Official website / download: `https://example.com/`

## Attribution

Distributed under the MIT licence. The original copyright notice is retained
in [LICENSE.md](LICENSE.md), the `LICENSE_*.md` files in
`Application/Solstice/Resources/` cover the bundled third-party components, and
the in-app Credits screen lists every upstream contributor.

- Upstream project: https://github.com/opa334/Dopamine

## Before you ship this

The fork ships with deliberate placeholders that must be pointed at your own
infrastructure. See [REBRAND.md](REBRAND.md) for the list, or in short:

| Placeholder | Where |
| --- | --- |
| `CHANGE-ME/Solstice` | `Application/Solstice/UI/DOUIManager.m`, `.../DOCreditsViewController.m`, `.../DOUpdateViewController.m`, `Packages/*/control` |
| `https://example.com/` | this file, `Packages/*/control` |
| `maintainer@example.com` | `Packages/*/control` |

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
