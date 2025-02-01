.PHONY: build


reset:
	rm -rf ./dist && rm -rf ./build && rm -rf adbConnector.zip

clean:
	rm -rf ./build && rm -rf adbConnector.spec

zip-adb:
	zip -j adbConnector.zip E:/vscode_workspace/adb/dist/adbConnector.exe

build:
	make reset && pyinstaller --noconfirm --onefile --console --name "adbConnector" --hide-console "hide-early"  "E:/vscode_workspace/adb/server.py" && make zip-adb && make clean

push:
	git add . && git commit -m "try again" && git push origin main

push-for-publish:
	git add . && git commit -m "publish" && git push origin main

publish:
	make build && make push-for-publish

