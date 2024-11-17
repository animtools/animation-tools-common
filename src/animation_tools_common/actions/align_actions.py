from typing import List
from PySide6.QtWidgets import QGraphicsItem
from .base_action import BaseAction

class BaseAlignAction(BaseAction):
    """揃えるアクションの基底クラス"""
    pass
    def _get_selected_items(self) -> List[QGraphicsItem]:
        """シーンから選択されているアイテムを取得"""
        return self.scene.selectedItems()

class AlignLeftAction(BaseAlignAction):
    """選択アイテムを左端に揃えるアクション"""
    
    action_text = "左揃え"
    action_tooltip = "選択したアイテムを左端に揃えます"
    action_shortcut = "Ctrl+Shift+L"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if not items:
            return
            
        # 基準となる最も左のX座標を取得
        left_most = min(item.sceneBoundingRect().left() for item in items)
        
        # 全てのアイテムを左端に揃える
        for item in items:
            current_left = item.sceneBoundingRect().left()
            item.moveBy(left_most - current_left, 0)

class AlignCenterAction(BaseAlignAction):
    """選択アイテムを水平中央に揃えるアクション"""
    
    action_text = "中央揃え"
    action_tooltip = "選択したアイテムを水平方向の中央に揃えます"
    action_shortcut = "Ctrl+Shift+C"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if not items:
            return
            
        # 基準となる中心のX座標を計算（最初のアイテムの中心を使用）
        united_bounding_rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            united_bounding_rect = united_bounding_rect.united(item.sceneBoundingRect())
        reference_center = united_bounding_rect.center().x()
        
        # 全てのアイテムを中央に揃える
        for item in items:
            current_center = item.sceneBoundingRect().center().x()
            item.moveBy(reference_center - current_center, 0)

class AlignRightAction(BaseAlignAction):
    """選択アイテムを右端に揃えるアクション"""
    
    action_text = "右揃え"
    action_tooltip = "選択したアイテムを右端に揃えます"
    action_shortcut = "Ctrl+Shift+R"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if not items:
            return
            
        # 基準となる最も右のX座標を取得
        right_most = max(item.sceneBoundingRect().right() for item in items)
        
        # 全てのアイテムを右端に揃える
        for item in items:
            current_right = item.sceneBoundingRect().right()
            item.moveBy(right_most - current_right, 0)


class AlignTopAction(BaseAlignAction):
    """選択アイテムを上端に揃えるアクション"""
    
    action_text = "上揃え"
    action_tooltip = "選択したアイテムを上端に揃えます"
    action_shortcut = "Ctrl+Shift+T"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if not items:
            return
            
        # 基準となる最も上のY座標を取得
        top_most = min(item.sceneBoundingRect().top() for item in items)
        
        # 全てのアイテムを上端に揃える
        for item in items:
            current_top = item.sceneBoundingRect().top()
            item.moveBy(0, top_most - current_top)

class AlignVerticalCenterAction(BaseAlignAction):
    """選択アイテムを垂直中央に揃えるアクション"""
    
    action_text = "垂直中央揃え"
    action_tooltip = "選択したアイテムを垂直方向の中央に揃えます"
    action_shortcut = "Ctrl+Shift+V"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if not items:
            return
            
        # 基準となる中心のY座標を計算（最初のアイテムの中心を使用）
        united_bounding_rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            united_bounding_rect = united_bounding_rect.united(item.sceneBoundingRect())
        reference_center = united_bounding_rect.center().y()
        
        # 全てのアイテムを垂直中央に揃える
        for item in items:
            current_center = item.sceneBoundingRect().center().y()
            item.moveBy(0, reference_center - current_center)

class AlignBottomAction(BaseAlignAction):
    """選択アイテムを下端に揃えるアクション"""
    
    action_text = "下揃え"
    action_tooltip = "選択したアイテムを下端に揃えます"
    action_shortcut = "Ctrl+Shift+B"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if not items:
            return
            
        # 基準となる最も下のY座標を取得
        bottom_most = max(item.sceneBoundingRect().bottom() for item in items)
        
        # 全てのアイテムを下端に揃える
        for item in items:
            current_bottom = item.sceneBoundingRect().bottom()
            item.moveBy(0, bottom_most - current_bottom)

class DistributeHorizontallyAction(BaseAlignAction):
    """選択アイテムを水平方向に等間隔で並べるアクション"""
    
    action_text = "水平に整列"
    action_tooltip = "選択したアイテムを水平方向に等間隔で並べます"
    action_shortcut = "Ctrl+Shift+H"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if len(items) < 2:
            return
            
        # 全体の矩形を計算
        united_rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            united_rect = united_rect.united(item.sceneBoundingRect())
            
        # アイテムの合計幅とスペースを計算
        total_width = sum(item.sceneBoundingRect().width() for item in items)
        spacing = 10  # アイテム間のスペース
        total_spacing = spacing * (len(items) - 1)
        
        # 開始位置を計算（中央揃え）
        start_x = united_rect.center().x() - (total_width + total_spacing) / 2
        center_y = united_rect.center().y()
        
        # アイテムを配置
        current_x = start_x
        for item in items:
            rect = item.sceneBoundingRect()
            item.moveBy(
                current_x - rect.left(),
                center_y - rect.center().y()
            )
            current_x += rect.width() + spacing

class DistributeVerticallyAction(BaseAlignAction):
    """選択アイテムを垂直方向に等間隔で並べるアクション"""
    
    action_text = "垂直に整列"
    action_tooltip = "選択したアイテムを垂直方向に等間隔で並べます"
    action_shortcut = "Ctrl+Shift+Y"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if len(items) < 2:
            return
            
        # 全体の矩形を計算
        united_rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            united_rect = united_rect.united(item.sceneBoundingRect())
            
        # アイテムの合計高さとスペースを計算
        total_height = sum(item.sceneBoundingRect().height() for item in items)
        spacing = 10  # アイテム間のスペース
        total_spacing = spacing * (len(items) - 1)
        
        # 開始位置を計算（中央揃え）
        center_x = united_rect.center().x()
        start_y = united_rect.center().y() - (total_height + total_spacing) / 2
        
        # アイテムを配置
        current_y = start_y
        for item in items:
            rect = item.sceneBoundingRect()
            item.moveBy(
                center_x - rect.center().x(),
                current_y - rect.top()
            )
            current_y += rect.height() + spacing

class DistributeTiledAction(BaseAlignAction):
    """選択アイテムをタイル状に並べるアクション"""
    
    action_text = "タイル状に整列"
    action_tooltip = "選択したアイテムをタイル状に並べます"
    action_shortcut = "Ctrl+Shift+G"
    
    def execute(self) -> None:
        items = self._get_selected_items()
        if len(items) < 2:
            return
            
        # 全体の矩形を計算
        united_rect = items[0].sceneBoundingRect()
        for item in items[1:]:
            united_rect = united_rect.united(item.sceneBoundingRect())
            
        # グリッドの列数を計算
        num_items = len(items)
        num_cols = int(num_items ** 0.5)  # ルートを取って四捨五入
        num_rows = (num_items + num_cols - 1) // num_cols
        
        spacing = 10  # アイテム間のスペース
        
        # アイテムの最大サイズを計算
        max_width = max(item.sceneBoundingRect().width() for item in items)
        max_height = max(item.sceneBoundingRect().height() for item in items)
        
        # グリッド全体のサイズを計算
        total_width = max_width * num_cols + spacing * (num_cols - 1)
        total_height = max_height * num_rows + spacing * (num_rows - 1)
        
        # 開始位置を計算（中央揃え）
        start_x = united_rect.center().x() - total_width / 2
        start_y = united_rect.center().y() - total_height / 2
        
        # アイテムを配置
        for i, item in enumerate(items):
            row = i // num_cols
            col = i % num_cols
            
            rect = item.sceneBoundingRect()
            target_x = start_x + col * (max_width + spacing)
            target_y = start_y + row * (max_height + spacing)
            
            item.moveBy(
                target_x - rect.left() + (max_width - rect.width()) / 2,
                target_y - rect.top() + (max_height - rect.height()) / 2
            )