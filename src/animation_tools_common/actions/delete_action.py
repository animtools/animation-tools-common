from .base_action import BaseAction

class DeleteAction(BaseAction):
    """選択アイテムを削除するアクション"""
    
    action_text = "削除"
    action_shortcut = "Delete"
    action_tooltip = "選択したアイテムを削除"
    action_icon = None
    
    def execute(self) -> None:
        """選択されているアイテムを削除"""
        selected_items = self.scene.selectedItems()
        for item in selected_items:
            self.scene.removeItem(item) 