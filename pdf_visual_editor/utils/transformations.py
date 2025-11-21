from PyQt6.QtGui import QTransform

class TransformationUtils:
    """
    Helper functions for item transformations.
    """
    @staticmethod
    def apply_scale(item, scale_factor: float):
        transform = item.transform()
        transform.scale(scale_factor, scale_factor)
        item.setTransform(transform)

    @staticmethod
    def apply_rotation(item, angle: float):
        # Rotate around center
        rect = item.boundingRect()
        center = rect.center()
        
        transform = item.transform()
        transform.translate(center.x(), center.y())
        transform.rotate(angle)
        transform.translate(-center.x(), -center.y())
        item.setTransform(transform)
