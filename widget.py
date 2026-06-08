import sys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QApplication, QFrame
from PyQt6.QtCore import Qt, QPoint, QRectF
from PyQt6.QtGui import QPainter, QColor, QPainterPath

class ModelLimitWidget(QWidget):
    def __init__(self, model_name, parent=None):
        super().__init__(parent)
        self.model_name = model_name
        
        layout = QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)
        
        # Header layout (Name and Usage Text)
        header_layout = QHBoxLayout()
        self.name_label = QLabel(model_name)
        self.name_label.setStyleSheet("color: #FFFFFF; font-weight: 600; font-size: 13px; font-family: 'Segoe UI', Arial;")
        
        self.status_label = QLabel("Loading...")
        self.status_label.setStyleSheet("color: #B0B0C0; font-size: 11px; font-family: 'Segoe UI', Arial;")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        header_layout.addWidget(self.name_label)
        header_layout.addWidget(self.status_label)
        
        # Indicator bar using QProgressBar
        from PyQt6.QtWidgets import QProgressBar
        self.progress = QProgressBar()
        self.progress.setFixedHeight(6)
        self.progress.setTextVisible(False)
        self.progress.setRange(0, 100)
        self.progress.setValue(100)
        self.progress.setStyleSheet("""
            QProgressBar {
                background-color: #2A2A35;
                border: none;
                border-radius: 3px;
            }
            QProgressBar::chunk {
                background-color: #8A2BE2;
                border-radius: 3px;
            }
        """)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.progress)
        
        self.setLayout(layout)
        
    def update_status(self, status, percentage=100, reset_time=""):
        if reset_time:
            self.status_label.setText(f"{status} | {reset_time}")
        else:
            self.status_label.setText(status)
        self.progress.setValue(percentage)
        
        # Color the bar based on the raw_status embedded in the status string or from logic
        if "Fast" in status:
            color = "#00FA9A"
        elif "Limited time" in status:
            color = "#FFA500"
        elif "Slow" in status:
            color = "#FFD700"
        elif "Rate" in status or "Quota" in status or percentage <= 0:
            color = "#FF4500"
        else:
            color = "#8A2BE2"
            
        self.progress.setStyleSheet(f"""
            QProgressBar {{
                background-color: #2A2A35;
                border: none;
                border-radius: 3px;
            }}
            QProgressBar::chunk {{
                background-color: {color};
                border-radius: 3px;
            }}
        """)

class AntigravityWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.model_widgets = {}

        # Variables for dragging the window
        self.drag_position = QPoint()

    def init_ui(self):
        # Make the window frameless and translucent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.setFixedWidth(320)
        
        # Main layout
        self.main_layout = QVBoxLayout()
        # This makes the window auto-shrink to fit contents perfectly
        self.main_layout.setSizeConstraint(QVBoxLayout.SizeConstraint.SetFixedSize)
        self.main_layout.setContentsMargins(18, 18, 18, 18)
        self.main_layout.setSpacing(12)
        
        # Title Label
        title = QLabel("Antigravity IDE Limits")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("color: #FFFFFF; font-size: 14px; font-weight: bold; font-family: 'Segoe UI', Arial; margin-bottom: 4px;")
        self.main_layout.addWidget(title)
        
        # Container for the models
        self.models_layout = QVBoxLayout()
        self.models_layout.setSpacing(8)
        self.main_layout.addLayout(self.models_layout)
        
        # Close Button instructions
        close_label = QLabel("Right-click for options • Double-click to close")
        close_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        close_label.setStyleSheet("color: #606060; font-size: 10px; font-family: 'Segoe UI', Arial; margin-top: 8px;")
        self.main_layout.addWidget(close_label)
        self.setLayout(self.main_layout)

    def showEvent(self, event):
        super().showEvent(event)
        from PyQt6.QtCore import QTimer
        # Wait a tiny bit for the window to be fully rendered and scaled
        QTimer.singleShot(100, self.position_top_right)

    def position_top_right(self):
        from PyQt6.QtWidgets import QApplication
        screens = QApplication.screens()
        
        # Find the rightmost screen reliably
        rightmost_screen = max(screens, key=lambda s: s.geometry().right())
                
        # Get the screen's available geometry (excluding taskbar)
        screen_geo = rightmost_screen.availableGeometry()
        
        # Calculate position using actual self.width() after render, with 20px padding
        # Use x() and width() for safer calculation
        x = screen_geo.x() + screen_geo.width() - self.width() - 20
        y = screen_geo.y() + 20
        
        self.move(x, y)

    def paintEvent(self, event):
        # Draw the custom rounded background
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), 16.0, 16.0)
        
        # Semi-transparent dark background (glassy effect)
        bg_color = QColor(22, 22, 32, 245)
        painter.fillPath(path, bg_color)
        
        # Subtle border
        painter.setPen(QColor(80, 80, 100, 150))
        painter.drawPath(path)

    def update_data(self, limits_data):
        if not limits_data:
            return
            
        current_models = list(self.model_widgets.keys())
        new_models = list(limits_data.keys())
        
        if current_models != new_models:
            # Clear existing widgets to respect the incoming order
            while self.models_layout.count():
                item = self.models_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                    
            self.model_widgets.clear()
                
            # Recreate widgets in the exact order they are received from the API
            for model_name, data in limits_data.items():
                widget = ModelLimitWidget(model_name)
                self.model_widgets[model_name] = widget
                self.models_layout.addWidget(widget)
                
                # Update status
                widget.update_status(data["status"], data.get("percentage", 100), data.get("reset_time", ""))
        else:
            # Update existing widgets without clearing the layout to prevent flickering
            for model_name, data in limits_data.items():
                widget = self.model_widgets[model_name]
                widget.update_status(data["status"], data.get("percentage", 100), data.get("reset_time", ""))

    # --- Mouse events for dragging the frameless window ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
            
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            QApplication.quit()

    def contextMenuEvent(self, event):
        from PyQt6.QtWidgets import QMenu
        from PyQt6.QtGui import QAction
        
        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background-color: #2b2b36;
                color: #ffffff;
                border: 1px solid #4a4a5a;
                border-radius: 5px;
            }
            QMenu::item {
                padding: 5px 20px 5px 20px;
            }
            QMenu::item:selected {
                background-color: #4169E1;
            }
        """)
        
        always_on_top_action = QAction("Always on Top", self)
        always_on_top_action.setCheckable(True)
        # Check current state
        is_on_top = bool(self.windowFlags() & Qt.WindowType.WindowStaysOnTopHint)
        always_on_top_action.setChecked(is_on_top)
        
        close_action = QAction("Close", self)
        
        menu.addAction(always_on_top_action)
        menu.addSeparator()
        menu.addAction(close_action)
        
        action = menu.exec(self.mapToGlobal(event.pos()))
        
        if action == always_on_top_action:
            if always_on_top_action.isChecked():
                # Enable Always on Top
                self.setWindowFlags(self.windowFlags() | Qt.WindowType.WindowStaysOnTopHint)
            else:
                # Disable Always on Top, send to background
                self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowStaysOnTopHint)
            
            # Changing Window Flags hides the window, we need to show it again
            self.show()
        elif action == close_action:
            QApplication.quit()
