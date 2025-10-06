import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QPushButton, QTextEdit, QLineEdit, QLabel, QRadioButton,
                             QButtonGroup, QFileDialog, QMessageBox)
from PyQt5.QtCore import Qt
import collections
import math

ruAlphabet = "абвгдеёжзийклмнопрстуфхцчшщъыьэюя0123456789"
enAlphabet = "abcdefghijklmnopqrstuvwxyz0123456789"


class VigenereCracker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Шифр Виженера с взломом")
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
        self.key_edit = QLineEdit("давай")
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
        self.found_key_label = QLabel("Не найден")
        layout.addWidget(self.found_key_label)

        self.alphabets = {
            'RU': ruAlphabet,
            'EN': enAlphabet
        }
        self.expected_freq = {
            'RU': {
                'а': 0.0764, 'б': 0.0201, 'в': 0.0438, 'г': 0.0172, 'д': 0.0309, 'е': 0.0875, 'ё': 0.0020, 'ж': 0.0101, 'з': 0.0148, 'и': 0.0709,
                'й': 0.0121, 'к': 0.0330, 'л': 0.0496, 'м': 0.0317, 'н': 0.0678, 'о': 0.1118, 'п': 0.0247, 'р': 0.0423, 'с': 0.0497, 'т': 0.0609,
                'у': 0.0222, 'ф': 0.0021, 'х': 0.0095, 'ц': 0.0039, 'ч': 0.0140, 'ш': 0.0072, 'щ': 0.0030, 'ъ': 0.0002, 'ы': 0.0236, 'ь': 0.0184,
                'э': 0.0036, 'ю': 0.0047, 'я': 0.0196, '0': 0.0, '1': 0.0, '2': 0.0, '3': 0.0, '4': 0.0, '5': 0.0, '6': 0.0, '7': 0.0, '8': 0.0, '9': 0.0
            },
            'EN': {
                'a': 0.08167, 'b': 0.01492, 'c': 0.02782, 'd': 0.04253, 'e': 0.12702, 'f': 0.02228, 'g': 0.02015, 'h': 0.06094, 'i': 0.06966, 'j': 0.00153,
                'k': 0.00772, 'l': 0.04025, 'm': 0.02406, 'n': 0.06749, 'o': 0.07507, 'p': 0.01929, 'q': 0.00095, 'r': 0.05987, 's': 0.06327, 't': 0.09056,
                'u': 0.02758, 'v': 0.00978, 'w': 0.02360, 'x': 0.00150, 'y': 0.01974, 'z': 0.00074, '0': 0.0, '1': 0.0, '2': 0.0, '3': 0.0, '4': 0.0, '5': 0.0, '6': 0.0, '7': 0.0, '8': 0.0, '9': 0.0
            }
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
        cleaned = ''.join(c.lower() for c in self.raw_text if c.lower() in alph)
        self.orig_text.setPlainText(cleaned)

    def encrypt(self):
        text = self.orig_text.toPlainText()
        if not text:
            QMessageBox.warning(self, "Ошибка", "Загрузите файл и очистите текст")
            return
        key_str = self.key_edit.text().strip().lower()
        if not key_str:
            QMessageBox.warning(self, "Ошибка", "Введите ключ")
            return
        alph = self.alphabets[self.lang]
        if not all(c in alph for c in key_str):
            QMessageBox.warning(self, "Ошибка", "Ключ содержит недопустимые символы")
            return
        encoded = encryptVigenere(text, key_str, alph)
        self.cipher_text.setPlainText(encoded)

    def crack(self):
        ciphertext = self.cipher_text.toPlainText()
        if not ciphertext:
            QMessageBox.warning(self, "Ошибка", "Зашифруйте текст сначала")
            return
        alph = self.alphabets[self.lang]
        expected_freq = self.expected_freq[self.lang]

        key_length = self.kasiski_test(ciphertext, alph)
        if key_length == 0:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить длину ключа")
            return

        shifts = []
        for i in range(key_length):
            sub_cipher = ciphertext[i::key_length]
            if len(sub_cipher) < 10:
                continue
            shift = self.find_shift(sub_cipher, alph, expected_freq)
            shifts.append(shift)

        if len(shifts) < key_length:
            QMessageBox.warning(self, "Предупреждение", "Недостаточно данных для полного ключа, используется частичный")
            key_length = len(shifts)

        key_chars = ''.join(alph[shift] for shift in shifts)
        found_key = ''.join(key_chars)

        decrypted = decryptVigenere(ciphertext, found_key, alph)

        self.dec_text.setPlainText(decrypted)
        self.found_key_label.setText(found_key)

    def kasiski_test(self, text, alph, min_length=4, min_distance=5):
        repeats = collections.defaultdict(int)
        n = len(text)
        for i in range(n - min_length + 1):
            seq = text[i:i + min_length]
            if all(c in alph for c in seq):
                for j in range(i + min_distance, n - min_length + 1):
                    if text[j:j + min_length] == seq:
                        distance = j - i
                        repeats[distance] += 1

        if not repeats:
            return 0

        max_score = 0
        key_length = 1
        for L in range(2, 21):
            score = sum(repeats[dist] for dist in repeats if dist % L == 0)
            if score > max_score or (score == max_score and L < key_length):
                max_score = score
                key_length = L
        return key_length

    def find_shift(self, text, alph, expected_freq):
        len_alph = len(alph)
        min_chi = float('inf')
        best_shift = 0
        total = len(text)
        if total == 0:
            return 0
        for s in range(len_alph):
            counts = collections.Counter()
            for c in text:
                if c in alph:
                    p_index = (alph.index(c) - s) % len_alph
                    p = alph[p_index]
                    counts[p] += 1
            chi = 0.0
            total_letters = sum(counts.values())
            for letter, exp in expected_freq.items():
                obs = counts[letter] / total_letters if total_letters > 0 else 0
                if exp > 0:
                    chi += (obs - exp) ** 2 / exp
                else:
                    if obs > 0:
                        chi += obs ** 2 / 0.0001
            if chi < min_chi:
                min_chi = chi
                best_shift = s
        return best_shift


def encryptVigenere(text, key, alph):
    key = key * (len(text) // len(key) + 1)
    final = ''
    for t, k in zip(text, key):
        if t in alph and k in alph:
            shift = alph.index(k)
            newIndex = (alph.index(t) + shift) % len(alph)
            final += alph[newIndex]
        else:
            final += t
    return final


def decryptVigenere(text, key, alph):
    key = key * (len(text) // len(key) + 1)
    final = ''
    for t, k in zip(text, key):
        if t in alph and k in alph:
            shift = alph.index(k)
            newIndex = (alph.index(t) - shift) % len(alph)
            final += alph[newIndex]
        else:
            final += t
    return final


def main():
    app = QApplication(sys.argv)
    window = VigenereCracker()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()