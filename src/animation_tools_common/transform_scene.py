from PySide6.QtCore import Qt, QRectF, QObject, QPointF, Signal, QPoint, QRect, QTimer
from PySide6.QtGui import QBrush, QPen, QColor, QPainter, QTransform, QMouseEvent, QKeyEvent, QPainterPath
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsView, QRubberBand, QGraphicsRectItem, QGraphicsSceneMouseEvent
from .transform_rect_item import TransformRectItem  # GraphicsRectItemをインポート
from .selection_path_item import SelectionPathItem  # SelectionRectItemからSelectionPathItemに変更
import math


class TransformScene(QGraphicsScene):
    itemsTransformed = Signal(list)  # 変換されたアイテムのリストを送信
    itemsMoved = Signal(list)        # 移動されたアイテムのリストを送信
    itemsRotated = Signal(list)      # 回転されたアイテムのリストを送信
    itemsTransformedFinished = Signal(list)  # 変換が完了したアイテムのリストを送信

    def __init__(self, parent: QObject | None = None, movable: bool = True, resizable: bool = True, rotatable: bool = True, keep_aspect_ratio: bool = False):
        super().__init__(parent)
        self._tool = 'select'  # デフォルトは'select'
        self.transform_rect_item = TransformRectItem(QRectF(), movable=movable, resizable=resizable, rotatable=rotatable, keep_aspect_ratio=keep_aspect_ratio)
        self.transform_rect_item.setVisible(False)
        self.transform_rect_item.setZValue(1000)  # 他のアイテムより上に表示
        self.addItem(self.transform_rect_item)
        self.selectionChanged.connect(self.onSelectionChanged)
        self.last_transform_rect: QRectF | None = None
        self.last_transform_pos: QPointF | None = None
        self.last_transform_angle: float | None = None
        self.original_keep_aspect_ratio = keep_aspect_ratio
        # self.itemsTransformedFinished.connect(self.onItemsTransformedFinished)
        
        # 選択範囲表示用のパスアイテムを追加
        self.selection_path_item = SelectionPathItem()
        self.addItem(self.selection_path_item)
        self.selection_start_pos = None
    
    @property
    def tool(self) -> str:
        return self._tool

    @tool.setter
    def tool(self, value: str):
        self._tool = value
        # ツール変更時に選択パスをクリア
        if hasattr(self, 'selection_path_item'):
            self.selection_path_item.stopAnimation()
            self.selection_start_pos = None

    def setMovable(self, movable: bool):
        self.transform_rect_item.setMovable(movable)
    
    def setResizable(self, resizable: bool):
        self.transform_rect_item.setResizable(resizable)
    
    def setRotatable(self, rotatable: bool):
        self.transform_rect_item.setRotatable(rotatable)
    
    def setKeepAspectRatio(self, keep_aspect_ratio: bool):
        self.original_keep_aspect_ratio = keep_aspect_ratio
        self.transform_rect_item.setKeepAspectRatio(keep_aspect_ratio)
    
    def onSelectionChanged(self):
        if self.tool == 'transform':
            self.updateTransformRect()
        else:
            self.transform_rect_item.setVisible(False)
    
    # def onItemsTransformedFinished(self, items: list[QGraphicsItem]):
    #     print(f"変換が完了したアイテム: {items}")

    def updateTransformRect(self):
        selected_items = self.selectedItems()

        if selected_items:
            self.transform_rect_item.setPos(QPointF(0, 0))
            self.transform_rect_item.resetRotation()
            self.transform_rect_item.resetTransformCenter()

            if len(selected_items) == 1:
                item = selected_items[0]
                if self.transform_rect_item.keep_aspect_ratio != self.original_keep_aspect_ratio:
                    self.transform_rect_item.setKeepAspectRatio(self.original_keep_aspect_ratio)
                
                if isinstance(item, QGraphicsRectItem):
                    # 矩形アイテムの場合、変換行列から直接スケールを取得
                    transform = item.transform()

                    # スケール値を計算
                    scale_x = math.sqrt(transform.m11() * transform.m11() + transform.m12() * transform.m12())
                    scale_y = math.sqrt(transform.m21() * transform.m21() + transform.m22() * transform.m22())
                    
                    # 元の矩形を取得し、スケールを適用
                    original_rect = item.rect()
                    rect = QRectF(
                        0, 0,
                        original_rect.width() * scale_x,
                        original_rect.height() * scale_y
                    )
                else:
                    # イテムの変換行列から回転とスケールを取得
                    transform = item.transform()
                    m11 = transform.m11()
                    m12 = transform.m12()
                    m21 = transform.m21()
                    m22 = transform.m22()
                    
                    # スケール値を計算
                    scale_x = math.sqrt(m11 * m11 + m21 * m21)
                    scale_y = math.sqrt(m12 * m12 + m22 * m22)
                    
                    # 回転角度を取得
                    rotation = item.rotation()
                    
                    # 回転とスケールを取り消す変換行列を作成
                    inverse_transform = QTransform()
                    inverse_transform.rotate(-rotation)
                    inverse_transform.scale(1/scale_x, 1/scale_y)
                    
                    # アイテムの現在のバウンディングレクトを取得し、変換を取り消す
                    scene_rect = item.sceneBoundingRect()
                    scene_points = [
                        scene_rect.topLeft(),
                        scene_rect.topRight(),
                        scene_rect.bottomRight(),
                        scene_rect.bottomLeft()
                    ]
                    
                    # 点を回転の中心で逆変換
                    center = scene_rect.center()
                    transformed_points: list[QPointF] = []
                    for point in scene_points:
                        # 中心を原点に移動
                        point -= center
                        # 逆変換（回転とスケール）
                        point = inverse_transform.map(point)
                        # 中心を戻す
                        point += center
                        transformed_points.append(point)
                    
                    # 変換した点から新しい矩形を作成
                    x_coords = [p.x() for p in transformed_points]
                    y_coords = [p.y() for p in transformed_points]
                    rect = QRectF(
                        min(x_coords),
                        min(y_coords),
                        (max(x_coords) - min(x_coords)),
                        (max(y_coords) - min(y_coords))
                    )
                    # アイテムのローカル座標系に変換
                    rect = QRectF(0, 0, rect.width(), rect.height())
                
                
                self.transform_rect_item.setRect(rect)
                # item.rotation()の代わりに変換行列から回転角度を計算
                transform = item.transform()
                rotation_angle = math.degrees(math.atan2(transform.m12(), transform.m11()))
                self.transform_rect_item.setRotation(rotation_angle)


                # アイテムの中心位置を取得
                center = item.sceneBoundingRect().center()
                # transform_rect_itemの中心が元のアイテムの中心と一致するように位置を設定
                # transform_rect_center = self.transform_rect_item.sceneBoundingRect().center()
                # transform_rect_itemの中心位置を計算（回転を考慮）
                transform = QTransform()
                transform.rotate(rotation_angle)
                rect_center = QPointF(rect.center())
                transform_rect_center = self.transform_rect_item.mapToScene(rect_center)
                pos = center - transform_rect_center

                self.transform_rect_item.setPos(pos)
            else:
                rect = selected_items[0].sceneBoundingRect()
                for item in selected_items[1:]:
                    rect = rect.united(item.sceneBoundingRect())

                # 選択されたアイテムの中に回転が適用されているものがあるか確認
                has_rotation = any(
                    abs(math.degrees(math.atan2(item.transform().m12(), item.transform().m11()))) > 0.1
                    for item in selected_items
                )
                
                # 回転が存在する場合、一時的にアスペクト比を固定
                if has_rotation:
                    self.transform_rect_item.setKeepAspectRatio(True)
                elif self.transform_rect_item.keep_aspect_ratio != self.original_keep_aspect_ratio:
                    self.transform_rect_item.setKeepAspectRatio(self.original_keep_aspect_ratio)

                self.transform_rect_item.setRect(rect)
            self.transform_rect_item.updateHandlesPos()
            self.transform_rect_item.setVisible(True)
            self.last_transform_rect = None
            self.last_transform_pos = None
            self.last_transform_angle = None
        else:
            self.transform_rect_item.setVisible(False)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        if self.tool == 'select' and event.button() == Qt.MouseButton.LeftButton:
            # 新しい選択開始時に前の選択パスを消す
            self.selection_path_item.stopAnimation()
            self.selection_start_pos = event.scenePos()
            # 矩形パスを作成
            path = QPainterPath()
            path.addRect(QRectF(self.selection_start_pos, self.selection_start_pos))
            self.selection_path_item.setPath(path)
            self.selection_path_item.startAnimation()
        elif self.tool == 'transform' and event.button() == Qt.MouseButton.LeftButton:
            if self.transform_rect_item.isVisible():
                self.last_transform_rect = self.transform_rect_item.rect()
                self.last_transform_pos = self.transform_rect_item.pos()
                self.last_transform_angle = self.transform_rect_item.rotationAngle
                self.updated_items = []
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self.tool == 'select' and event.buttons() & Qt.MouseButton.LeftButton and self.selection_start_pos:
            rect = QRectF(self.selection_start_pos, event.scenePos()).normalized()
            # 矩形パスを更新
            path = QPainterPath()
            path.addRect(rect)
            self.selection_path_item.setPath(path)
        elif self.tool == 'transform' and event.buttons() & Qt.MouseButton.LeftButton:
            if self.transform_rect_item.isVisible():
                current_rect = self.transform_rect_item.rect()
                current_pos = self.transform_rect_item.pos()
                current_angle = self.transform_rect_item.rotationAngle
                self.updated_items = []
                if self.last_transform_rect is not None and current_rect != self.last_transform_rect:
                    self.updated_items = self.onTransformRectChanged(self.last_transform_rect, current_rect)
                if self.last_transform_pos is not None and current_pos != self.last_transform_pos:
                    self.updated_items = self.onTransformRectPosChanged(self.last_transform_pos, current_pos)
                if self.last_transform_angle is not None and current_angle != self.last_transform_angle:
                    self.updated_items = self.onTransformRectAngleChanged(self.last_transform_angle, current_angle)
                self.last_transform_rect = current_rect
                self.last_transform_pos = current_pos
                self.last_transform_angle = current_angle
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        if self.tool == 'select' and event.button() == Qt.MouseButton.LeftButton:
            if self.selection_start_pos:
                # 選択範囲内のアイテムを選択
                rect = QRectF(self.selection_start_pos, event.scenePos()).normalized()
                items = self.items(rect)
                # 親アイテムのみを選択対象とする
                # self.clearSelection()
                # for item in items:
                #     if item.parentItem() is None and item != self.selection_rect_item and item != self.transform_rect_item:
                #         item.setSelected(True)
                
                # 選択矩形は表示したままにする
                self.selection_start_pos = None
        elif self.tool == 'transform' and event.button() == Qt.MouseButton.LeftButton:
            if self.transform_rect_item.isVisible():
                if self.updated_items:
                    self.itemsTransformedFinished.emit(self.updated_items)
                self.last_transform_rect = None
                self.last_transform_pos = None
                self.last_transform_angle = None
                self.updated_items = []
        super().mouseReleaseEvent(event)

    def onTransformRectChanged(self, old_rect: QRectF, new_rect: QRectF) -> list[QGraphicsItem]:
        selected_items = self.selectedItems()
        if not selected_items:
            return []

        if old_rect.width() == 0 or old_rect.height() == 0:
            return []

        scale_x = new_rect.width() / old_rect.width()
        scale_y = new_rect.height() / old_rect.height()

        # 操作のハンドルの対角にあるハンドルの位置を原点として取得
        origin = self.transform_rect_item.mapToScene(
            self.transform_rect_item.getOppositeHandlePos()
        )

        updated_items: list[QGraphicsItem] = []
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                # QGraphicsRectItemの場合は直接rectを更新
                current_rect = item.rect()
                new_width = current_rect.width() * scale_x
                new_height = current_rect.height() * scale_y
                
                # 新しい矩形を作成（位置は0,0を維持）
                new_item_rect = QRectF(0, 0, new_width, new_height)
                item.setRect(new_item_rect)
                
                # 回転角度を取得
                transform = item.transform()
                rotation_angle = math.degrees(math.atan2(transform.m12(), transform.m11()))
                
                # スケール変更後の位置調整（回転を考慮）
                item_origin = item.mapFromScene(origin)
                
                # 回転を考慮した位置の差分を計算
                rotation_rad = math.radians(rotation_angle)
                cos_theta = math.cos(rotation_rad)
                sin_theta = math.sin(rotation_rad)
                
                dx = item_origin.x() * (scale_x - 1)
                dy = item_origin.y() * (scale_y - 1)
                
                # 回転行列を使用して位置の差分を変換
                rotated_dx = dx * cos_theta - dy * sin_theta
                rotated_dy = dx * sin_theta + dy * cos_theta
                
                item.setPos(item.pos() - QPointF(rotated_dx, rotated_dy))
            else:
                # その他のアイテムは従来通りtransformで変換
                item_origin = item.mapFromScene(origin)
                item_rotation = item.rotation()
                
                rotated_scale_x = scale_x * math.cos(math.radians(item_rotation)) - scale_y * math.sin(math.radians(item_rotation))
                rotated_scale_y = scale_x * math.sin(math.radians(item_rotation)) + scale_y * math.cos(math.radians(item_rotation))
                
                transform = QTransform()
                transform.translate(item_origin.x(), item_origin.y())
                transform.scale(rotated_scale_x, rotated_scale_y)
                transform.translate(-item_origin.x(), -item_origin.y())
                item.setTransform(transform, True)

            updated_items.append(item)
        # 変換が完了した後にシグナルを発信
        self.itemsTransformed.emit(updated_items)

        return updated_items

    def onTransformRectPosChanged(self, old_pos: QPointF, new_pos: QPointF) -> list[QGraphicsItem]:
        selected_items = self.selectedItems()
        if not selected_items:
            return []

        global_translate_x = new_pos.x() - old_pos.x()
        global_translate_y = new_pos.y() - old_pos.y()

        updated_items: list[QGraphicsItem] = []
        for item in selected_items:
            old_item_pos = item.pos()
            new_item_pos = old_item_pos + QPointF(global_translate_x, global_translate_y)
            item.setPos(new_item_pos)
            updated_items.append(item)
        # 移動が完了した後にシグナルを発信
        self.itemsMoved.emit(updated_items)

        return updated_items

    def calculate_transform_origin(self, old_rect: QRectF, new_rect: QRectF):
        # 左方向への拡大/縮小
        if new_rect.left() != old_rect.left() and new_rect.right() == old_rect.right():
            origin_x = old_rect.right()
        # 右方向への拡大/縮小
        elif new_rect.left() == old_rect.left() and new_rect.right() != old_rect.right():
            origin_x = old_rect.left()
        # 両方向への拡大/縮小
        else:
            origin_x = old_rect.center().x()

        # 上方向への拡大/縮小
        if new_rect.top() != old_rect.top() and new_rect.bottom() == old_rect.bottom():
            origin_y = old_rect.bottom()
        # 下方向への拡大/縮小
        elif new_rect.top() == old_rect.top() and new_rect.bottom() != old_rect.bottom():
            origin_y = old_rect.top()
        # 両方向への拡大/縮小
        else:
            origin_y = old_rect.center().y()

        return QPointF(origin_x, origin_y)

    def onTransformRectAngleChanged(self, old_angle: float, new_angle: float) -> list[QGraphicsItem]:
        selected_items = self.selectedItems()
        if not selected_items:
            return []

        angle_diff = new_angle - old_angle
        transform_center = self.transform_rect_item.transformCenterScenePos()

        updated_items: list[QGraphicsItem] = []
        for item in selected_items:
            # アイテムの現在の変換を保持
            current_transform = item.transform()
            
            # イテムのローカル座標系での回転中心点を計算
            item_center = item.mapFromScene(transform_center)
            
            # 回転変換を作成
            rotation_transform = QTransform()
            rotation_transform.translate(item_center.x(), item_center.y())
            rotation_transform.rotate(angle_diff)
            rotation_transform.translate(-item_center.x(), -item_center.y())
            
            # 現在の変換に新しい回転を右から乗算
            new_transform = current_transform * rotation_transform
            
            # 新しい変換を適用
            item.setTransform(new_transform)

            # 回転後のオフセットを計算して位置を調整
            offset = transform_center - item.mapToScene(item_center)
            item.setPos(item.pos() + offset)

            updated_items.append(item)
        # 回転が完了した後にシグナルを発信
        self.itemsRotated.emit(updated_items)

        return updated_items

    def addItem(self, item: QGraphicsItem) -> None:
        if isinstance(item, QGraphicsRectItem) and not isinstance(item, TransformRectItem):
            # 矩形の現在の位置を取得
            rect = item.rect()
            if rect.topLeft() != QPointF(0, 0):
                # topleftが(0,0)以外の場合、posに変換
                current_pos = item.pos()
                new_pos = current_pos + rect.topLeft()
                
                # 矩形を(0,0)を起点に設定
                new_rect = QRectF(0, 0, rect.width(), rect.height())
                item.setRect(new_rect)
                
                # 新しい位置を設定
                item.setPos(new_pos)
        
        super().addItem(item)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if not self.transform_rect_item.isVisible():
            return super().keyPressEvent(event)

        delta = 1
        if event.modifiers() & Qt.KeyboardModifier.ShiftModifier:
            delta = 10

        if event.key() == Qt.Key.Key_Left:
            self.onTransformRectPosChanged(
                self.transform_rect_item.pos(),
                self.transform_rect_item.pos() + QPointF(-delta, 0)
            )
        elif event.key() == Qt.Key.Key_Right:
            self.onTransformRectPosChanged(
                self.transform_rect_item.pos(),
                self.transform_rect_item.pos() + QPointF(delta, 0)
            )
        elif event.key() == Qt.Key.Key_Up:
            self.onTransformRectPosChanged(
                self.transform_rect_item.pos(),
                self.transform_rect_item.pos() + QPointF(0, -delta)
            )
        elif event.key() == Qt.Key.Key_Down:
            self.onTransformRectPosChanged(
                self.transform_rect_item.pos(),
                self.transform_rect_item.pos() + QPointF(0, delta)
            )
        else:
            super().keyPressEvent(event)
        
        self.updateTransformRect()

class CustomRubberBand(QRubberBand):
    def __init__(self, shape, parent=None):
        super().__init__(shape, parent)
        self.pen = QPen(QColor(255, 0, 0), 2)
        self.brush = QColor(255, 0, 0, 64)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setPen(self.pen)
        painter.setBrush(self.brush)
        painter.drawRect(self.rect().adjusted(0, 0, -1, -1))

class TransformView(QGraphicsView):
    def __init__(self, scene: QGraphicsScene):
        super().__init__(scene)
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.RubberBandDrag)

# 使用例
if __name__ == '__main__':
    from PySide6.QtWidgets import QApplication
    import sys

    app = QApplication(sys.argv)
    scene = TransformScene()
    view = TransformView(scene)

    # 3つ��rect_itemを配置
    for i in range(3):
        rect_item = QGraphicsRectItem(0, 0, 100, 100)
        rect_item.setPos(i * 100, i * 100)
        rect_item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
        scene.addItem(rect_item)

    # 親矩形アイテムを作成（水色枠）
    parent_rect = QGraphicsRectItem(0, 0, 200, 150)
    parent_rect.setPos(300, 50)
    parent_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
    parent_rect.setPen(QPen(QColor(0, 180, 255), 2))  # 水色の枠線
    scene.addItem(parent_rect)

    # 子矩形アイテムを作成（赤枠）
    child_rect = QGraphicsRectItem(0, 0, 80, 60)  # 親の座標系での位置とサイズ
    child_rect.setPos(50, 30)
    child_rect.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
    child_rect.setPen(QPen(Qt.GlobalColor.red, 2))  # 赤色の枠線
    child_rect.setParentItem(parent_rect)  # 親子関係を設定

    view.show()
    sys.exit(app.exec())
