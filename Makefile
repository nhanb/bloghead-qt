all: src/bloghead/resources.py src/bloghead/djot-server.dist.js

src/bloghead/resources.py:
	pyside2-rcc src/bloghead/resources.qrc -o src/bloghead/resources.py

src/bloghead/djot-server.dist.js: src/js/vendored/djot/LICENSE src/js/vendored/djot/djot.js src/js/djot-server.js
	cat \
		src/js/vendored/djot/LICENSE \
		src/js/vendored/djot/djot.js \
		src/js/djot-server.js \
		> src/bloghead/djot-server.dist.js
