.PHONY: build

remove-build:
	rm -rf ./build && rm -rf ./output


build:
	make remove-build && pyinstaller --onefile --noconsole --distpath ./output/ --name adbConnector server.py
