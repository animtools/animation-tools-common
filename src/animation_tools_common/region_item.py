from PySide6.QtWidgets import QGraphicsItem, QStyleOptionGraphicsItem, QWidget, QGraphicsSceneMouseEvent, QGraphicsSceneHoverEvent
from PySide6.QtCore import Qt, QRectF, QPointF, Signal, QObject, QSizeF
from PySide6.QtGui import QFont, QColor, QPen, QBrush, QPainter, QUndoStack
from .convert import qrectf_to_rectf
from .obj import RectF

class RegionItem(QGraphicsItem, QObject):
    props_changed = Signal(QRectF)
    def __init__(self, region_key:str, rect:QRectF=QRectF(0, 0, 400, 300), label:str='', undo_stack:QUndoStack|None=None):
        QGraphicsItem.__init__(self)
        QObject.__init__(self)
        self._region_key = region_key
        self._rect = rect
        self._label = label
        self._font = QFont("Arial", 10)
        self._color = Qt.black
        self.handlers = [QRectF(-5, -5, 10, 10) for _ in range(4)]
        self.update_handlers()
        self.pressed_handler = None
        self.drag_start = None
        self.old_rect = None
        self.undo_stack = undo_stack
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setAcceptHoverEvents(True)
    
    def get_region_rect(self)->dict[str, RectF]:
        return {self._region_key: qrectf_to_rectf(self._rect)}

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
        return self._font

    @color.setter
    def color(self, value:QColor):
        self._color = value
        self.update()

    def rect(self):
        return QRectF(self._rect)
    
    def setRect(self, rect:QRectF):
        self._rect = rect
        self.update_handlers()
        self.update()

    def boundingRect(self):
        return self._rect.adjusted(-10, -10, 10, 10)

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget):
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
        painter.drawRect(self._rect)
        
        # ハンドルの描画
        painter.setBrush(Qt.white)
        painter.setPen(QPen(self._color, pen_width / 2))
        for handler in self.handlers:
            scaled_handler = QRectF(handler.center().x() - handler_size / 2,
                                    handler.center().y() - handler_size / 2,
                                    handler_size, handler_size)
            painter.drawRect(scaled_handler)

        # ラベルの描画
        if self._label:
            font = QFont(self._font)
            font.setPointSizeF(font.pointSizeF() / lod)  # フォントサイズをLODに応じて調整
            painter.setFont(font)
            painter.setPen(self._color)
            text_rect = painter.fontMetrics().boundingRect(self._label)
            center = self._rect.center()
            text_pos = center - QPointF(text_rect.width() / 2, -text_rect.height() / 2)
            painter.drawText(text_pos, self._label)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.ClosedHandCursor)
            self.old_rect = self.rect()
            lod = self.get_lod()
            scaled_handler_size = 10 / lod
            for i, handler in enumerate(self.handlers):
                scaled_handler = QRectF(handler.center().x() - scaled_handler_size / 2,
                                        handler.center().y() - scaled_handler_size / 2,
                                        scaled_handler_size, scaled_handler_size)
                if scaled_handler.contains(event.pos()):
                    self.pressed_handler = i
                    return
            if self._rect.contains(event.pos()):
                self.drag_start = event.pos()
                return
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self.pressed_handler is not None:
            new_pos = event.pos()
            if self.pressed_handler == 0:  # Top-left
                self._rect.setTopLeft(new_pos)
            elif self.pressed_handler == 1:  # Top-right
                self._rect.setTopRight(new_pos)
            elif self.pressed_handler == 2:  # Bottom-left
                self._rect.setBottomLeft(new_pos)
            elif self.pressed_handler == 3:  # Bottom-right
                self._rect.setBottomRight(new_pos)
            # self.update_handlers([self.pressed_handler])
            # self.prepareGeometryChange()
        elif self.drag_start is not None:
            delta = event.pos() - self.drag_start
            self._rect.translate(delta)
            self.drag_start = event.pos()
            
        self.update_handlers()
        self.prepareGeometryChange()

        if self.scene():
            self.scene().update()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if event.button() == Qt.LeftButton:
            self.setCursor(Qt.OpenHandCursor)
            if self.old_rect is not None and self.undo_stack is not None:
                new_rect = self.rect()
                if self.old_rect != new_rect:
                    command = RectChangeCommand(self, self.old_rect, new_rect)
                    self.undo_stack.push(command)
            self.old_rect = None
            if self.pressed_handler is not None or self.drag_start is not None:
                self.props_changed.emit(self.rect())
            self.pressed_handler = None
            self.drag_start = None
        super().mouseReleaseEvent(event)

    def update_handlers(self):
        handler_size = 10
        top_left = self._rect.topLeft()
        top_right = self._rect.topRight()
        bottom_left = self._rect.bottomLeft()
        bottom_right = self._rect.bottomRight()
        offset = QPointF(-handler_size/2, -handler_size/2)
        size = QSizeF(handler_size, handler_size)
        
        self.handlers[0] = QRectF(top_left + offset, size)
        self.handlers[1] = QRectF(top_right + offset, size)
        self.handlers[2] = QRectF(bottom_left + offset, size)
        self.handlers[3] = QRectF(bottom_right + offset, size)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        self.setCursor(Qt.OpenHandCursor)
        super().hoverEnterEvent(event)
    
    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        self.unsetCursor()
        super().hoverLeaveEvent(event)

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        lod = self.get_lod()
        scaled_handler_size = 10 / lod
        for handler in self.handlers:
            scaled_handler = QRectF(handler.center().x() - scaled_handler_size / 2,
                                    handler.center().y() - scaled_handler_size / 2,
                                    scaled_handler_size, scaled_handler_size)
            if scaled_handler.contains(event.pos()):
                self.setCursor(Qt.SizeAllCursor)
                return
        self.setCursor(Qt.OpenHandCursor)
        super().hoverMoveEvent(event)

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
