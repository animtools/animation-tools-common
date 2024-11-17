from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QGraphicsRectItem, QWidget, QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QObject, QSizeF
from PySide6.QtGui import QFont, QColor, QPen, QBrush, QPainter, QUndoStack
from .convert import qrectf_to_rectf
from .obj import RectF

class RegionItem(QGraphicsRectItem):
    def __init__(self, region_key:str, rect:QRectF=QRectF(0, 0, 400, 300), label:str='', undo_stack:QUndoStack|None=None):
        super().__init__(QRectF(0, 0, rect.width(), rect.height()))
        self.setPos(rect.topLeft())
        self._region_key = region_key
        self._label = label
        self._font = QFont("Arial", 10)
        self._color = Qt.GlobalColor.black
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
    
    def get_region_rect(self)->dict[str, RectF]:
        return {self._region_key: qrectf_to_rectf(self.rect())}

    @property
    def label(self):
        return self._label

    @label.setter
    def label(self, value:str):
        self._label = value
        self.update()

    @property
    def font(self):
        return self._font

    @font.setter
    def font(self, value:QFont):
        self._font = value
        self.update()

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value:QColor):
        self._color = value
        self.update()

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None):
        lod = option.levelOfDetailFromTransform(painter.worldTransform())
        
        # 線の太さをLODに応じて調整
        pen_width = 2 / lod
        handler_size = 10 / lod

        # 矩形の描画
        painter.setPen(QPen(self._color, pen_width))
        fill_color = QColor(self._color)
        
        # 透明度を設定（元の透明度を維持）
        fill_color.setAlpha(51)
        
        # 選択時の描画（背景色を明く）
        if self.isSelected():
            h, s, l, _ = fill_color.getHsl()
            fill_color.setHsl(h, s, min(l + 100, 255), fill_color.alpha())  # 明度を30増加（最大255）
        
        fill_brush = QBrush(fill_color)
        painter.setBrush(fill_brush)
        painter.drawRect(self.rect())
        
        # ラベルの描画
        if self._label:
            font = QFont(self._font)
            font.setPointSizeF(font.pointSizeF() / lod)  # フォントサイズをLODに応じて調整
            painter.setFont(font)
            painter.setPen(self._color)
            
            # テキストの境界矩形を取得
            text_rect = painter.fontMetrics().boundingRect(self._label)
            
            # 矩形内にテキストが収まるかチェック
            if text_rect.width() < self.rect().width() and text_rect.height() < self.rect().height():
                center = self.rect().center()
                text_pos = center - QPointF(text_rect.width() / 2, -text_rect.height() / 2)
                painter.drawText(text_pos, self._label)


    def get_lod(self):
        return self.scene().views()[0].transform().m11() if self.scene() and self.scene().views() else 1

# 使用例
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QGraphicsScene, QGraphicsView
    import sys

    app = QApplication(sys.argv)

    scene = QGraphicsScene()
    view = QGraphicsView(scene)

    region_item = RegionItem("region1", QRectF(0, 0, 200, 150), "テスト領域")
    scene.addItem(region_item)

    view.setSceneRect(0, 0, 400, 300)
    view.show()

    sys.exit(app.exec())
