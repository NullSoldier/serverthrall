set -e

rm -rf bin/updater/dist
mkdir -p bin/updater
cp updater.ico bin/updater/updater.ico

pyinstaller updater.py \
    --name updater \
    --workpath .\\bin\\updater\\build \
    --distpath .\\bin\\updater\\dist \
    --specpath .\\bin\\updater \
    --icon .\\bin\\updater\\updater.ico \
    --console \
    --onedir \
    --onefile \
    --noconfirm \
    --clean
