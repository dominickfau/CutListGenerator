"""This is a file for debugging modules"""


# from PyQt5.QtWidgets import QApplication
# import sys

# from cutlistgenerator.ui.cutjobdialog import CutJobDialog

# app = QApplication(sys.argv)
# win = CutJobDialog()
# win.show()
# sys.exit(app.exec_())

from domonic.html import *
from xhtml2pdf import pisa

# Define your data
output_filename = "test.pdf"
source_html = render(
    html(
        body(
            div("hello world"),
            a("this is a link", _href="http://www.somesite.com", _style="font-size:10px;"),
            ol(''.join([f'{li()}' for thing in range(5)])),
            h1("test", _class="test"),
        )
    )
)

# Utility function
def convert_html_to_pdf(source_html, output_filename):
    # open output file for writing (truncated binary)
    result_file = open(output_filename, "w+b")

    # convert HTML to PDF
    pisa_status = pisa.pisaDocument(
            source_html,                # the HTML to convert
            dest=result_file)           # file handle to recieve result

    # close output file
    result_file.close()                 # close output file

    # return False on success and True on errors
    return pisa_status.err

# Main program
if __name__ == "__main__":
    convert_html_to_pdf(source_html, output_filename)