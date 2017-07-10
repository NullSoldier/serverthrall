set -e

rm -rf installer/dist

pyinstaller main.py \
	--name serverthrall \
	--workpath .\\installer\\build \
	--distpath .\\installer\\dist \
	--specpath .\\installer \
	--icon .\\installer\\icon.ico \
	--console \
	--onedir \
	--onefile \
	--noconfirm \
	--clean

 mkdir installer/dist/vendor
 mkdir installer/dist/vendor/steamcmd
 cp -r vendor/steamcmd/steamcmd.exe installer/dist/vendor/steamcmd/steamcmd.exe