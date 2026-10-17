.PHONY: all clean build_clean

all: Solstice.ipa

Solstice.ipa: build/Build/Products/Debug-iphoneos/Solstice.app
	@echo Ad-Hoc signing Solstice
	xattr -rc build/Build/Products/Debug-iphoneos/Solstice.app
	ldid -SSolstice/Solstice.entitlements build/Build/Products/Debug-iphoneos/Solstice.app/Solstice
	ldid -s build/Build/Products/Debug-iphoneos/Solstice.app
	rm -rf Payload Solstice.ipa
	mkdir Payload
	cp -r build/Build/Products/Debug-iphoneos/Solstice.app Payload/Solstice.app
	zip -Ar Solstice.ipa Payload
	rm -rf Payload
	rm -rf Solstice.tipa
	cp Solstice.ipa Solstice.tipa

ifeq ($(NIGHTLY), 1)
build/Build/Products/Debug-iphoneos/Solstice.app: FORCE
	xcodebuild -scheme Solstice -derivedDataPath build -destination 'generic/platform=iOS' CODE_SIGN_IDENTITY="" CODE_SIGNING_REQUIRED=NO GCC_PREPROCESSOR_DEFINITIONS='NIGHTLY=1 COMMIT_HASH=\"$(COMMIT_HASH)\"'
else
build/Build/Products/Debug-iphoneos/Solstice.app: FORCE
	xcodebuild -scheme Solstice -derivedDataPath build -destination 'generic/platform=iOS' CODE_SIGN_IDENTITY="" CODE_SIGNING_REQUIRED=NO
endif

clean:
	rm -rf build Payload Solstice.ipa Solstice.tipa

build_clean:
	rm -rf Payload build

FORCE: ;