from PySide6.QtCore import QObject
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent
from PySide6.QtGui import QKeyEvent, QIcon, QKeySequence

class BaseTool(QObject):
    """ツールの基底クラス"""
    
    tool_name: str = ""
    tool_cursor = None  # QCursor型
    tool_icon: QIcon | None = None
    tool_tooltip: str = ""
    tool_shortcut: QKeySequence | str = ""
    
    def __init__(self, scene: QGraphicsScene):
        super().__init__()
        self.scene = scene
        self.is_active = False
        self._setup()
    
    def _setup(self) -> None:
        """ツールの基本設定"""
        pass
    
    def activate(self):
        """ツールがアクティブになった時の処理"""
        self.setup()
        self.is_active = True
    
    def deactivate(self):
        """ツールが非アクティブになった時の処理"""
        self.is_active = False
        self.cleanup()
        
    def cleanup(self) -> None:
        """ツールのクリーンアップ処理"""
        raise NotImplementedError
    
    def setup(self) -> None:
        """ツールのセットアップ処理"""
        raise NotImplementedError
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        return False
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        return False
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        return False
    
    def keyPressEvent(self, event: QKeyEvent) -> bool:
        return False
    
    def keyReleaseEvent(self, event: QKeyEvent) -> bool:
        return False
