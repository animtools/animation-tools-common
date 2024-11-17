import sys
from typing import Any
from PySide6.QtCore import Qt, QRectF, QPointF, QLineF 
from PySide6.QtGui import QBrush, QPainterPath, QPainter, QColor, QPen, QPixmap, QTransform
from PySide6.QtWidgets import (QGraphicsRectItem, QApplication, QGraphicsView, QGraphicsSceneHoverEvent,
                               QGraphicsSceneMouseEvent, QGraphicsScene, QGraphicsItem, QStyleOptionGraphicsItem, QWidget, QVBoxLayout, QPushButton, QCheckBox)
import math

class TransformRectItem(QGraphicsRectItem):
    handleTopLeft      = 1
    handleTopMiddle    = 2
    handleTopRight     = 3
    handleMiddleLeft   = 4
    handleMiddleRight  = 5
    handleBottomLeft   = 6
    handleBottomMiddle = 7
    handleBottomRight  = 8
    handleTransformCenter     = 9
    handleRotate = 10

    handleSize  = +8.0
    handleSpace = -4.0

    handleCursors: dict[int, Qt.CursorShape] = {
        handleTopLeft:      Qt.CursorShape.SizeFDiagCursor,
        handleTopMiddle:    Qt.CursorShape.SizeVerCursor,
        handleTopRight:     Qt.CursorShape.SizeBDiagCursor,
        handleMiddleLeft:   Qt.CursorShape.SizeHorCursor,
        handleMiddleRight:  Qt.CursorShape.SizeHorCursor,
        handleBottomLeft:   Qt.CursorShape.SizeBDiagCursor,
        handleBottomMiddle: Qt.CursorShape.SizeVerCursor,
        handleBottomRight:  Qt.CursorShape.SizeFDiagCursor,
        handleTransformCenter: Qt.CursorShape.CrossCursor,
        handleRotate: Qt.CursorShape.CrossCursor,
    }

    handleColors: dict[int, QColor] = {
        handleTopLeft:      QColor(255, 0, 0),     # 赤
        handleTopMiddle:    QColor(0, 255, 0),     # 緑
        handleTopRight:     QColor(0, 0, 255),     # 青
        handleMiddleLeft:   QColor(255, 255, 0),   # 黄
        handleMiddleRight:  QColor(0, 255, 255),   # シアン
        handleBottomLeft:   QColor(255, 0, 255),   # マゼンタ
        handleBottomMiddle: QColor(128, 0, 128),   # 紫
        handleBottomRight:  QColor(128, 128, 0),   # オリーブ
        handleTransformCenter:     QColor(255, 165, 0),  # オレンジ色
        handleRotate: QColor(255, 128, 0),  # オレンジ色
    }

    def __init__(self, *args: Any, movable: bool = True, resizable: bool = True, rotatable: bool = True, 
                 keep_aspect_ratio: bool = False, bound_rect: QRectF | None = None):
        super().__init__(*args)
        self.handles: dict[int, QRectF] = {}
        self.handleSelected: int | None = None
        self.mousePressPos: QPointF | None = None
        self.mousePressRect: QRectF | None = None
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, movable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges, True)
        self.transformCenterOffset = QPointF(0, 0)
        self.rotationAngle = 0
        self.tolerance = 2
        self.adjust_size = 3
        self.updateHandlesPos()
        self.debug_mode = False
        self.movable = movable
        self.resizable = resizable
        self.rotatable = rotatable
        self.keep_aspect_ratio = keep_aspect_ratio
        self._last_lod = 1.0  # 最後のLOD値を保存する変数を追加
        self.bound_rect = bound_rect  # 制限範囲を保存
    
    def setMovable(self, movable: bool):
        self.movable = movable
        self.update()
    
    def setResizable(self, resizable: bool):
        self.resizable = resizable
        self.update()
    
    def setRotatable(self, rotatable: bool):
        self.rotatable = rotatable
        self.update()
    
    def setKeepAspectRatio(self, keep_aspect_ratio: bool):
        self.keep_aspect_ratio = keep_aspect_ratio
        self.update()

    def handleAt(self, point: QPointF):
        for k, v in self.handles.items():
            # 移動不可かつスケール不可の場合のみ、リサイズハンドルを無効化
            if not self.movable and not self.resizable and k not in [self.handleRotate, self.handleTransformCenter]:
                continue
                
            # スケール不可の場合はリサイズハンドルを無効化
            if not self.resizable and k in [
                self.handleTopLeft, self.handleTopMiddle, self.handleTopRight,
                self.handleMiddleLeft, self.handleMiddleRight,
                self.handleBottomLeft, self.handleBottomMiddle, self.handleBottomRight
            ]:
                continue
                
            # 回転不可の場合は回転関連ハンドルを無効化
            if not self.rotatable and k in [self.handleRotate, self.handleTransformCenter]:
                continue
                
            # アスペクト比維持モードの場合、中間ハンドルの検出をスキップ
            if self.keep_aspect_ratio and k in [
                self.handleTopMiddle, self.handleMiddleLeft, 
                self.handleMiddleRight, self.handleBottomMiddle
            ]:
                continue
            
            if k == self.handleRotate:
                # 回転ハンドルの場合、円周上の判定を行う
                lod = self.get_lod()
                center = v.center()
                radius = v.width() / 2
                distance = QLineF(center, point).length()
                tolerance = self.tolerance / lod
                if abs(distance - radius) <= tolerance:
                    return k
            else:
                # その他のハンドルの場合、矩形の判定を行う
                enlarged = v.adjusted(-self.adjust_size, -self.adjust_size, self.adjust_size, self.adjust_size)
                if enlarged.contains(point):
                    return k
        return None

    def hoverMoveEvent(self, event: QGraphicsSceneHoverEvent):
        handle = self.handleAt(event.pos())
        if handle is None:
            self.setCursor(Qt.CursorShape.SizeAllCursor)  # 十字矢印のカーソル
        else:
            cursor = self.handleCursors[handle]
            self.setCursor(cursor)
        super().hoverMoveEvent(event)

    def hoverEnterEvent(self, event: QGraphicsSceneHoverEvent):
        super().hoverEnterEvent(event)

    def hoverLeaveEvent(self, event: QGraphicsSceneHoverEvent):
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().hoverLeaveEvent(event)

    def mousePressEvent(self, event: QGraphicsSceneMouseEvent):
        self.handleSelected = self.handleAt(event.pos())
        if self.handleSelected:
            self.mousePressPos  = event.pos()
            self.mousePressRect = self.rect() #self.boundingRect()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent):
        if self.handleSelected == self.handleRotate and self.rotatable:
            self.interactiveRotate(event.pos())
        elif self.handleSelected == self.handleTransformCenter and self.rotatable:
            self.updateTransformCenterPos(event.pos())
        elif self.handleSelected is not None and self.resizable:
            self.interactiveResize(event.pos())
        elif self.movable:
            super().mouseMoveEvent(event)
            # 移動後に制限範囲をチェック
            if self.bound_rect:
                current_rect = self.mapRectToScene(self.rect())
                if not self.bound_rect.contains(current_rect):
                    # 制限範囲を超えた場合、位置を調整
                    new_pos = self.pos()
                    if current_rect.left() < self.bound_rect.left():
                        new_pos.setX(new_pos.x() + self.bound_rect.left() - current_rect.left())
                    if current_rect.right() > self.bound_rect.right():
                        new_pos.setX(new_pos.x() + self.bound_rect.right() - current_rect.right())
                    if current_rect.top() < self.bound_rect.top():
                        new_pos.setY(new_pos.y() + self.bound_rect.top() - current_rect.top())
                    if current_rect.bottom() > self.bound_rect.bottom():
                        new_pos.setY(new_pos.y() + self.bound_rect.bottom() - current_rect.bottom())
                    self.setPos(new_pos)

    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent):
        super().mouseReleaseEvent(event)
        self.handleSelected = None
        self.mousePressPos  = None
        self.mousePressRect = None
        self.update()

    def boundingRect(self):
        o = self.handleSize + self.handleSpace
        r = self.rect()
        br = QRectF(r.left() - o, r.top() - o,
                    r.width() + 2*o, r.height() + 2*o)
        
        # 回転中心ハンドルの位置も考
        center = r.center()
        transformCenterPos = center + self.transformCenterOffset
        br = br.united(QRectF(transformCenterPos.x() - o, transformCenterPos.y() - o, 2*o, 2*o))
        
        # 回転ハンドルの位置も考慮
        diagonal = math.sqrt(r.width()**2 + r.height()**2)
        radius = diagonal / 2 + 20  # updateHandlesPos メソッドと同じ値を使用
        rotateHandleRect = QRectF(transformCenterPos.x() - radius - o,
                                  transformCenterPos.y() - radius - o,
                                  2 * (radius + o),
                                  2 * (radius + o))
        br = br.united(rotateHandleRect)
        
        return br

    def updateHandlesPos(self, keep_transform_center: bool = False):
        # LODを取得
        lod = self.get_lod()
        
        # LODに応じてハンドルサイズを調整
        s = self.handleSize / lod
        r = self.rect()
        
        self.handles[self.handleTopLeft]      = QRectF(r.left() - s / 2, r.top() - s / 2, s, s)
        self.handles[self.handleTopMiddle]    = QRectF(r.center().x() - s / 2, r.top() - s / 2, s, s)
        self.handles[self.handleTopRight]     = QRectF(r.right() - s / 2, r.top() - s / 2, s, s)
        self.handles[self.handleMiddleLeft]   = QRectF(r.left() - s / 2, r.center().y() - s / 2, s, s)
        self.handles[self.handleMiddleRight]  = QRectF(r.right() - s / 2, r.center().y() - s / 2, s, s)
        self.handles[self.handleBottomLeft]   = QRectF(r.left() - s / 2, r.bottom() - s / 2, s, s)
        self.handles[self.handleBottomMiddle] = QRectF(r.center().x() - s / 2, r.bottom() - s / 2, s, s)
        self.handles[self.handleBottomRight]  = QRectF(r.right() - s / 2, r.bottom() - s / 2, s, s)
        
        # 回転中心ハンドルの位置を更新
        if keep_transform_center:
            old_center = self.handles[self.handleTransformCenter].center()
            new_center = r.center()
            self.transformCenterOffset = old_center - new_center
            transformCenterPos = new_center + self.transformCenterOffset
        else:
            center = r.center()
            transformCenterPos = center + self.transformCenterOffset

        self.handles[self.handleTransformCenter] = QRectF(
            transformCenterPos.x() - s / 2,
            transformCenterPos.y() - s / 2,
            s, s
        )
        # 回転ハンドルの位置を更新
        diagonal = math.sqrt(r.width()**2 + r.height()**2)
        radius = diagonal / 2 + 20  # 20はマージン。必要に応じて調整してください。
        self.handles[self.handleRotate] = QRectF(
            transformCenterPos.x() - radius / 2,
            transformCenterPos.y() - radius / 2,
            radius, radius
        )
        self.updateHandleCursors()

    def updateHandleCursors(self):
        r = self.rect()
        self.handleCursors[self.handleTopLeft]      = Qt.CursorShape.SizeFDiagCursor if (r.width() > 0 and r.height() > 0) or (r.width() < 0 and r.height() < 0) else Qt.CursorShape.SizeBDiagCursor
        self.handleCursors[self.handleTopRight]     = Qt.CursorShape.SizeBDiagCursor if (r.width() > 0 and r.height() > 0) or (r.width() < 0 and r.height() < 0) else Qt.CursorShape.SizeFDiagCursor
        self.handleCursors[self.handleBottomLeft]   = Qt.CursorShape.SizeBDiagCursor if (r.width() > 0 and r.height() > 0) or (r.width() < 0 and r.height() < 0) else Qt.CursorShape.SizeFDiagCursor
        self.handleCursors[self.handleBottomRight]  = Qt.CursorShape.SizeFDiagCursor if (r.width() > 0 and r.height() > 0) or (r.width() < 0 and r.height() < 0) else Qt.CursorShape.SizeBDiagCursor

    def interactiveResize(self, mousePos: QPointF):
        if self.mousePressPos is None or self.mousePressRect is None:
            return


        # アスペクト比を維持する場合の処理
        if self.keep_aspect_ratio and self.handleSelected in [self.handleTopLeft, self.handleTopRight, 
                                                             self.handleBottomLeft, self.handleBottomRight]:
            original_rect = self.mousePressRect
            aspect_ratio = original_rect.width() / original_rect.height()
            
            # マウスの移動量を計算
            dx = mousePos.x() - self.mousePressPos.x()
            dy = mousePos.y() - self.mousePressPos.y()
            
            # 移動方向に基づいて符号を決定
            if self.handleSelected in [self.handleTopLeft, self.handleTopRight]:
                sign_y = -1  # 上方向は負
            else:
                sign_y = 1   # 下方向は正
                
            if self.handleSelected in [self.handleTopLeft, self.handleBottomLeft]:
                sign_x = -1  # 左方向は負
            else:
                sign_x = 1   # 右方向は正
            
            # マウスの移動量から新しいサイズを計算
            if sign_x * dx > 0:  # 幅が増加する方向
                new_width = original_rect.width() + abs(dx)
                new_height = new_width / aspect_ratio
            else:  # 幅が減少する方向
                new_width = original_rect.width() - abs(dx)
                new_height = new_width / aspect_ratio
            
            # 新しい位置を計算
            if self.handleSelected == self.handleTopLeft:
                new_rect = QRectF(original_rect.right() - new_width,
                                 original_rect.bottom() - new_height,
                                 new_width, new_height)
            elif self.handleSelected == self.handleTopRight:
                new_rect = QRectF(original_rect.left(),
                                 original_rect.bottom() - new_height,
                                 new_width, new_height)
            elif self.handleSelected == self.handleBottomLeft:
                new_rect = QRectF(original_rect.right() - new_width,
                                 original_rect.top(),
                                 new_width, new_height)
            elif self.handleSelected == self.handleBottomRight:
                new_rect = QRectF(original_rect.left(),
                                 original_rect.top(),
                                 new_width, new_height)

            # 制限範囲のチェック
            if self.bound_rect:
                scene_rect = self.mapRectToScene(new_rect)
                if self.bound_rect.contains(scene_rect):
                    self.setRect(new_rect)
            else:
                self.setRect(new_rect)

        else:
            # リサイズ前の処理を保存
            original_rect = self.rect()
            original_pos = self.pos()
            offset       = self.handleSize + self.handleSpace
            boundingRect = self.boundingRect()
            rect         = self.rect()
            diff         = QPointF(0, 0)

            self.prepareGeometryChange()

            if self.handleSelected == self.handleTopLeft:
                fromX = self.mousePressRect.left()
                fromY = self.mousePressRect.top()
                toX   = fromX + mousePos.x() - self.mousePressPos.x()
                toY   = fromY + mousePos.y() - self.mousePressPos.y()
                diff.setX(toX - fromX)
                diff.setY(toY - fromY)
                boundingRect.setLeft(toX)
                boundingRect.setTop(toY)
                rect.setLeft(boundingRect.left() + offset)
                rect.setTop(boundingRect.top() + offset)
                self.setRect(rect)

            elif self.handleSelected == self.handleTopMiddle:
                fromY = self.mousePressRect.top()
                toY = fromY + mousePos.y() - self.mousePressPos.y()
                diff.setY(toY - fromY)
                boundingRect.setTop(toY)
                rect.setTop(boundingRect.top() + offset)
                self.setRect(rect)

            elif self.handleSelected == self.handleTopRight:
                fromX = self.mousePressRect.right()
                fromY = self.mousePressRect.top()
                toX   = fromX + mousePos.x() - self.mousePressPos.x()
                toY   = fromY + mousePos.y() - self.mousePressPos.y()
                diff.setX(toX - fromX)
                diff.setY(toY - fromY)
                boundingRect.setRight(toX)
                boundingRect.setTop(toY)
                rect.setRight(boundingRect.right() - offset)
                rect.setTop(boundingRect.top() + offset)
                self.setRect(rect)

            elif self.handleSelected == self.handleMiddleLeft:
                fromX = self.mousePressRect.left()
                toX   = fromX + mousePos.x() - self.mousePressPos.x()
                diff.setX(toX - fromX)
                boundingRect.setLeft(toX)
                rect.setLeft(boundingRect.left() + offset)
                self.setRect(rect)

            elif self.handleSelected == self.handleMiddleRight:
                fromX = self.mousePressRect.right()
                toX   = fromX + mousePos.x() - self.mousePressPos.x()
                diff.setX(toX - fromX)
                boundingRect.setRight(toX)
                rect.setRight(boundingRect.right() - offset)
                self.setRect(rect)

            elif self.handleSelected == self.handleBottomLeft:
                fromX = self.mousePressRect.left()
                fromY = self.mousePressRect.bottom()
                toX   = fromX + mousePos.x() - self.mousePressPos.x()
                toY   = fromY + mousePos.y() - self.mousePressPos.y()
                diff.setX(toX - fromX)
                diff.setY(toY - fromY)
                boundingRect.setLeft(toX)
                boundingRect.setBottom(toY)
                rect.setLeft(boundingRect.left() + offset)
                rect.setBottom(boundingRect.bottom() - offset)
                self.setRect(rect)

            elif self.handleSelected == self.handleBottomMiddle:
                fromY = self.mousePressRect.bottom()
                toY   = fromY + mousePos.y() - self.mousePressPos.y()
                diff.setY(toY - fromY)
                boundingRect.setBottom(toY)
                rect.setBottom(boundingRect.bottom() - offset)
                self.setRect(rect)

            elif self.handleSelected == self.handleBottomRight:
                fromX = self.mousePressRect.right()
                fromY = self.mousePressRect.bottom()
                toX   = fromX + mousePos.x() - self.mousePressPos.x()
                toY   = fromY + mousePos.y() - self.mousePressPos.y()
                diff.setX(toX - fromX)
                diff.setY(toY - fromY)
                boundingRect.setRight(toX)
                boundingRect.setBottom(toY)
                rect.setRight(boundingRect.right() - offset)
                rect.setBottom(boundingRect.bottom() - offset)
                self.setRect(rect)

            # 制限範囲のチェック
            if self.bound_rect:
                current_rect = self.mapRectToScene(self.rect())
                if not self.bound_rect.contains(current_rect):
                    # 制限範囲を超えた場合、元の状態に戻す
                    self.setRect(original_rect)
                    self.setPos(original_pos)
                    return

        # transformCenterOffsetがデフォルト値（0, 0）かどうかをチェック
        keep_transform_center = self.transformCenterOffset != QPointF(0, 0)
        self.updateHandlesPos(keep_transform_center=keep_transform_center)

    def shape(self):
        path = QPainterPath()
        path.addRect(self.rect())
        
        # ハンドル用のサブパスを作成
        handles_path = QPainterPath()
        for handle, rect in self.handles.items():
            # 移動不可かつスケール不可の場合のみ、リサイズハンドルを無効化
            if not self.movable and not self.resizable and handle not in [self.handleRotate, self.handleTransformCenter]:
                continue
                
            # スケール不可の場合はリサイズハンドルを無効化
            if not self.resizable and handle in [
                self.handleTopLeft, self.handleTopMiddle, self.handleTopRight,
                self.handleMiddleLeft, self.handleMiddleRight,
                self.handleBottomLeft, self.handleBottomMiddle, self.handleBottomRight
            ]:
                continue
                
            # 回転不可の場合は回転関連ハンドルを無効化
            if not self.rotatable and handle in [self.handleRotate, self.handleTransformCenter]:
                continue
                
            # アスペクト比維持モードの場合、中間ハンドルをスキップ
            if self.keep_aspect_ratio and handle in [
                self.handleTopMiddle, self.handleMiddleLeft, 
                self.handleMiddleRight, self.handleBottomMiddle
            ]:
                continue

            if handle == self.handleRotate:
                handles_path.addEllipse(rect)
            else:
                if isinstance(rect, QRectF):
                    handles_path.addRect(rect)
                elif isinstance(rect, QPointF):
                    handles_path.addEllipse(rect, self.handleSize, self.handleSize)
        
        # メインのパスとハンドルのパスを結合
        path.addPath(handles_path)
        
        # 塗りつぶしルールを Qt.WindingFill に設定
        path.setFillRule(Qt.FillRule.WindingFill)
        
        return path

    def paint(self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: QWidget | None = None):
        # 現在のLODを取得
        current_lod = self.get_lod()
        
        # LODが変化した場合、ハンドルの位置を更新
        if abs(current_lod - self._last_lod) > 0.001:
            self.updateHandlesPos()
            self._last_lod = current_lod

        # デバッグモードの場合は赤い半透明の塗りつぶし、それ以外は透明
        if self.debug_mode:
            painter.setBrush(QBrush(QColor(255, 0, 0, 100)))
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)

        # 矩形の線の色を設定（デバッグモードでない場合は青系の色を使用）
        line_color = QColor(0, 0, 0) if self.debug_mode else QColor(0, 120, 215)
        line_width = self.tolerance / current_lod
        painter.setPen(QPen(line_color, line_width, Qt.PenStyle.SolidLine))
        painter.drawRect(self.rect())

        if self.resizable or self.rotatable:
            painter.setRenderHint(QPainter.RenderHint.Antialiasing)
            for handle, rect in self.handles.items():
                # アスペクト比維持モードの場合、中間ハンドルをスキップ
                if self.keep_aspect_ratio and handle in [self.handleTopMiddle, self.handleMiddleLeft, 
                                                       self.handleMiddleRight, self.handleBottomMiddle]:
                    continue
                
                # 回転不可の場合、回転関連ハンドルをスキップ
                if not self.rotatable and handle in [self.handleRotate, self.handleTransformCenter]:
                    continue

                if self.handleSelected is None or handle == self.handleSelected:
                    if handle == self.handleRotate and self.rotatable:
                        painter.setBrush(Qt.BrushStyle.NoBrush)
                        # デバッグモードでない場合は矩形と同じ色を使用
                        handle_color = self.handleColors[handle] if self.debug_mode else line_color
                        painter.setPen(QPen(handle_color, line_width))
                        painter.drawEllipse(rect)
                    elif handle == self.handleTransformCenter and self.rotatable:
                        # デバッグモードでない場合は矩形と同じ色を使用
                        handle_color = self.handleColors[handle] if self.debug_mode else line_color
                        painter.setBrush(QBrush(handle_color))
                        painter.drawEllipse(rect)
                    elif handle not in [self.handleRotate, self.handleTransformCenter] and self.resizable:
                        # デバッグモードでない場合は矩形と同じ色を使用
                        handle_color = self.handleColors[handle] if self.debug_mode else line_color
                        painter.setBrush(QBrush(handle_color))
                        painter.drawEllipse(rect)

        # デバッグモードが有効の場合のみshapeを表示
        if self.debug_mode:
            painter.setPen(QPen(QColor(0, 255, 0, 100), 1, Qt.PenStyle.DashLine))
            painter.drawPath(self.shape())

    def updateTransformCenterPos(self, mousePos: QPointF):
        # 矩形の中心からの差を計算
        center = self.rect().center()
        self.transformCenterOffset = mousePos - center
        self.updateHandlesPos()
        self.update()  # 再描画を要求

    def interactiveRotate(self, mousePos: QPointF):
        if self.mousePressPos is None or self.mousePressRect is None:
            return

        center = self.rect().center() + self.transformCenterOffset
        startVector = self.mousePressPos - center
        currentVector = mousePos - center
        angle = math.degrees(math.atan2(currentVector.y(), currentVector.x()) - 
                             math.atan2(startVector.y(), startVector.x()))
        
        # 現在の回転をリセット
        # self.setRotation(0)

        # 回転中心を基準に矩形を回転
        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.rotate(angle)
        transform.translate(-center.x(), -center.y())
        
        self.setTransform(transform, True)
        
        # 回転角度を更新
        self.rotationAngle = (self.rotationAngle + angle) % 360
        
        self.updateHandlesPos()
        self.update()
    
    def setRotation(self, angle: float):
        self.rotationAngle = angle

        center = self.rect().center() + self.transformCenterOffset
        # 回転中心を基準に矩形を回転
        transform = QTransform()
        transform.translate(center.x(), center.y())
        transform.rotate(angle)
        transform.translate(-center.x(), -center.y())
        
        self.setTransform(transform, True)
    
    def resetRotation(self):
        self.setTransform(QTransform())
        
        # 回転角度をリセット
        self.rotationAngle = 0

    def resetTransformCenter(self):
        self.transformCenterOffset = QPointF(0, 0)
        self.updateHandlesPos()
        self.update()
        
        # シーンが存在する場合、シーン全体を更新
        if self.scene():
            self.scene().update()

    def set_debug_mode(self, enabled: bool):
        self.debug_mode = enabled
        self.update()  # 再描画を要求

    def transformCenterScenePos(self) -> QPointF:
        local_center = self.rect().center() + self.transformCenterOffset
        return self.mapToScene(local_center)

    def getOppositeHandlePos(self) -> QPointF:
        if self.handleSelected is None:
            # デォルトでは中心返す
            return self.rect().center()

        # 対角のハンドルのマッピング
        opposite_handles = {
            self.handleTopLeft: self.handleBottomRight,
            self.handleTopMiddle: self.handleBottomMiddle,
            self.handleTopRight: self.handleBottomLeft,
            self.handleMiddleLeft: self.handleMiddleRight,
            self.handleMiddleRight: self.handleMiddleLeft,
            self.handleBottomLeft: self.handleTopRight,
            self.handleBottomMiddle: self.handleTopMiddle,
            self.handleBottomRight: self.handleTopLeft,
        }

        # 選択されているハンドルに対応する対角のハンドルを取得
        opposite_handle = opposite_handles.get(self.handleSelected)
        if opposite_handle is None:
            # 回ハンドルや変形中心ハンドルの場合は矩形の中心を返す
            return self.rect().center()

        # 対角のハンドルの位置を返す
        return self.handles[opposite_handle].center()

    def get_lod(self) -> float:
        """現在のLOD（Level of Detail）を取得"""
        if self.scene() and self.scene().views():
            return self.scene().views()[0].transform().m11()
        return 1.0

    def setBoundRect(self, rect: QRectF | None):
        """制限範囲を設定するメソッド"""
        self.bound_rect = rect
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)

    grview = QGraphicsView()
    scene = QGraphicsScene()
    scene.setSceneRect(0, 0, 680, 459)
    scene.addPixmap(QPixmap('D:/_Qt/img/qt-logo.png'))
    
    # 制限範囲を表す矩形を追加
    bound_rect = QGraphicsRectItem(50, 50, 580, 359)  # シーンの端から少し内側に設定
    bound_rect.setPen(QPen(QColor(255, 0, 0), 2, Qt.PenStyle.DashLine))  # 赤色の点線
    scene.addItem(bound_rect)
    
    grview.setScene(scene)

    item = TransformRectItem(0, 0, 300, 150, movable=True, resizable=True, rotatable=True, keep_aspect_ratio=True)
    item.setBoundRect(bound_rect.rect())
    scene.addItem(item)

    # メインウィンドウとレイアウトの作成
    main_window = QWidget()
    layout = QVBoxLayout(main_window)

    # グラフィックスビューをレイアウトに追加
    layout.addWidget(grview)

    # リセットボタンの作成と追加
    reset_button = QPushButton("回転をリセット")
    reset_button.clicked.connect(item.resetRotation)
    layout.addWidget(reset_button)

    reset_center_button = QPushButton("回転中心をリセット")
    reset_center_button.clicked.connect(item.resetTransformCenter)
    layout.addWidget(reset_center_button)

    # チェックボックスに変更
    debug_mode_check = QCheckBox("デバッグモード")
    debug_mode_check.setChecked(item.debug_mode)
    debug_mode_check.toggled.connect(item.set_debug_mode)
    layout.addWidget(debug_mode_check)

    movable_check = QCheckBox("移動可能")
    movable_check.setChecked(item.movable)
    movable_check.toggled.connect(item.setMovable)
    layout.addWidget(movable_check)

    resizable_check = QCheckBox("リサイズ可能")
    resizable_check.setChecked(item.resizable)
    resizable_check.toggled.connect(item.setResizable)
    layout.addWidget(resizable_check)

    rotatable_check = QCheckBox("回転可能")
    rotatable_check.setChecked(item.rotatable)
    rotatable_check.toggled.connect(item.setRotatable)
    layout.addWidget(rotatable_check)

    keep_aspect_ratio_check = QCheckBox("アスペクト比維持")
    keep_aspect_ratio_check.setChecked(item.keep_aspect_ratio)
    keep_aspect_ratio_check.toggled.connect(item.setKeepAspectRatio)
    layout.addWidget(keep_aspect_ratio_check)

    grview.fitInView(scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
    
    main_window.show()
    sys.exit(app.exec())
