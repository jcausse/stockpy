from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor

class EvaluationBar(QWidget):
    """Widget that displays the current position evaluation."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.evaluation = 0.0  # Evaluation in pawns (positive = white advantage)
        self.setFixedHeight(20)  # Fixed height for the bar
        
    def setEvaluation(self, eval_score: float):
        """Set the current evaluation score."""
        self.evaluation = eval_score
        self.update()
        
    def paintEvent(self, event):
        """Draw the evaluation bar."""
        painter = QPainter(self)
        
        # Calculate the midpoint and bar width
        width = self.width()
        height = self.height()
        mid_x = width // 2
        
        # Clamp evaluation between -5 and 5 for display purposes
        clamped_eval = max(min(self.evaluation, 5), -5)
        
        # Calculate bar width based on evaluation
        bar_width = int((abs(clamped_eval) / 5) * (width // 2))
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor("#B58863"))  # Dark square color
        
        # Draw evaluation bar
        if clamped_eval > 0:
            # White advantage - draw from center to right
            painter.fillRect(mid_x, 0, bar_width, height, QColor("#F0D9B5"))  # Light square color
        else:
            # Black advantage - draw from center to left
            painter.fillRect(mid_x - bar_width, 0, bar_width, height, QColor("#F0D9B5"))  # Light square color 