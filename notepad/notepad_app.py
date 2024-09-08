import sys
from abc import ABCMeta

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QFileDialog, QColorDialog, QApplication
from notepad.ui.notepad_ui import Ui_MainWindow


class Controller(metaclass=ABCMeta):
    def connect(self):
        pass


class NotepadApp(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # UI 초기화

        self.menu_bar = MenuBar(self)
        self.font_controller = FontController(self)
        self.text_editor_controller = TextEditorController(self)
        self.text_align_controller = TextAlignController(self)
        self.file_controller = FileController(self)

        self.menu_bar.connect()
        self.font_controller.connect()
        self.text_editor_controller.connect()
        self.text_align_controller.connect()
        self.file_controller.connect()


class MenuBar(Controller):
    def __init__(self, notepad_app: NotepadApp):
        self.notepad_app = notepad_app

    def connect(self):
        self.notepad_app.fileOpenAction.triggered.connect(self.open_file)
        self.notepad_app.saveAction.triggered.connect(self.save_file)
        self.notepad_app.otherNameSaveAction.triggered.connect(self.save_file_as)
        self.notepad_app.plusAction.triggered.connect(self.zoom_in)
        self.notepad_app.minusAction.triggered.connect(self.zoom_out)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self.notepad_app, "Open File", "",
                                                   "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    content = f.read()
                    self.notepad_app.textEdit.setText(content)
            except Exception as e:
                QMessageBox.warning(self.notepad_app, "Error", f"Cannot open file: {e}")

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self.notepad_app, "Save File", "",
                                                   "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    content = self.notepad_app.textEdit.toPlainText()
                    f.write(content)
            except Exception as e:
                QMessageBox.warning(self.notepad_app, "Error", f"Cannot save file: {e}")

    def save_file_as(self):

        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(
            self.notepad_app, "Save As", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_name:
            self.notepad_app.current_file = file_name
            self.save_to_file(file_name)


    def save_to_file(self, file_name):
        content = self.notepad_app.textEdit.toPlainText()
        with open(file_name, 'w') as file:
            file.write(content)
        QMessageBox.information(self.notepad_app, "File Saved", f"File saved to {file_name}")

    def zoom_in(self):
        current_font = self.notepad_app.textEdit.font()
        current_font.setPointSize(current_font.pointSize() + 1)
        self.notepad_app.textEdit.setFont(current_font)


    def zoom_out(self):
        current_font = self.notepad_app.textEdit.font()
        current_font.setPointSize(max(1, current_font.pointSize() - 1))  # Avoid negative font size
        self.notepad_app.textEdit.setFont(current_font)

class FontController(Controller):
    MIN_FONT_SIZE = 0
    MAX_FONT_SIZE = 100

    def __init__(self, notepad_app: NotepadApp):
        self.notepad_app = notepad_app

    def connect(self):
        self.notepad_app.fontComboBox.currentFontChanged.connect(self.font_changed)
        self.notepad_app.sizeBox.valueChanged.connect(self.font_size_changed)

    def font_changed(self, font):
        cursor = self.notepad_app.textEdit.textCursor()
        if not cursor.hasSelection():
            char_format = self.notepad_app.textEdit.currentCharFormat()
            char_format.setFont(font)
            self.notepad_app.textEdit.setCurrentCharFormat(char_format)
            return

        fmt = cursor.charFormat()
        fmt.setFont(font)
        cursor.setCharFormat(fmt)

    def font_size_changed(self, size):
        cursor = self.notepad_app.textEdit.textCursor()
        size = max(self.MIN_FONT_SIZE, min(size, self.MAX_FONT_SIZE))

        if not cursor.hasSelection():
            char_format = self.notepad_app.textEdit.currentCharFormat()
            char_format.setFontPointSize(size)
            self.notepad_app.textEdit.setCurrentCharFormat(char_format)
        else:
            fmt = cursor.charFormat()
            fmt.setFontPointSize(size)
            cursor.setCharFormat(fmt)


class TextEditorController(Controller):
    def __init__(self, notepad_app: NotepadApp):
        self.notepad_app = notepad_app

    def connect(self):
        self.notepad_app.boldButton.clicked.connect(self.make_bold)
        self.notepad_app.italicButton.clicked.connect(self.make_italic)
        self.notepad_app.lineButton.clicked.connect(self.make_underline)
        self.notepad_app.cancelLineButton.clicked.connect(self.make_strikethrough)
        self.notepad_app.colorButton.clicked.connect(self.change_text_color)

    def make_bold(self):
        if self.notepad_app.textEdit.fontWeight() == QFont.Bold:
            self.notepad_app.textEdit.setFontWeight(QFont.Normal)
        else:
            self.notepad_app.textEdit.setFontWeight(QFont.Bold)

    def make_italic(self):
        state = self.notepad_app.textEdit.fontItalic()
        self.notepad_app.textEdit.setFontItalic(not state)

    def make_underline(self):
        state = self.notepad_app.textEdit.fontUnderline()
        self.notepad_app.textEdit.setFontUnderline(not state)

    def make_strikethrough(self):
        fmt = self.notepad_app.textEdit.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        cursor = self.notepad_app.textEdit.textCursor()
        cursor.mergeCharFormat(fmt)

    def change_text_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.notepad_app.textEdit.setTextColor(color)


class TextAlignController(Controller):
    def __init__(self, notepad_app: NotepadApp):
        self.notepad_app = notepad_app

    def connect(self):
        self.notepad_app.leftAlignButton.clicked.connect(self.align_left)
        self.notepad_app.centerAlignButton.clicked.connect(self.align_center)
        self.notepad_app.rightAlignButton.clicked.connect(self.align_right)
        self.notepad_app.betweenAlignButton.clicked.connect(self.align_justify)

    def align_left(self):
        self.notepad_app.textEdit.setAlignment(Qt.AlignLeft)

    def align_center(self):
        self.notepad_app.textEdit.setAlignment(Qt.AlignCenter)

    def align_right(self):
        self.notepad_app.textEdit.setAlignment(Qt.AlignRight)

    def align_justify(self):
        self.notepad_app.textEdit.setAlignment(Qt.AlignJustify)


class FileController(Controller):
    def __init__(self, notepad_app: NotepadApp):
        self.notepad_app = notepad_app

    def connect(self):
        self.notepad_app.openFileButton.clicked.connect(self.open_file)
        self.notepad_app.saveButton.clicked.connect(self.save_file)

    def open_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self.notepad_app, "Open File", "",
                                                   "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'r') as f:
                    content = f.read()
                    self.notepad_app.textEdit.setText(content)
            except Exception as e:
                QMessageBox.warning(self.notepad_app, "Error", f"Cannot open file: {e}")

    def save_file(self):
        file_name, _ = QFileDialog.getSaveFileName(self.notepad_app, "Save File", "",
                                                   "Text Files (*.txt);;All Files (*)")
        if file_name:
            try:
                with open(file_name, 'w') as f:
                    content = self.notepad_app.textEdit.toPlainText()
                    f.write(content)
            except Exception as e:
                QMessageBox.warning(self.notepad_app, "Error", f"Cannot save file: {e}")



class Application:
    @classmethod
    def run(cls):
        app = QApplication(sys.argv)
        window = NotepadApp()
        window.show()
        sys.exit(app.exec_())
