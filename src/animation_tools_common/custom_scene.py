from PySide6.QtCore import Qt, QObject, QPointF, QRectF, QRect
from PySide6.QtGui import QPen, QColor, QKeyEvent, QIcon, QAction, QKeySequence, QPainter
from PySide6.QtWidgets import QGraphicsScene, QGraphicsItem, QGraphicsRectItem, QGraphicsSceneMouseEvent, QToolBar, QVBoxLayout
from typing import Type, Dict, Optional, Callable

from .actions.align_actions import AlignLeftAction, AlignCenterAction, AlignRightAction, AlignTopAction, AlignVerticalCenterAction, AlignBottomAction, DistributeHorizontallyAction, DistributeVerticallyAction, DistributeTiledAction
from .actions.delete_action import DeleteAction
from .actions.duplicate_action import DuplicateAction
from .tools.base_tool import BaseTool
from .tools.region_tool import RegionTool
from .transform_rect_item import TransformRectItem
from .actions.base_action import BaseAction
from .actions.align_size_actions import AlignMinSizeAction, AlignMaxSizeAction, AlignMiddleSizeAction, AlignAverageWidthAction, AlignMinWidthAction, AlignMaxWidthAction, AlignAverageHeightAction, AlignMinHeightAction, AlignMaxHeightAction

class CustomScene(QGraphicsScene):
    """拡張可能なカスタムシーン"""
    def __init__(self, parent: QObject | None = None):
        super().__init__(parent)
        self.tools: Dict[str, BaseTool] = {}
        self.active_tool: Optional[BaseTool] = None
        self.tool_actions: Dict[str, QAction] = {}  # 追加：ツールアクションの管理
        self.scene_actions: Dict[str, QAction] = {}  # 追加：シーンアクション用の辞書
        # self._active_item: Optional[QGraphicsItem] = None  # アクティブアイテムを保持
        # self._active_item_pen = QPen(QColor(0, 255, 0), 2, Qt.PenStyle.DashLine)  # アクティブアイテムの枠線スタイル
        self._setup()
    
    def _setup(self):
        """初期設定"""
        # 選択可能なアイテムのデフォルト設定
        self.setItemIndexMethod(QGraphicsScene.ItemIndexMethod.NoIndex)
    
    def registerTool(self, key: str, tool: BaseTool | Type[BaseTool]) -> None:
        """
        新しいツールを登録
        
        Args:
            key: ツールの識別キー
            tool: ツールのインスタンスまたはクラス（BaseToolのサブクラス）
        """
        # 既存のツールがある場合はクリーンアップ
        if key in self.tools:
            self.tools[key].cleanup()
        
        # ツールがクラスの場合はインスタンス化
        if isinstance(tool, type):
            if not issubclass(tool, BaseTool):
                raise TypeError("tool_class must be a subclass of BaseTool")
            tool = tool(self)
        elif not isinstance(tool, BaseTool):
            raise TypeError("tool must be an instance of BaseTool or its subclass")
        
        # ツールを登録
        self.tools[key] = tool

        self.setActiveTool(key)
    
    def setActiveTool(self, key: str) -> None:
        """
        アクティブなツールを設定
        
        Args:
            key: アクティブにするツールのキー
        """
        if key not in self.tools:
            raise KeyError(f"Tool '{key}' not found")
        

        # 現在のツールを非アクティブ化
        if self.active_tool:
            self.active_tool.deactivate()
        
        # ツールバーのチェック状態を更新
        for action_key, action in self.tool_actions.items():
            action.setChecked(action_key == key)
        
        # 新しいツールをアクティブ化
        self.active_tool = self.tools[key]
        self.active_tool.activate()
    
    def getActiveTool(self) -> Optional[BaseTool]:
        """現在アクティブなツールを取得"""
        return self.active_tool
    
    def removeTool(self, key: str) -> None:
        """
        ツールを削除
        
        Args:
            key: 削除するツールのキー
        """
        if key in self.tools:
            if self.active_tool == self.tools[key]:
                self.active_tool = None
            self.tools[key].cleanup()
            del self.tools[key]
    
    # イベントハンドリング
    def mousePressEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """マウスプレスイベントの処理"""
        # # クリックされたアイテムを取得
        # clicked_item = self.itemAt(event.scenePos(), self.views()[0].transform())
        # if clicked_item:
        #     self.setActiveItem(clicked_item)

        if self.active_tool:
            self.active_tool.mousePressEvent(event)
        super().mousePressEvent(event)
    
    def mouseMoveEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """マウス移動イベントの処理"""
        if self.active_tool:
            self.active_tool.mouseMoveEvent(event)
        super().mouseMoveEvent(event)
    
    def mouseReleaseEvent(self, event: QGraphicsSceneMouseEvent) -> None:
        """マウスリリースイベントの処理"""
        if self.active_tool:
            self.active_tool.mouseReleaseEvent(event)
        super().mouseReleaseEvent(event)
    
    def keyPressEvent(self, event: QKeyEvent) -> None:
        """キープレスイベントの処理"""
        if self.active_tool:
            self.active_tool.keyPressEvent(event)
        super().keyPressEvent(event)
    
    def keyReleaseEvent(self, event: QKeyEvent) -> None:
        """ーリリースイベントの処理"""
        if self.active_tool:
            self.active_tool.keyReleaseEvent(event)
        super().keyReleaseEvent(event)

    def importItem(self, item: QGraphicsItem) -> None:
        """アイテムをシーンに追加する際の共通処理"""
        item.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable, True)
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
        self.addItem(item)

    def createToolbar(self) -> QToolBar:
        """
        登録されているツールに基づいてツールバーを作成
        
        Returns:
            QToolBar: ツール切り替え用のツールバー
        """
        toolbar = QToolBar()
        self.tool_actions.clear()  # アクション辞書をクリア
        
        # 登録済みの各ツールに対してアクションを作成
        for key, tool in self.tools.items():
            action = QAction(key.capitalize(), toolbar)
            action.setCheckable(True)
            
            if hasattr(tool, 'icon') and tool.icon:
                action.setIcon(QIcon(tool.icon))
            
            if hasattr(tool, 'tooltip'):
                action.setToolTip(tool.tooltip)
            
            # アクションが選択された時のハンドラを設定
            action.triggered.connect(lambda checked, k=key: self.setActiveTool(k))
            
            # 現在アクティブなツールの場合はチェック状態に
            if tool == self.active_tool:
                action.setChecked(True)
            
            toolbar.addAction(action)
            self.tool_actions[key] = action  # アクションを辞書に保存
        
        toolbar.setProperty('exclusive', True)
        return toolbar

    def registerAction(self, action_class: Type[BaseAction]) -> None:
        """
        アクションを登録
        
        Args:
            action_class: BaseActionのサブクラス
        """
        action = action_class(self)
        key = action_class.__name__.lower()
        
        if key in self.scene_actions:
            self.scene_actions[key].deleteLater()
        
        self.scene_actions[key] = action

    def removeAction(self, key: str) -> None:
        """
        シーンアクションを削除
        
        Args:
            key: 削除するアクションのキー
        """
        if key in self.scene_actions:
            self.scene_actions[key].deleteLater()
            del self.scene_actions[key]

    def createActionToolbar(self) -> QToolBar:
        """
        登録されているアクション用のツールバーを作成
        
        Returns:
            QToolBar: アクション用のツールバー
        """
        toolbar = QToolBar()
        
        for action in self.scene_actions.values():
            toolbar.addAction(action)
        
        return toolbar

    # def setActiveItem(self, item: Optional[QGraphicsItem]) -> None:
    #     """アクティブアイテムを設定"""
    #     if self._active_item == item:
    #         return
            
    #     old_item = self._active_item
    #     self._active_item = item
        
    #     # 必要に応じて古いアイテムと新しいアイテムの見た目を更新
    #     if old_item:
    #         old_item.update()
    #     if item:
    #         item.update()

    # def getActiveItem(self) -> Optional[QGraphicsItem]:
    #     """現在のアクティブアイテムを取得"""
    #     return self._active_item

    # def drawForeground(self, painter: QPainter, rect: QRectF | QRect) -> None:
    #     """シーンの前景を描画"""
    #     super().drawForeground(painter, rect)
        
    #     # アクティブアイテムがある場合、その周りに枠線を描画
    #     if self._active_item:
    #         painter.setPen(self._active_item_pen)
    #         # アイテムのバウンディングボックスを取得（シーン座標系）
    #         bounds = self._active_item.sceneBoundingRect()
    #         # 枠線を描画
    #         painter.drawRect(bounds)


    def setItemFlags(self, flag: QGraphicsItem.GraphicsItemFlag, enabled: bool) -> None:
        """シーン内の全アイテムのフラグを設定"""
        for item in self.items():
            item.setFlag(flag, enabled)


if __name__ == '__main__':
    from PySide6.QtWidgets import (QApplication, QGraphicsView, QMainWindow, 
                                 QListWidget, QHBoxLayout, QWidget)
    from PySide6.QtGui import QPainter
    from common.src.tools.select_tool import SelectTool
    from common.src.tools.transform_tool import TransformTool
    from PySide6.QtWidgets import QGraphicsRectItem

    class MainWindow(QMainWindow):
        def __init__(self):
            super().__init__()
            self.setWindowTitle("カスタムシーンデモ")
            
            # メインウィジェットとレイアウトの設定
            main_widget = QWidget()
            layout = QVBoxLayout(main_widget)
            
            self.scene, self.tools_toolbar, self.action_toolbar = self.setup_scene()
            layout.addWidget(self.tools_toolbar)
            layout.addWidget(self.action_toolbar)
            
            # シーンとビューの設定
            self.view = QGraphicsView(self.scene)
            self.view.setRenderHint(QPainter.RenderHint.Antialiasing)
            # self.view.setDragMode(QGraphicsView.DragMode.RubberBandDrag)
            layout.addWidget(self.view)
            
            # レイアウトの比率設定
            layout.setStretch(0, 1)  # ツールリスト
            layout.setStretch(1, 4)  # ビュー
            
            self.setCentralWidget(main_widget)
            self.add_test_items()
            
            # ウィンドウサイズ設定
            self.resize(1000, 600)
        
        def setup_scene(self):
            """シーンの設定"""
            scene = CustomScene()
            scene.registerTool('select', SelectTool)
            
            transform_tool = TransformTool(
                scene,
                movable=True,
                resizable=True,
                rotatable=True,
                keep_aspect_ratio=False
            )
            scene.registerTool('transform', transform_tool)
            
            # # シグナルの接続
            # transform_tool.itemsTransformed.connect(
            #     lambda items: print(f"Items transformed: {len(items)}")
            # )
            # transform_tool.itemsTransformedFinished.connect(
            #     lambda items: print(f"Transform finished: {len(items)}")
            # )

            scene.registerTool('region', RegionTool)
            
            # デフォルトツールを設定
            scene.setActiveTool('select')


            # アクションの登録
            scene.registerAction(DeleteAction)
            scene.registerAction(DuplicateAction)

            # 整列アクション
            scene.registerAction(AlignLeftAction)
            scene.registerAction(AlignCenterAction)
            scene.registerAction(AlignRightAction)
            scene.registerAction(AlignTopAction)
            scene.registerAction(AlignVerticalCenterAction)
            scene.registerAction(AlignBottomAction)
            scene.registerAction(DistributeHorizontallyAction)
            scene.registerAction(DistributeVerticallyAction)
            scene.registerAction(DistributeTiledAction)
            # サイズアクション
            scene.registerAction(AlignMinSizeAction)
            scene.registerAction(AlignMaxSizeAction)
            scene.registerAction(AlignMiddleSizeAction)
            scene.registerAction(AlignAverageWidthAction)
            scene.registerAction(AlignMinWidthAction)
            scene.registerAction(AlignMaxWidthAction)
            scene.registerAction(AlignAverageHeightAction)
            scene.registerAction(AlignMinHeightAction)
            scene.registerAction(AlignMaxHeightAction)



            tools_toolbar = scene.createToolbar()
            action_toolbar = scene.createActionToolbar()
            return scene, tools_toolbar, action_toolbar 
        
        # def change_tool(self, index: int) -> None:
        #     """ツールの切り替え"""
        #     # 現在選択されているアイテムをクリア
        #     self.scene.clearSelection()
            
        #     # ツールの切り替え
        #     tool_map = {
        #         0: 'select',
        #         1: 'transform',
        #         2: 'region'
        #     }
        #     if index in tool_map:
        #         self.scene.setActiveTool(tool_map[index])
        
        def add_test_items(self):
            """テスト用アイテムの追加"""
            # 10個のテスト用矩形アイテムを追加
            for i in range(10):
                rect_item = QGraphicsRectItem(0, 0, 50 + i*10, 50 + i*10)
                rect_item.setPos(i * 80, i * 60)
                self.scene.importItem(rect_item)

            # 親矩形アイテム（水色枠）
            parent_rect = QGraphicsRectItem(0, 0, 200, 150)
            parent_rect.setPos(300, 50)
            parent_rect.setPen(QPen(QColor(0, 180, 255), 2))
            self.scene.importItem(parent_rect)

            # 子矩形アイテム（赤枠）
            child_rect = QGraphicsRectItem(0, 0, 80, 60)
            child_rect.setPos(50, 30)
            child_rect.setPen(QPen(Qt.GlobalColor.red, 2))
            child_rect.setParentItem(parent_rect)

    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()