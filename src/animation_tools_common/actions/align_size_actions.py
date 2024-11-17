from PySide6.QtCore import QRectF
from PySide6.QtWidgets import QGraphicsRectItem
from .base_action import BaseAction

class AlignMinSizeAction(BaseAction):
    """選択アイテムを最小サイズに揃えるアクション"""
    
    action_text = "最小サイズに揃える"
    action_tooltip = "選択されているアイテムを最小サイズに揃えます"
    action_shortcut = "Ctrl+Shift+1"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # 最小サイズを検索（アイテムの種類に応じて適切なrectを使用）
        min_rect = min(selected_items, key=lambda item: (
            item.rect().width() * item.rect().height() 
            if isinstance(item, QGraphicsRectItem) 
            else item.boundingRect().width() * item.boundingRect().height()
        ))
        # 最小サイズのrectを取得
        min_rect = min_rect.rect() if isinstance(min_rect, QGraphicsRectItem) else min_rect.boundingRect()
        
        # すべての選択アイテムのサイズを変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                # 矩形アイテムの場合は直接サイズを変更
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    min_rect.width(),
                    min_rect.height()
                ))
            else:
                # その他のアイテムはスケールを使用
                item.setScale(min_rect.width() / item.boundingRect().width())

class AlignMaxSizeAction(BaseAction):
    """選択アイテムを最大サイズに揃えるアクション"""
    
    action_text = "最大サイズに揃える"
    action_tooltip = "選択されているアイテムを最大サイズに揃えます"
    action_shortcut = "Ctrl+Shift+2"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # 最大サイズを検索（アイテムの種類に応じて適切なrectを使用）
        max_rect = max(selected_items, key=lambda item: (
            item.rect().width() * item.rect().height() 
            if isinstance(item, QGraphicsRectItem) 
            else item.boundingRect().width() * item.boundingRect().height()
        ))
        # 最大サイズのrectを取得
        max_rect = max_rect.rect() if isinstance(max_rect, QGraphicsRectItem) else max_rect.boundingRect()
        
        # すべての選択アイテムのサイズを変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                # 矩形アイテムの場合は直接サイズを変更
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    max_rect.width(),
                    max_rect.height()
                ))
            else:
                # その他のアイテムはスケールを使用
                item.setScale(max_rect.width() / item.boundingRect().width())

class AlignMiddleSizeAction(BaseAction):
    """選択アイテムを中間サイズに揃えるアクション"""
    
    action_text = "中間サイズに揃える"
    action_tooltip = "選択されているアイテムを中間サイズに揃えます"
    action_shortcut = "Ctrl+Shift+3"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # すべてのアイテムの面積を計算（アイテムの種類に応じて適切なrectを使用）
        areas = [(
            item.rect().width() * item.rect().height() 
            if isinstance(item, QGraphicsRectItem) 
            else item.boundingRect().width() * item.boundingRect().height()
        ) for item in selected_items]
        areas.sort()
        
        # 中間のサイズを取得
        middle_index = len(areas) // 2
        middle_area = areas[middle_index]
        
        # 中間サイズのアイテムを見つける
        middle_item = next(item for item in selected_items 
                         if (item.rect().width() * item.rect().height() if isinstance(item, QGraphicsRectItem) 
                             else item.boundingRect().width() * item.boundingRect().height()) == middle_area)
        # 中間サイズのrectを取得
        middle_rect = middle_item.rect() if isinstance(middle_item, QGraphicsRectItem) else middle_item.boundingRect()
        
        # すべての選択アイテムのサイズを変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                # 矩形アイテムの場合は直接サイズを変更
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    middle_rect.width(),
                    middle_rect.height()
                ))
            else:
                # その他のアイテムはスケールを使用
                item.setScale(middle_rect.width() / item.boundingRect().width()) 

class AlignAverageWidthAction(BaseAction):
    """選択アイテムの横幅を揃えるアクション"""
    
    action_text = "横幅を揃える"
    action_tooltip = "選択されているアイテムの横幅を平均値に揃えます"
    action_shortcut = "Ctrl+Shift+4"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # すべてのアイテムの横幅を取得して平均を計算
        widths = [
            item.rect().width() if isinstance(item, QGraphicsRectItem)
            else item.boundingRect().width()
            for item in selected_items
        ]
        average_width = sum(widths) / len(widths)
        
        # すべての選択アイテムの横幅を変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    average_width,
                    current_rect.height()
                ))
            else:
                # 現在の横幅に対する比率でスケールを調整
                current_width = item.boundingRect().width()
                scale_factor = item.scale() * (average_width / current_width)
                item.setScale(scale_factor)

class AlignAverageHeightAction(BaseAction):
    """選択アイテムの高さを揃えるアクション"""
    
    action_text = "高さを揃える"
    action_tooltip = "選択されているアイテムの高さを平均値に揃えます"
    action_shortcut = "Ctrl+Shift+5"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # すべてのアイテムの高さを取得して平均を計算
        heights = [
            item.rect().height() if isinstance(item, QGraphicsRectItem)
            else item.boundingRect().height()
            for item in selected_items
        ]
        average_height = sum(heights) / len(heights)
        
        # すべての選択アイテムの高さを変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    current_rect.width(),
                    average_height
                ))
            else:
                # 現在の高さに対する比率でスケールを調整
                current_height = item.boundingRect().height()
                scale_factor = item.scale() * (average_height / current_height)
                item.setScale(scale_factor)

class AlignMinWidthAction(BaseAction):
    """選択アイテムの横幅を最小値に揃えるアクション"""
    
    action_text = "最小横幅に揃える"
    action_tooltip = "選択されているアイテムの横幅を最小値に揃えます"
    action_shortcut = "Ctrl+Shift+6"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # 最小横幅を取得
        min_width = min(
            item.rect().width() if isinstance(item, QGraphicsRectItem)
            else item.boundingRect().width()
            for item in selected_items
        )
        
        # すべての選択アイテムの横幅を変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    min_width,
                    current_rect.height()
                ))
            else:
                current_width = item.boundingRect().width()
                scale_factor = item.scale() * (min_width / current_width)
                item.setScale(scale_factor)

class AlignMaxWidthAction(BaseAction):
    """選択アイテムの横幅を最大値に揃えるアクション"""
    
    action_text = "最大横幅に揃える"
    action_tooltip = "選択されているアイテムの横幅を最大値に揃えます"
    action_shortcut = "Ctrl+Shift+7"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # 最大横幅を取得
        max_width = max(
            item.rect().width() if isinstance(item, QGraphicsRectItem)
            else item.boundingRect().width()
            for item in selected_items
        )
        
        # すべての選択アイテムの横幅を変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    max_width,
                    current_rect.height()
                ))
            else:
                current_width = item.boundingRect().width()
                scale_factor = item.scale() * (max_width / current_width)
                item.setScale(scale_factor)

class AlignMinHeightAction(BaseAction):
    """選択アイテムの高さを最小値に揃えるアクション"""
    
    action_text = "最小高さに揃える"
    action_tooltip = "選択されているアイテムの高さを最小値に揃えます"
    action_shortcut = "Ctrl+Shift+8"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # 最小高さを取得
        min_height = min(
            item.rect().height() if isinstance(item, QGraphicsRectItem)
            else item.boundingRect().height()
            for item in selected_items
        )
        
        # すべての選択アイテムの高さを変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    current_rect.width(),
                    min_height
                ))
            else:
                current_height = item.boundingRect().height()
                scale_factor = item.scale() * (min_height / current_height)
                item.setScale(scale_factor)

class AlignMaxHeightAction(BaseAction):
    """選択アイテムの高さを最大値に揃えるアクション"""
    
    action_text = "最大高さに揃える"
    action_tooltip = "選択されているアイテムの高さを最大値に揃えます"
    action_shortcut = "Ctrl+Shift+9"
    
    def execute(self) -> None:
        selected_items = self.scene.selectedItems()
        if len(selected_items) < 2:
            return
            
        # 最大高さを取得
        max_height = max(
            item.rect().height() if isinstance(item, QGraphicsRectItem)
            else item.boundingRect().height()
            for item in selected_items
        )
        
        # すべての選択アイテムの高さを変更
        for item in selected_items:
            if isinstance(item, QGraphicsRectItem):
                current_rect = item.rect()
                item.setRect(QRectF(
                    current_rect.x(),
                    current_rect.y(),
                    current_rect.width(),
                    max_height
                ))
            else:
                current_height = item.boundingRect().height()
                scale_factor = item.scale() * (max_height / current_height)
                item.setScale(scale_factor) 