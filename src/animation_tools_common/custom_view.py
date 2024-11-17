from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QPainter, QDropEvent, QResizeEvent, QWheelEvent, QDragEnterEvent, QTransform
from PySide6.QtWidgets import QGraphicsView, QWidget, QGraphicsScene, QGraphicsRectItem
from PySide6.QtCore import QRectF
import random

class CustomBaseGraphicsView(QGraphicsView):
    xdts_dropped = Signal(str)
    image_dropped = Signal(str)  # 新しいシグナルを追加
    
    def __init__(self, parent:QWidget|None=None):
        super().__init__(parent)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # レンダリング品質を設定
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)

        # ビューポートの更新モードを設定
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)

        # トランスフォーメーションモードを設定
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        # デフォルトのドラッグモードをRubberBandDragに変更
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        self.setAcceptDrops(True)

        # 背景色をグレーに設定
        self.setBackgroundBrush(Qt.GlobalColor.lightGray)

    def dragEnterEvent(self, event:QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            for url in urls:
                file_path = url.toLocalFile()
                if file_path.endswith('.xdts') or file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                    event.acceptProposedAction()
                    return
        event.ignore()

    def dropEvent(self, event:QDropEvent):
        urls = event.mimeData().urls()
        for url in urls:
            file_path = url.toLocalFile()
            if file_path.endswith('.xdts'):
                self.xdts_dropped.emit(file_path)
            elif file_path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')):
                self.image_dropped.emit(file_path)
        event.acceptProposedAction()

    def resizeEvent(self, event:QResizeEvent) -> None:
        return super().resizeEvent(event)

    def fitSceneInView(self):
        if self.scene().itemsBoundingRect().isValid():
            target_rect = self.scene().itemsBoundingRect()
            view_rect = self.viewport().rect()

            scale_x = view_rect.width() / target_rect.width()
            scale_y = view_rect.height() / target_rect.height()
            scale = min(scale_x, scale_y)
            transform = QTransform()
            transform.scale(scale, scale)
            self.setTransform(transform)

    def wheelEvent(self, event:QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            factor = 1.2
            if event.angleDelta().y() < 0:
                factor = 1.0 / factor
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)

    # 新しいキーイベントハンドラーを追加
    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space:
            self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
        super().keyReleaseEvent(event)

# 使用例
if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication, QMainWindow
    import sys

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.view = CustomBaseGraphicsView(self)
            self.setCentralWidget(self.view)
            
            # シーンの作成と設定
            self.scene = QGraphicsScene()
            self.view.setScene(self.scene)
            
            # ランダムな矩形アイテムを追加
            for _ in range(10):  # 10個の矩形を作成
                rect_item = QGraphicsRectItem()
                # ランダムなサイズ（50-150のランダムな値）
                width = random.randint(50, 150)
                height = random.randint(50, 150)
                # ランダムな位置（-400から400の範囲）
                x = random.randint(-400, 400)
                y = random.randint(-400, 400)
                
                rect_item.setRect(QRectF(x, y, width, height))
                self.scene.addItem(rect_item)
            
            # ビューをシーンに合わせる
            self.view.fitSceneInView()
            
            self.view.xdts_dropped.connect(self.handle_xdts_drop)
            self.view.image_dropped.connect(self.handle_image_drop)

        def handle_xdts_drop(self, file_path:str):
            print(f"XDTSファイルがドロップされました: {file_path}")

        def handle_image_drop(self, file_path:str):
            print(f"画像ファイルがドロップされました: {file_path}")

    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(100, 100, 800, 600)
    window.show()
    sys.exit(app.exec())
