.PHONY: build

remove-old:
	rm -rf ./build && rm -rf ./output && rm -rf adbConnector.zip

zip-adb:
	zip -j adbConnector.zip C:/programs/adb/output/adbConnector.exe

build:
	make remove-old && pyinstaller --onefile --noconsole --distpath ./output/ --name adbConnector server.py && make zip-adb

