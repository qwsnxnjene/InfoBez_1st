import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

import design

ruAlphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789"
enAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


class MyApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.russianOption.setChecked(True)
        self.lang = 'RU'
        self.russianOption.clicked.connect(self.updateLanguage)
        self.englishOption.clicked.connect(self.updateLanguage)

        self.keyText.setText("3")
        self.lastEncryptedKey = 3
        self.lastEncryptedLang = 'RU'
        self.encryptButton.clicked.connect(self.encrypt)
        self.decryptButton.clicked.connect(self.decrypt)

    def updateLanguage(self):
        if self.russianOption.isChecked():
            self.lang = 'RU'
            self.englishOption.setChecked(False)
        else:
            self.lang = 'EN'
            self.russianOption.setChecked(False)

    def encrypt(self):
        text = self.inputText.toPlainText()
        self.outputTextW_2.setPlainText("")
        self.outputTextW.setPlainText("")

        if self.check(text):
            offset = self.keyText.text()
            try:
                offset = int(offset)
            except Exception:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Critical)
                msg.setText("Ошибка ввода")
                msg.setInformativeText(f'Некорректное значение ключа')
                msg.setWindowTitle("Ошибка")
                msg.exec_()
                return
            self.lastEncryptedKey = offset
            self.lastEncryptedLang = self.lang
            if self.lang == 'RU':
                encodedText = encryptText(text, ruAlphabet, offset)
            else:
                encodedText = encryptText(text, enAlphabet, offset)
            self.outputTextW.setPlainText(encodedText)

    def check(self, text):
        if self.lang == 'RU':
            for letter in text:
                if letter not in ruAlphabet:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Ошибка ввода")
                    msg.setInformativeText(f'Неверный символ {letter}')
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
                    return False
        else:
            for letter in text:
                if letter not in enAlphabet:
                    msg = QMessageBox()
                    msg.setIcon(QMessageBox.Critical)
                    msg.setText("Ошибка ввода")
                    msg.setInformativeText(f'Неверный символ {letter}')
                    msg.setWindowTitle("Ошибка")
                    msg.exec_()
                    return False
        return True

    def decrypt(self):
        if self.lastEncryptedLang == 'RU':
            decryptedText = decryptText(self.outputTextW.toPlainText(), ruAlphabet, self.lastEncryptedKey)
        else:
            decryptedText = decryptText(self.outputTextW.toPlainText(), enAlphabet, self.lastEncryptedKey)
        self.outputTextW_2.setPlainText(decryptedText)



def encryptText(text, alph, offset):
    final = ''
    for letter in text:
        newIndex = (alph.index(letter) + offset) % len(alph)
        final += alph[newIndex]
    return final

def decryptText(text, alph, offset):
    final = ''
    for letter in text:
        newIndex = (alph.index(letter) - offset) % len(alph)
        final += alph[newIndex]
    return final


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
