from typing import Optional
from PySide6.QtCore import Qt, QRectF, QPointF
from PySide6.QtGui import QPainterPath, QKeyEvent
from PySide6.QtWidgets import (QGraphicsItem, QGraphicsScene, 
                              QGraphicsSceneMouseEvent)

from ..selection_path_item import SelectionPathItem
from .base_tool import BaseTool

class SelectTool(BaseTool):
    """選択機能を提供するツール"""
    
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.selection_start_pos: Optional[QPointF] = None
        self.selection_path_item = SelectionPathItem()
        # self._last_added_items: set[QGraphicsItem] = set()
        self._click_pos: Optional[QPointF] = None  # クリック位置を保存
    
    def setup(self) -> None:
        """ツールがアクティブになった時の処理"""
        if hasattr(self, 'selection_path_item'):
            self.scene.addItem(self.selection_path_item)
    
    def cleanup(self) -> None:
        """ツールの状態をクリアする処理"""
        # 選択ツールが非アクティブになったら、アイテムを選択不可に
        if hasattr(self, 'selection_path_item'):
            self.selection_path_item.stopAnimation()
            self.selection_path_item.setVisible(False)
            self.selection_path_item.setPath(QPainterPath())
            if self.selection_path_item.scene() == self.scene:
                self.scene.removeItem(self.selection_path_item)
        self.selection_start_pos = None
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        """マウスプレスイベントの処理"""
        if event.button() == Qt.MouseButton.LeftButton:
            self._click_pos = event.scenePos()
            self.selection_start_pos = event.scenePos()
            
            # クリックされたアイテムを取得
            clicked_item = self.scene.itemAt(event.scenePos(), self.scene.views()[0].transform())
            
            if clicked_item and clicked_item != self.selection_path_item:
                # Ctrlキーが押されていない場合は既存の選択をクリア
                if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.scene.clearSelection()
                
                # アイテムを選択状態に
                clicked_item.setSelected(True)
                
                # シーンにsetActiveItemメソッドが存在する場合のみ呼び出し
                # if hasattr(self.scene, 'setActiveItem'):
                #     self.scene.setActiveItem(clicked_item)
            elif not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                # 空白部分をクリックした場合で、Ctrlキーが押されていない場合
                self.scene.clearSelection()
                # if hasattr(self.scene, 'setActiveItem'):
                #     self.scene.setActiveItem(None)
            
            return True
        return False
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        """マウス移動イベントの処理"""
        if event.buttons() & Qt.MouseButton.LeftButton and self.selection_start_pos:
            # マウスが動いた距離をチェック
            move_distance = (event.scenePos() - self._click_pos).manhattanLength()
            
            # 一定距離以上動いた場合のみドラッグ選択を開始
            if move_distance > 3:  # 3ピクセル以上の移動でドラッグ選択開始
                rect = QRectF(self.selection_start_pos, event.scenePos()).normalized()
                path = QPainterPath()
                path.addRect(rect)
                self.selection_path_item.setPath(path)
                self.selection_path_item.setVisible(True)
                
                # 選択範囲内のアイテムを取得
                items = [item for item in self.scene.items(rect) 
                        if item != self.selection_path_item]# and item.isSelectable()]
                
                # Ctrlキーが押されていない場合は既存の選択をクリア
                if not event.modifiers() & Qt.KeyboardModifier.ControlModifier:
                    self.scene.clearSelection()
                    # self._last_added_items.clear()
                
                # 選択範囲内の全アイテムを選択状態に
                for item in items:
                    # if not item.isSelected():
                        # self._last_added_items.add(item)
                    item.setSelected(True)
                
                # # 最後に追加されたアイテムをアクティブに
                # if self._last_added_items and hasattr(self.scene, 'setActiveItem'):
                #     self.scene.setActiveItem(list(self._last_added_items)[-1])
            
            return True
        return False
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        """マウスリリースイベントの処理"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.selection_path_item.setVisible(False)
            self.selection_path_item.setPath(QPainterPath())
            self.selection_start_pos = None
            self._click_pos = None
            # self._last_added_items.clear()
            return True
        return False
    
    def keyPressEvent(self, event: QKeyEvent) -> bool:
        """キープレスイベントの処理"""
        # 必要に応じてキーボードショートカットなどを実装
        return False

    def keyReleaseEvent(self, event: QKeyEvent) -> bool:
        return False

