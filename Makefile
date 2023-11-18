.PHONY: build

reset:
	rm -rf ./dist && rm -rf ./build && rm -rf adbConnector.zip

clean:
	rm -rf ./build && rm -rf adbConnector.spec

zip-adb:
	zip -j adbConnector.zip C:/programs/adb/dist/adbConnector/adbConnector.exe

build:
	make reset && pyinstaller --noconfirm --onedir --console --name "adbConnector" --hide-console "hide-early"  "C:/programs/adb/server.py" && make zip-adb && make clean

