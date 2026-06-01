import sys
from PyQt6.QtWidgets import QApplication
from widget import AntigravityWidget
from api import RealApiWorker

def main():
    app = QApplication(sys.argv)
    
    # Initialize the main widget
    widget = AntigravityWidget()
    widget.show()
    
    # Initialize the background worker
    api_worker = RealApiWorker()
    
    # Connect the signal from the worker to the widget's update slot
    api_worker.data_updated.connect(widget.update_data)
    
    # Start the background polling
    api_worker.start()
    
    # Start the event loop
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
