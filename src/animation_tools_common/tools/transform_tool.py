from PySide6.QtCore import Qt, QRectF, QPointF, Signal
from PySide6.QtWidgets import (QGraphicsItem, QGraphicsRectItem, QGraphicsScene, 
                              QGraphicsSceneMouseEvent)
from PySide6.QtGui import QTransform, QKeyEvent
import math
from ..custom_scene import BaseTool
from ..transform_rect_item import TransformRectItem

class TransformTool(BaseTool):
    """変形機能を提供するツール"""
    
    # シグナルの定義
    itemsTransformed = Signal(list)
    itemsMoved = Signal(list)
    itemsRotated = Signal(list)
    itemsTransformedFinished = Signal(list)
    
    def __init__(self, scene: QGraphicsScene, movable: bool = True, 
                 resizable: bool = True, rotatable: bool = True, 
                 keep_aspect_ratio: bool = False):
        super().__init__(scene)
        # 変形用の矩形アイテムを初期化
        self.transform_rect_item = TransformRectItem(
            QRectF(),
            movable=movable,
            resizable=resizable,
            rotatable=rotatable,
            keep_aspect_ratio=keep_aspect_ratio
        )
        self.transform_rect_item.setVisible(False)
        self.transform_rect_item.setZValue(1000)
        # self.scene.addItem(self.transform_rect_item)
        
        # 状態管理用の変数
        self.last_transform_rect = None
        self.last_transform_pos = None
        self.last_transform_angle = None
        self.original_keep_aspect_ratio = keep_aspect_ratio
        self.updated_items = []
        
        # シーンの選択変更を監視
        self.scene.selectionChanged.connect(self.onSelectionChanged)
    
    def setup(self) -> None:
        self.scene.addItem(self.transform_rect_item)
        self.updateTransformRect()
    
    def cleanup(self) -> None:
        """ツールの状態をクリアする処理"""
        if hasattr(self, 'transform_rect_item'):
            self.transform_rect_item.setVisible(False)
            self.transform_rect_item.setRect(QRectF())
            if self.transform_rect_item.scene() == self.scene:
                self.scene.removeItem(self.transform_rect_item)
        self.last_transform_rect = None
        self.last_transform_pos = None
        self.last_transform_angle = None
        self.updated_items = []
    
    def onSelectionChanged(self):
        """選択変更時の処理"""
        if self.is_active:
            self.updateTransformRect()
    
    def updateTransformRect(self):
        """変形用矩形の更新"""
        selected_items = self.scene.selectedItems()
        
        if not selected_items:
            self.transform_rect_item.setVisible(False)
            return
        
        self.transform_rect_item.setPos(QPointF(0, 0))
        self.transform_rect_item.resetRotation()
        self.transform_rect_item.resetTransformCenter()
        
        if len(selected_items) == 1:
            self._updateSingleItemTransform(selected_items[0])
        else:
            self._updateMultiItemTransform(selected_items)
        
        self.transform_rect_item.updateHandlesPos()
        self.transform_rect_item.setVisible(True)
        self.last_transform_rect = None
        self.last_transform_pos = None
        self.last_transform_angle = None
    
    def _updateSingleItemTransform(self, item: QGraphicsItem):
        """単一アイテムの変形矩形更新"""
        if self.transform_rect_item.keep_aspect_ratio != self.original_keep_aspect_ratio:
            self.transform_rect_item.setKeepAspectRatio(self.original_keep_aspect_ratio)
        
        # 変換行列から情報を取得
        transform = item.transform()
        
        if isinstance(item, QGraphicsRectItem):
            # スケール値を計算
            scale_x = math.sqrt(transform.m11() * transform.m11() + transform.m12() * transform.m12())
            scale_y = math.sqrt(transform.m21() * transform.m21() + transform.m22() * transform.m22())
            # 矩形アイテムの場合の特別処理
            original_rect = item.rect()
            rect = QRectF(0, 0,
                         original_rect.width() * scale_x,
                         original_rect.height() * scale_y)
        else:
            # その他のアイテムの場合
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
        
        # 回転角度を設定
        rotation_angle = math.degrees(math.atan2(transform.m12(), transform.m11()))
        self.transform_rect_item.setRotation(rotation_angle)
        
        # 位置を設定
        center = item.sceneBoundingRect().center()
        transform = QTransform()
        transform.rotate(rotation_angle)
        rect_center = QPointF(rect.center())
        transform_rect_center = self.transform_rect_item.mapToScene(rect_center)
        pos = center - transform_rect_center

        self.transform_rect_item.setPos(pos)
    
    def _updateMultiItemTransform(self, items: list[QGraphicsItem]):
        """複数アイテムの変形矩形更新"""
        # 全アイテムを含む矩形を計算
        rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            rect = rect.united(item.sceneBoundingRect())
        
        # 回転の有無を確認
        has_rotation = any(
            abs(math.degrees(math.atan2(item.transform().m12(), item.transform().m11()))) > 0.1
            for item in items
        )
        
        # 回転がある場合はアスペクト比を固定
        if has_rotation:
            self.transform_rect_item.setKeepAspectRatio(True)
        elif self.transform_rect_item.keep_aspect_ratio != self.original_keep_aspect_ratio:
            self.transform_rect_item.setKeepAspectRatio(self.original_keep_aspect_ratio)
        
        self.transform_rect_item.setRect(rect)
    
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        # if not self.transform_rect_item.isUnderMouse():
        #     return False
        
        if event.button() == Qt.MouseButton.LeftButton and self.transform_rect_item.isVisible():
            self.last_transform_rect = self.transform_rect_item.rect()
            self.last_transform_pos = self.transform_rect_item.pos()
            self.last_transform_angle = self.transform_rect_item.rotationAngle
            self.updated_items = []
            return True
        return False
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        # if not self.transform_rect_item.isUnderMouse():
        #     return False
        
        if event.buttons() & Qt.MouseButton.LeftButton and self.transform_rect_item.isVisible():
            current_rect = self.transform_rect_item.rect()
            current_pos = self.transform_rect_item.pos()
            current_angle = self.transform_rect_item.rotationAngle
            
            self.updated_items = []
            
            if self.last_transform_rect and current_rect != self.last_transform_rect:
                self.updated_items = self._handleTransformRectChanged(
                    self.last_transform_rect, current_rect)
            
            if self.last_transform_pos and current_pos != self.last_transform_pos:
                self.updated_items = self._handleTransformPosChanged(
                    self.last_transform_pos, current_pos)
            
            if self.last_transform_angle and current_angle != self.last_transform_angle:
                self.updated_items = self._handleTransformAngleChanged(
                    self.last_transform_angle, current_angle)
            
            self.last_transform_rect = current_rect
            self.last_transform_pos = current_pos
            self.last_transform_angle = current_angle
            return True
        return False
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> bool:
        # if not self.transform_rect_item.isUnderMouse():
        #     return False
        
        if event.button() == Qt.MouseButton.LeftButton and self.transform_rect_item.isVisible():
            if self.updated_items:
                self.itemsTransformedFinished.emit(self.updated_items)
            self.last_transform_rect = None
            self.last_transform_pos = None
            self.last_transform_angle = None
            self.updated_items = []
            return True
        return False
    
    def _handleTransformRectChanged(self, old_rect: QRectF, new_rect: QRectF) -> list[QGraphicsItem]:
        """矩形サイズ変更時の処理"""
        if old_rect.width() == 0 or old_rect.height() == 0:
            return []
        
        scale_x = new_rect.width() / old_rect.width()
        scale_y = new_rect.height() / old_rect.height()
        origin = self.transform_rect_item.mapToScene(
            self.transform_rect_item.getOppositeHandlePos()
        )
        
        updated_items: list[QGraphicsItem] = []
        for item in self.scene.selectedItems():
            if isinstance(item, QGraphicsRectItem):
                self._transformRectItem(item, scale_x, scale_y, origin)
            else:
                self._transformGenericItem(item, scale_x, scale_y, origin)
            updated_items.append(item)
        
        if len(updated_items) > 0:
            self.itemsTransformed.emit(updated_items)
        return updated_items
    
    def _handleTransformPosChanged(self, old_pos: QPointF, new_pos: QPointF) -> list[QGraphicsItem]:
        """位置変更時の処理"""
        selected_items = self.scene.selectedItems()
        if not selected_items:
            return []

        global_translate_x = new_pos.x() - old_pos.x()
        global_translate_y = new_pos.y() - old_pos.y()

        updated_items: list[QGraphicsItem] = []
        for item in selected_items:
            item.setPos(item.pos() + QPointF(global_translate_x, global_translate_y))
            updated_items.append(item)
        
        if len(updated_items) > 0:
            self.itemsMoved.emit(updated_items)
        return updated_items
    
    def _handleTransformAngleChanged(self, old_angle: float, new_angle: float) -> list[QGraphicsItem]:
        """回転時の処理"""
        angle_diff = new_angle - old_angle
        transform_center = self.transform_rect_item.transformCenterScenePos()
        updated_items: list[QGraphicsItem] = []
        
        for item in self.scene.selectedItems():
            item_center = item.mapFromScene(transform_center)
            rotation_transform = QTransform()
            rotation_transform.translate(item_center.x(), item_center.y())
            rotation_transform.rotate(angle_diff)
            rotation_transform.translate(-item_center.x(), -item_center.y())
            
            item.setTransform(item.transform() * rotation_transform)
            offset = transform_center - item.mapToScene(item_center)
            item.setPos(item.pos() + offset)
            
            updated_items.append(item)
        
        if len(updated_items) > 0:
            self.itemsRotated.emit(updated_items)
        return updated_items
    
    def _transformRectItem(self, item: QGraphicsRectItem, scale_x: float, scale_y: float, origin: QPointF):
        """矩形アイテムの変形処理"""
        current_rect = item.rect()
        new_width = current_rect.width() * scale_x
        new_height = current_rect.height() * scale_y
        new_rect = QRectF(0, 0, new_width, new_height)
        item.setRect(new_rect)
        
        transform = item.transform()
        rotation_angle = math.degrees(math.atan2(transform.m12(), transform.m11()))
        item_origin = item.mapFromScene(origin)
        
        rotation_rad = math.radians(rotation_angle)
        cos_theta = math.cos(rotation_rad)
        sin_theta = math.sin(rotation_rad)
        
        dx = item_origin.x() * (scale_x - 1)
        dy = item_origin.y() * (scale_y - 1)
        
        rotated_dx = dx * cos_theta - dy * sin_theta
        rotated_dy = dx * sin_theta + dy * cos_theta
        
        item.setPos(item.pos() - QPointF(rotated_dx, rotated_dy))
    
    def _transformGenericItem(self, item: QGraphicsItem, scale_x: float, scale_y: float, origin: QPointF):
        """一般アイテムの変形処理"""
        item_origin = item.mapFromScene(origin)
        item_rotation = item.rotation()
        
        rotated_scale_x = scale_x * math.cos(math.radians(item_rotation)) - scale_y * math.sin(math.radians(item_rotation))
        rotated_scale_y = scale_x * math.sin(math.radians(item_rotation)) + scale_y * math.cos(math.radians(item_rotation))
        
        transform = QTransform()
        transform.translate(item_origin.x(), item_origin.y())
        transform.scale(rotated_scale_x, rotated_scale_y)
        transform.translate(-item_origin.x(), -item_origin.y())
        
        item.setTransform(transform, True) 

    def keyPressEvent(self, event: QKeyEvent) -> bool:
        return False

    def keyReleaseEvent(self, event: QKeyEvent) -> bool:
        return False
