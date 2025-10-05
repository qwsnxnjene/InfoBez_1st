import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLineEdit, QLabel, QRadioButton,
                             QButtonGroup, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt


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


class CaesarCracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Шифр Цезаря с взломом")
        self.setGeometry(100, 100, 800, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        self.file_btn = QPushButton("Выбрать файл")
        self.file_btn.clicked.connect(self.select_file)
        layout.addWidget(self.file_btn)

        layout.addWidget(QLabel("Текст файла:"))
        self.orig_text = QTextEdit()
        self.orig_text.setReadOnly(True)
        layout.addWidget(self.orig_text)

        lang_layout = QHBoxLayout()
        lang_group = QButtonGroup()
        self.ru_radio = QRadioButton("RU")
        self.en_radio = QRadioButton("EN")
        lang_group.addButton(self.ru_radio)
        lang_group.addButton(self.en_radio)
        self.ru_radio.setChecked(True)
        self.lang = 'RU'
        self.ru_radio.toggled.connect(self.update_lang)
        self.en_radio.toggled.connect(self.update_lang)
        lang_layout.addWidget(self.ru_radio)
        lang_layout.addWidget(self.en_radio)
        layout.addLayout(lang_layout)

        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Ключ:"))
        self.key_edit = QLineEdit("3")
        key_layout.addWidget(self.key_edit)
        layout.addLayout(key_layout)

        self.encrypt_btn = QPushButton("Зашифровать")
        self.encrypt_btn.clicked.connect(self.encrypt)
        layout.addWidget(self.encrypt_btn)

        layout.addWidget(QLabel("Зашифрованный текст:"))
        self.cipher_text = QTextEdit()
        self.cipher_text.setReadOnly(True)
        layout.addWidget(self.cipher_text)

        self.crack_btn = QPushButton("Взлом")
        self.crack_btn.clicked.connect(self.crack)
        layout.addWidget(self.crack_btn)

        layout.addWidget(QLabel("Расшифрованный текст:"))
        self.dec_text = QTextEdit()
        self.dec_text.setReadOnly(True)
        layout.addWidget(self.dec_text)

        layout.addWidget(QLabel("Найденный ключ:"))
        self.found_key_label = QLabel("0")
        layout.addWidget(self.found_key_label)

        self.alphabets = {
            'RU': ruAlphabet,
            'EN': enAlphabet
        }
        self.expected = {
            'RU': 'о',
            'EN': 'e'
        }

        self.raw_text = ""

    def update_lang(self):
        if self.ru_radio.isChecked():
            self.lang = 'RU'
        else:
            self.lang = 'EN'

        if self.raw_text:
            self.clean_and_display()

    def select_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Выбрать файл', '', 'Text files (*.txt)')
        if fname:
            try:
                with open(fname, 'r', encoding='utf-8') as f:
                    self.raw_text = f.read()
                self.clean_and_display()
            except Exception as e:
                QMessageBox.warning(self, "Ошибка", f"Не удалось прочитать файл: {e}")

    def clean_and_display(self):
        if not self.raw_text:
            return
        alph = self.alphabets[self.lang]
        cleaned = ''.join(c for c in self.raw_text if c in alph)
        self.orig_text.setPlainText(cleaned)

    def encrypt(self):
        text = self.orig_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Загрузите файл и очистите текст")
            return
        offset_str = self.key_edit.text()
        alph = self.alphabets[self.lang]
        try:
            offset = str_mod(offset_str, len(alph))
            if offset is False:
                raise Exception
        except Exception:
            QMessageBox.warning(self, "Ошибка", "Некорректное значение ключа")
            return
        encoded = encryptText(text, alph, offset)
        self.cipher_text.setPlainText(encoded)

    def crack(self):
        ciphertext = self.cipher_text.toPlainText()
        if not ciphertext:
            QMessageBox.warning(self, "Ошибка", "Зашифруйте текст сначала")
            return
        alph = self.alphabets[self.lang]
        expected = self.expected[self.lang]
        if expected not in alph:
            QMessageBox.warning(self, "Ошибка", "Ожидаемая буква не в алфавите")
            return

        freq = {c: 0 for c in alph}
        for c in ciphertext:
            if c in freq:
                freq[c] += 1

        most_freq = max(freq, key=freq.get)
        if freq[most_freq] == 0:
            QMessageBox.warning(self, "Ошибка", "Текст пустой или без букв")
            return

        shift = (alph.index(most_freq) - alph.index(expected)) % len(alph)
        decrypted = decryptText(ciphertext, alph, shift)
        self.dec_text.setPlainText(decrypted)
        self.found_key_label.setText(str(shift))


def encryptText(text, alph, offset):
    final = ''
    for letter in text:
        if letter in alph:
            newIndex = (alph.index(letter) + offset) % len(alph)
            final += alph[newIndex]
        else:
            final += letter
    return final


def decryptText(text, alph, offset):
    final = ''
    for letter in text:
        if letter in alph:
            newIndex = (alph.index(letter) - offset) % len(alph)
            final += alph[newIndex]
        else:
            final += letter
    return final


def main():
    app = QApplication(sys.argv)
    window = CaesarCracker()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()