from PySide6.QtCore import Qt
from .base_action import BaseAction

class DuplicateAction(BaseAction):
    """選択アイテムを複製するアクション"""
    
    action_text = "複製"
    action_shortcut = "Ctrl+D"
    action_tooltip = "選択したアイテムを複製"
    action_icon = None
    
    def execute(self) -> None:
        """選択されているアイテムを複製"""
        selected_items = self.scene.selectedItems()
        offset = 20  # 複製時のオフセット
        
        for item in selected_items:
            # アイテムの複製（具体的な実装はアイテムの種類によって異なる）
            new_item = type(item)()
            new_item.setPos(item.pos().x() + offset, item.pos().y() + offset)
            # その他のプロパティのコピー
            # ...
            self.scene.importItem(new_item) 