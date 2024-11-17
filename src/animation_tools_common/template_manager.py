from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLineEdit, QPushButton, QListWidget, 
                             QMessageBox, QComboBox, QLabel, QDialog)
from PySide6.QtCore import Qt, Signal
from typing import List, Set

class TemplateManager:
    def __init__(self):
        # デフォルトの予約語とテンプレートを設定
        self._reserved_words: Set[str] = set(["{TITLE}", "{SCENE}", "{CUT}"])
        self._templates: List[str] = [
            "{TITLE}_{SCENE:2}_{CUT:3}",
            "{TITLE}_s{SCENE:2}_c{CUT:3}"
        ]

    @property
    def reserved_words(self) -> Set[str]:
        return self._reserved_words

    @property
    def templates(self) -> List[str]:
        return self._templates

    def add_reserved_word(self, word: str) -> bool:
        if not word:
            return False
        # 桁数指定がある場合の処理を追加
        if ":" in word:
            base_word, digits = word.split(":")
            if not digits.isdigit():
                return False
            formatted_word = "{" + base_word + ":" + digits + "}"
        else:
            formatted_word = "{" + word + "}"
        
        if formatted_word not in self._reserved_words:
            self._reserved_words.add(formatted_word)
            return True
        return False

    def remove_reserved_word(self, word: str) -> bool:
        if word in self._reserved_words:
            self._reserved_words.remove(word)
            return True
        return False

    def add_template(self, template: str) -> bool:
        if not template:
            return False
        # テンプレートに少なくとも1つの予約語が含まれているかチェック
        if any(word in template for word in self._reserved_words):
            if template not in self._templates:
                self._templates.append(template)
                return True
        return False

    def remove_template(self, template: str) -> bool:
        if template in self._templates:
            self._templates.remove(template)
            return True
        return False

class TemplateOptionsDialog(QDialog):
    def __init__(self, template_manager: TemplateManager, allow_reserved_word_edit=True, parent=None):
        super().__init__(parent)
        self.template_manager = template_manager
        self.allow_reserved_word_edit = allow_reserved_word_edit
        self.setWindowTitle("テンプレートオプション")
        self.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(self)
        layout.addWidget(self._create_options_widget())
        
        # OKとキャンセルボタン
        buttons_layout = QHBoxLayout()
        ok_button = QPushButton("OK")
        cancel_button = QPushButton("キャンセル")
        ok_button.clicked.connect(self.accept)
        cancel_button.clicked.connect(self.reject)
        buttons_layout.addWidget(ok_button)
        buttons_layout.addWidget(cancel_button)
        layout.addLayout(buttons_layout)

    def _create_options_widget(self):
        options_widget = QWidget()
        options_layout = QVBoxLayout(options_widget)

        # 予約語セクション
        reserved_word_section = QWidget()
        reserved_word_layout = QVBoxLayout(reserved_word_section)

        if self.allow_reserved_word_edit:
            # 予約語の登録用ウィジェット
            reserved_word_layout.addWidget(QLabel("予約語の登録"))
            reserved_word_layout.addWidget(QLabel("※ 桁数指定する場合は「WORD:n」の形式で入力 (例: SCENE:3)"))
            reserved_layout = QHBoxLayout()
            self.reserved_input = QLineEdit()
            self.reserved_input.setPlaceholderText("予約語を入力 (例: TITLE または SCENE:3)")
            add_reserved_button = QPushButton("予約語を追加")
            add_reserved_button.clicked.connect(self._add_reserved_word)
            reserved_layout.addWidget(self.reserved_input)
            reserved_layout.addWidget(add_reserved_button)
            reserved_word_layout.addLayout(reserved_layout)

        # 予約語ボタンセクション（編集不可の場合でも表示）
        reserved_word_layout.addWidget(QLabel("利用可能な予約語"))
        self.reserved_buttons_widget = QWidget()
        self.reserved_buttons_layout = QHBoxLayout(self.reserved_buttons_widget)
        self.reserved_buttons_layout.setSpacing(5)
        self._update_reserved_buttons()
        reserved_word_layout.addWidget(self.reserved_buttons_widget)

        options_layout.addWidget(reserved_word_section)

        # テンプレートセクション
        options_layout.addWidget(QLabel("テンプレートの登録"))
        template_layout = QHBoxLayout()
        self.template_input = QLineEdit()
        self.template_input.setPlaceholderText("{TITLE}_S{SCENE}_C{CUT}")
        add_template_button = QPushButton("追加")
        add_template_button.clicked.connect(self._add_template)
        template_layout.addWidget(self.template_input)
        template_layout.addWidget(add_template_button)
        options_layout.addLayout(template_layout)

        self.template_list = QListWidget()
        self.template_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        for template in self.template_manager.templates:
            self.template_list.addItem(template)
        options_layout.addWidget(self.template_list)

        delete_template_button = QPushButton("選択したテンプレートを削除")
        delete_template_button.clicked.connect(self._delete_template)
        options_layout.addWidget(delete_template_button)

        return options_widget

    def _update_reserved_buttons(self):
        # 既存のボタンをクリア
        for i in reversed(range(self.reserved_buttons_layout.count())): 
            self.reserved_buttons_layout.itemAt(i).widget().setParent(None)

        # 予約語ごとにボタンを作成
        for word in self.template_manager.reserved_words:
            button = QPushButton(word)
            button.clicked.connect(lambda checked, w=word: self._insert_reserved_word(w))
            if not self.allow_reserved_word_edit:
                # 編集不可の場合は、ボタンのスタイルを変更して区別
                button.setStyleSheet("QPushButton { background-color: #f0f0f0; }")
            self.reserved_buttons_layout.addWidget(button)

    def _insert_reserved_word(self, word: str):
        current_text = self.template_input.text()
        cursor_pos = self.template_input.cursorPosition()
        new_text = current_text[:cursor_pos] + word + current_text[cursor_pos:]
        self.template_input.setText(new_text)
        self.template_input.setFocus()
        # カーソルを挿入した予約語の後ろに移動
        self.template_input.setCursorPosition(cursor_pos + len(word))

    def _add_reserved_word(self):
        word = self.reserved_input.text().strip()
        if self.template_manager.add_reserved_word(word):
            self._update_reserved_buttons()
            self.reserved_input.clear()

    def _delete_reserved_word(self):
        # この関数は不要になったため削除可能です
        pass

    def _add_template(self):
        template = self.template_input.text().strip()
        if self.template_manager.add_template(template):
            self.template_list.addItem(template)
            self.template_input.clear()
        else:
            QMessageBox.warning(
                self,
                "エラー",
                "テンプレートには少なくとも1つの予約語を含める必要があります。",
                QMessageBox.StandardButton.Ok
            )

    def _delete_template(self):
        current_item = self.template_list.currentItem()
        if current_item:
            template = current_item.text()
            if self.template_manager.remove_template(template):
                self.template_list.takeItem(self.template_list.row(current_item))

class TemplateManagerWidget(QWidget):
    template_changed = Signal(str)
    def __init__(self, parent: QWidget | None = None, allow_reserved_word_edit: bool = True):
        super().__init__(parent)
        self.template_manager = TemplateManager()
        self.allow_reserved_word_edit = allow_reserved_word_edit
        
        layout = QHBoxLayout(self)
        
        # テンプレート選択コンボボックス
        layout.addWidget(QLabel("テンプレート:"))
        self.template_combo = QComboBox()
        self.template_combo.setMinimumWidth(200)
        self.template_combo.currentTextChanged.connect(self.template_changed.emit)
        layout.addWidget(self.template_combo)
        
        # オプションボタン
        self.options_button = QPushButton("オプション...")
        self.options_button.clicked.connect(self._show_options)
        layout.addWidget(self.options_button)
        
        # 初期テンプレートの設定
        self._update_template_combo()

    def _show_options(self):
        dialog = TemplateOptionsDialog(
            self.template_manager, 
            allow_reserved_word_edit=self.allow_reserved_word_edit,
            parent=self
        )
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self._update_template_combo()

    def _update_template_combo(self):
        self.template_combo.clear()
        self.template_combo.addItems(self.template_manager.templates)

    def get_selected_template(self) -> str:
        return self.template_combo.currentText()

# 使用例
if __name__ == "__main__":
    app = QApplication([])
    
    # メインウィンドウの作成
    window = QMainWindow()
    window.setWindowTitle("テンプレート管理デモ")
    window.setMinimumSize(400, 100)
    
    # TemplateManagerWidgetを配置
    template_widget = TemplateManagerWidget(allow_reserved_word_edit=False)
    window.setCentralWidget(template_widget)
    
    window.show()
    app.exec() 