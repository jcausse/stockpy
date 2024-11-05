from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QPainter, QColor, QFont
from PyQt6.QtCore import Qt

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

    def setDisabled(self):
        """Set the evaluation bar to disabled."""
        self.evaluation = None
        self.update()

    def reset(self):
        """Reset the evaluation bar."""
        self.evaluation = 0.0
        self.update()
        
    def paintEvent(self, event):
        """Draw the evaluation bar."""
        painter = QPainter(self)
        
        # Calculate the midpoint and bar width
        width = self.width()
        height = self.height()
        mid_x = width // 2
        
        # Draw background
        painter.fillRect(0, 0, width, height, QColor("#B58863"))  # Dark square color

        if self.evaluation is not None:
            # Clamp evaluation between -5 and 5 for display purposes
            clamped_eval = max(min(self.evaluation, 5), -5)
            
            # Calculate bar width based on evaluation
            bar_width = int((abs(clamped_eval) / 5) * (width // 2))
            
            # Draw evaluation bar
            if clamped_eval > 0:
                # White advantage - draw from center to right
                painter.fillRect(mid_x, 0, bar_width, height, QColor("#F0D9B5"))  # Light square color
            else:
                # Black advantage - draw from center to left
                painter.fillRect(mid_x - bar_width, 0, bar_width, height, QColor("#F0D9B5"))  # Light square color
            
        # Set up text drawing
        painter.setFont(QFont("Arial", 11))
        painter.setPen(QColor("black"))
        
        # Format evaluation text
        if self.evaluation is None:
            eval_text = "Evaluation disabled"
        elif abs(self.evaluation) >= 100:
            eval_text = "M" + str(abs(int(self.evaluation - 100))) if self.evaluation > 0 else "M" + str(abs(int(self.evaluation + 100)))
        else:
            eval_text = f"{self.evaluation:+.1f}"
        
        # Draw text centered in the bar
        text_rect = painter.fontMetrics().boundingRect(eval_text)
        x = (width - text_rect.width()) // 2
        y = (height + text_rect.height()) // 2 - 2  # -2 for slight vertical adjustment
        painter.drawText(x, y, eval_text)
