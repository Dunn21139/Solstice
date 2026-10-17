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

Official website / download: <https://github.com/Dunn21139/Solstice>

## Attribution

Distributed under the MIT licence. The original copyright notice is retained
in [LICENSE.md](LICENSE.md), the `LICENSE_*.md` files in
`Application/Solstice/Resources/` cover the bundled third-party components, and
the in-app Credits screen lists every upstream contributor.

- Upstream project: https://github.com/opa334/Dopamine

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
