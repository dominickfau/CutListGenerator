from PyQt5.QtWidgets import QDialog, QMessageBox, QTableWidgetItem


from cutlistgenerator.ui.helpdialog_ui import Ui_Dialog
from cutlistgenerator.logging import FileLogger

logger = FileLogger(__name__)


class HelpDialog(Ui_Dialog, QDialog):
    # TODO: Code this class.
    def __init__(self, parent=None):
        super(Ui_Dialog, self).__init__(parent)
        self.setupUi(self)