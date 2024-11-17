from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QGraphicsScene, QGraphicsSceneMouseEvent
from .base_tool import BaseTool
from ..region_item_v2 import RegionItem

class RegionTool(BaseTool):
    """領域作成機能を提供するツール"""
    
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.start_pos: QPointF | None = None
        self.current_region: RegionItem | None = None
        self._region_count = 0
        self.MIN_WIDTH = 50  # ピクセル
        self.MIN_HEIGHT = 50  # ピクセル
    
    def setup(self) -> None:
        """ツールのセットアップ処理"""
        pass
    
    def cleanup(self) -> None:
        """ツールの状態をクリアする処理"""
        self.start_pos = None
        self.current_region = None
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        """マウスプレスイベントの処理"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.start_pos = event.scenePos()
            
            # 初期サイズ0の領域を作成
            initial_rect = QRectF(self.start_pos, self.start_pos)
            self._region_count += 1
            self.current_region = RegionItem(
                f"region_{self._region_count}",
                initial_rect,
                f"領域{self._region_count}"
            )
            self.scene.addItem(self.current_region)
            return True
        return False
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        """マウス移動イベントの処理"""
        if event.buttons() & Qt.MouseButton.LeftButton and self.start_pos and self.current_region:
            # 領域のサイズを更新
            rect = QRectF(self.start_pos, event.scenePos()).normalized()
            self.current_region.setPos(rect.topLeft())
            self.current_region.setRect(QRectF(0, 0, rect.width(), rect.height()))
            return True
        return False
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        """マウスリリースイベントの処理"""
        if event.button() == Qt.MouseButton.LeftButton and self.start_pos:
            if self.current_region:
                rect = QRectF(self.start_pos, event.scenePos()).normalized()
                
                # 最小サイズチェック
                if rect.width() < self.MIN_WIDTH or rect.height() < self.MIN_HEIGHT:
                    # 最小サイズ未満の場合、領域アイテムを削除
                    self.scene.removeItem(self.current_region)
                else:
                    # 十分なサイズがある場合は領域を確定
                    self.current_region.setPos(rect.topLeft())
                    self.current_region.setRect(QRectF(0, 0, rect.width(), rect.height()))
                
            self.start_pos = None
            self.current_region = None
            return True
        return False
    
    def keyPressEvent(self, event: QKeyEvent) -> bool:
        return False

    def keyReleaseEvent(self, event: QKeyEvent) -> bool:
        return False 