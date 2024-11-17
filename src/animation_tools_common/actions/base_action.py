from PySide6.QtGui import QAction, QIcon, QKeySequence
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import QObject

class BaseAction(QAction):
    """アクションの基底クラス"""
    
    action_text: str = ""
    action_icon: QIcon | None = None
    action_shortcut: QKeySequence | str = ''
    action_tooltip: str = ' '
    action_checkable: bool = False
    
    def __init__(self, scene: QGraphicsScene, parent: QObject | None = None):
        super().__init__(parent)
        self.scene = scene
        self._setup()
    
    def _setup(self) -> None:
        """アクションの基本設定"""
        # 基本プロパティの設定
        if hasattr(self, 'action_text'):
            self.setText(self.action_text)
        if hasattr(self, 'action_shortcut'):
            self.setShortcut(self.action_shortcut)
        if hasattr(self, 'action_icon') and self.action_icon:
            if isinstance(self.action_icon, str):
                self.setIcon(QIcon(self.action_icon))
            else:
                self.setIcon(self.action_icon)
        if hasattr(self, 'action_tooltip'):
            self.setToolTip(self.action_tooltip)
        if hasattr(self, 'action_checkable'):
            self.setCheckable(self.action_checkable)
        
        # トリガー時のコールバックを接続
        self.triggered.connect(self.execute)
    
    def execute(self) -> None:
        """アクションの実行処理"""
        raise NotImplementedError