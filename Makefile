.PHONY: build

# Cleans up local folders
reset:
	rm -rf ./dist && rm -rf ./build && rm -rf adbConnector.zip && rm -rf adbConnector.spec

# Zips locally (only for your own testing)
zip-adb:
	zip -j adbConnector.zip ./dist/adbConnector.exe

# Builds locally (only for your own testing)
build:
	pyinstaller --noconfirm --onefile --console --name "adbConnector" --hidden-import=colorama "./server.py" && make zip-adb

# Pushes CODE only. GitHub will see the code, build it, and create the release.
publish:
	git add .
	git commit -m "New Release Update"
	git push origin main