import sys

from PySide2 import QtWidgets
from PySide2.QtUiTools import QUiLoader


def main():
    loader = QUiLoader()
    app = QtWidgets.QApplication(sys.argv)
    main = loader.load("main.ui", None)
    main.show()
    app.exec_()
