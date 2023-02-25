import sys

from PySide2 import QtWidgets
from PySide2.QtUiTools import QUiLoader

loader = QUiLoader()
app = QtWidgets.QApplication(sys.argv)
main = loader.load("mockup.ui", None)
main.show()
app.exec_()
