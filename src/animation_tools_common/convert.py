from PySide6.QtCore import QRect, QRectF
from .obj import Rect, RectF

def qrect_to_rect(qrect: QRect) -> Rect:
    return Rect(
        left=qrect.left(),
        top=qrect.top(),
        width=qrect.width(),
        height=qrect.height()
    )

def qrectf_to_rectf(qrectf: QRectF) -> RectF:
    return RectF(
        left=qrectf.left(),
        top=qrectf.top(),
        width=qrectf.width(),
        height=qrectf.height()
    )