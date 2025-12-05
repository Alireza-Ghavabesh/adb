.PHONY: build

# Cleans up local folders
reset:
	rm -rf ./dist && rm -rf ./build && rm -rf emuVPN.zip && rm -rf emuVPN.spec

# Zips locally (only for your own testing)
zip-emu:
	zip -j emuVPN.zip ./dist/emuVPN.exe

# Builds locally (only for your own testing)
build:
	pyinstaller --noconfirm --onefile --console --name "emuVPN" --hidden-import=colorama "./server.py" && make zip-emu

# Pushes CODE only. GitHub will see the code, build it, and create the release.
publish:
	git add .
	git commit -m "New Release Update"
	git push origin main
