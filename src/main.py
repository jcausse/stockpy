import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget

# Initialize the application
app = QApplication(sys.argv)

# Create a main window
window = QWidget()
window.setWindowTitle('Hello World')

# Create a label and set it as the content of the window
label = QLabel('Hello, PyQt5!', parent=window)
label.move(50, 50)

# Set the window size
window.setGeometry(100, 100, 280, 80)

# Show the window
window.show()

# Run the application's event loop
sys.exit(app.exec())