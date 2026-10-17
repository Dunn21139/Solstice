set -e

zsign -k ./.sign/pkey.p12 -p 1234 -m ./.sign/development.cer -b $1 -m ./.sign/profile.mobileprovision -o ./.sign/Solstice.signed.ipa ./Application/Solstice.ipa
ideviceinstaller install ./.sign/Solstice.signed.ipa