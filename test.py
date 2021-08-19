"""This is a file for debugging modules"""


from PyQt5.QtWidgets import QApplication
import sys

from cutlistgenerator.ui.cutjobdialog import CutJobDialog

app = QApplication(sys.argv)
win = CutJobDialog()
win.show()
sys.exit(app.exec_())