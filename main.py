import sys
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMessageBox

import design

ruAlphabet = "АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯабвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789"
enAlphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"


def str_mod(s, n):
    if s == "-":
        return False
    res = 0
    negative = False
    for i, ch in enumerate(s):
        if i == 0 and ch == '-':
            negative = True
            continue
        if ch.isdigit():
            res = (res * 10 + int(ch)) % n
        else:
            return false
    return -res if negative else res


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
            offset_str = self.keyText.text()
            if self.lang == 'RU':
                alph = ruAlphabet
            else:
                alph = enAlphabet
            try:
                offset = str_mod(offset_str, len(alph))
                if offset is False:
                    raise Exception
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
            encodedText = encryptText(text, alph, offset)
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
        if (str_mod(self.keyText.text(), len(ruAlphabet)) != self.lastEncryptedKey and self.lang == "RU") or \
                (str_mod(self.keyText.text(), len(enAlphabet)) != self.lastEncryptedKey and self.lang == "EN"):
            print(repr(self.lastEncryptedKey), repr(str_mod(self.keyText.text(), len(ruAlphabet))))
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка ввода")
            msg.setInformativeText(f'Некорректное значение ключа')
            msg.setWindowTitle("Исходное значение ключа не равно нынешнему!")
            msg.exec_()
            return

        if self.lastEncryptedLang == 'RU':
            alph = ruAlphabet
        else:
            alph = enAlphabet
        offset = str_mod(str(self.lastEncryptedKey), len(alph))
        if offset is False:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setText("Ошибка ввода")
            msg.setInformativeText(f'Неверный ключ')
            msg.setWindowTitle("Ошибка")
            msg.exec_()
        decryptedText = decryptText(self.outputTextW.toPlainText(), alph, offset)
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
