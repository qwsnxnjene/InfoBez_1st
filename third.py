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
        self.setWindowTitle("Шифр Виженера с взломом (Kasiski)")
        self.setGeometry(100, 100, 800, 700)

        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Кнопка выбора файла
        self.file_btn = QPushButton("Выбрать файл")
        self.file_btn.clicked.connect(self.select_file)
        layout.addWidget(self.file_btn)

        # Поле с текстом файла
        layout.addWidget(QLabel("Текст файла:"))
        self.orig_text = QTextEdit()
        self.orig_text.setReadOnly(True)
        layout.addWidget(self.orig_text)

        # Выбор языка
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

        # Поле для ключа
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("Ключ:"))
        self.key_edit = QLineEdit("ключ")
        key_layout.addWidget(self.key_edit)
        layout.addLayout(key_layout)

        # Кнопка зашифровать
        self.encrypt_btn = QPushButton("Зашифровать")
        self.encrypt_btn.clicked.connect(self.encrypt)
        layout.addWidget(self.encrypt_btn)

        # Поле с зашифрованным текстом
        layout.addWidget(QLabel("Зашифрованный текст:"))
        self.cipher_text = QTextEdit()
        self.cipher_text.setReadOnly(True)
        layout.addWidget(self.cipher_text)

        # Кнопка взлом
        self.crack_btn = QPushButton("Взлом")
        self.crack_btn.clicked.connect(self.crack)
        layout.addWidget(self.crack_btn)

        # Поле с расшифрованным текстом
        layout.addWidget(QLabel("Расшифрованный текст:"))
        self.dec_text = QTextEdit()
        self.dec_text.setReadOnly(True)
        layout.addWidget(self.dec_text)

        # Вывод найденного ключа
        layout.addWidget(QLabel("Найденный ключ:"))
        self.found_key_label = QLabel("Не найден")
        layout.addWidget(self.found_key_label)

        # Алфавиты и ожидаемые частые буквы
        self.alphabets = {
            'RU': ruAlphabet,
            'EN': enAlphabet
        }
        self.expected = {
            'RU': 'о',  # Наиболее частая в русском
            'EN': 'e'   # Наиболее частая в английском
        }

        # Загруженный сырой текст (до очистки)
        self.raw_text = ""

    def update_lang(self):
        if self.ru_radio.isChecked():
            self.lang = 'RU'
        else:
            self.lang = 'EN'
        # Переочищаем текст при смене языка
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
        expected = self.expected[self.lang]
        if expected not in alph:
            QMessageBox.warning(self, "Ошибка", "Ожидаемая буква не в алфавите")
            return

        # Шаг 1: Kasiski - найти длину ключа
        key_length = self.kasiski_test(ciphertext, alph)
        if key_length == 0:
            QMessageBox.warning(self, "Ошибка", "Не удалось определить длину ключа")
            return

        # Шаг 2: Для каждой позиции найти сдвиг
        shifts = []
        for i in range(key_length):
            sub_cipher = ciphertext[i::key_length]
            if len(sub_cipher) < 10:  # Минимум символов для анализа
                continue
            shift = self.find_shift(sub_cipher, alph, expected)
            shifts.append(shift)

        if len(shifts) < key_length:
            QMessageBox.warning(self, "Предупреждение", "Недостаточно данных для полного ключа, используется частичный")
            key_length = len(shifts)

        # Шаг 3: Построить ключ
        key_chars = [alph[shift] for shift in shifts]
        found_key = ''.join(key_chars)

        # Шаг 4: Расшифровать
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

        list_of_dists = [dist for dist, count in repeats.items() if count >= 1]
        if not list_of_dists:
            return 0

        max_count = 0
        key_length = 1
        for L in range(2, 21):
            count = sum(1 for d in list_of_dists if d % L == 0)
            if count > max_count or (count == max_count and L > key_length):
                max_count = count
                key_length = L
        return key_length

    def find_shift(self, text, alph, expected):
        freq = collections.Counter(c for c in text if c in alph)
        if not freq:
            return 0
        most_freq = max(freq, key=freq.get)
        shift = (alph.index(most_freq) - alph.index(expected)) % len(alph)
        return shift


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