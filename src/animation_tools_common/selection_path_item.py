from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPen, QColor
from PySide6.QtWidgets import QGraphicsPathItem, QGraphicsRectItem

class SelectionPathItem(QGraphicsPathItem):
    def __init__(self):
        super().__init__()
        # 点線のペンを設定
        self.pen = QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine)
        self.pen.setDashOffset(0)
        self.dash_offset = 0
        
        # アニメーションタイマーの設定
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.updateDashOffset)
        self.animation_timer.setInterval(50)  # 50msごとに更新
        
        self.setPen(self.pen)
        self.setBrush(QColor(0, 120, 215, 30))  # 半透明の青色
        self.setZValue(1000)  # 他のアイテムより上に表示
        self.hide()

    def updateDashOffset(self):
        self.dash_offset -= 1
        self.pen.setDashOffset(self.dash_offset)
        self.setPen(self.pen)
        self.update()

    def startAnimation(self):
        self.animation_timer.start()
        self.show()

    def stopAnimation(self):
        self.animation_timer.stop()
        self.hide()

class SelectionRectItem(QGraphicsRectItem):
    def __init__(self):
        super().__init__()
        # 点線のペンを設定
        self.pen = QPen(QColor(0, 120, 215), 1, Qt.PenStyle.DashLine)
        self.pen.setDashOffset(0)
        self.dash_offset = 0
        
        # アニメーションタイマーの設定
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.updateDashOffset)
        self.animation_timer.setInterval(50)  # 50msごとに更新
        
        self.setPen(self.pen)
        self.setBrush(QColor(0, 120, 215, 30))  # 半透明の青色
        self.setZValue(1000)  # 他のアイテムより上に表示
        self.hide()

    def updateDashOffset(self):
        self.dash_offset -= 1
        self.pen.setDashOffset(self.dash_offset)
        self.setPen(self.pen)
        self.update()

    def startAnimation(self):
        self.animation_timer.start()
        self.show()

    def stopAnimation(self):
        self.animation_timer.stop()
        self.hide() 