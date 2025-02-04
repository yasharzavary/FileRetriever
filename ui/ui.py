from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QLabel,
    QHBoxLayout, QProgressBar, QMessageBox, QFileDialog
)
from PySide6.QtCore import QThread, Signal, QTimer

# Import the Preprocessor class from the external file
from algorithms.preprocess import Preprocess  # Ensure preprocess_module.py is in the same directory


preprocess = Preprocess('all')  # our preprocessor
class PreprocessThread(QThread):
    progress_updated = Signal(int)
    phase_finished = Signal(str)  # Notify when a phase completes

    def __init__(self, directory="all", phase="count"):
        """
            thread class for run prerpocess and control it
        :param directory: location that user want for reterival analyzze
        :param phase: state that we should do in prerpocess
        """
        super().__init__()
        self.location = directory
        self.phase = phase  # Store which phase we are running

    def run(self):
        global preprocess
        preprocess.loc = self.location
        preprocess.pre_process(self.progress_updated.emit, self.phase)  # Run progress
        self.phase_finished.emit(self.phase)  # Notify UI when done


class SearchEngineUI(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Search Engine Prototype")
        self.setGeometry(100, 100, 600, 400)  # Window size

        # Main Layout
        main_layout = QVBoxLayout()

        # Search Bar Layout
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter search query...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_action)  # Connect search button
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # Search Results Section
        self.results_list = QListWidget()

        # Future Updates Bar with Progress Bar
        update_layout = QVBoxLayout()
        self.update_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        update_layout.addWidget(self.update_label)
        update_layout.addWidget(self.progress_bar)

        # Adding widgets to layout
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.results_list)
        main_layout.addLayout(update_layout)

        self.setLayout(main_layout)

        # Flag to track preprocessing
        self.preprocess_done = False

        # Show preprocessing confirmation AFTER the window appears
        QTimer.singleShot(500, self.ask_preprocessing)  # Delay to show after UI loads

    def ask_preprocessing(self):
        """
            program must to preprocess before search.
        :return:
        """
        msg = QMessageBox()
        msg.setWindowTitle("Preprocessing Required")
        msg.setText("The preprocess will start to analyze. Do you want to continue?")
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        response = msg.exec()

        if response == QMessageBox.Yes:
            self.ask_location()  # Ask for location before starting
        else:
            self.preprocess_done = False  # User declined preprocessing

    def ask_location(self):
        """
            if user want a location for analyze, select it
        :return:
        """
        while True:
            msg = QMessageBox()
            msg.setWindowTitle("Select Preprocessing Scope")
            msg.setText("Do you want to analyze all locations of the computer or just a specific location?")
            msg.setInformativeText("Warning: Analyzing all locations can take some times and work slower.")
            msg.setInformativeText("Recommend: select one location for analying and searching.")
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.button(QMessageBox.Yes).setText("All Locations")
            msg.button(QMessageBox.No).setText("Specific Location")
            response = msg.exec()

            if response == QMessageBox.Yes:
                self.start_preprocessing("all")  # Start preprocessing for all locations
            else:
                if self.select_directory():  # Open file explorer for specific location:
                    break


    def select_directory(self):
        directory = QFileDialog.getExistingDirectory(self, "Select Directory for Preprocessing")
        if directory:  # If user selected a directory
            self.start_preprocessing(directory)
        else:
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("Error")
            msg.setText("please select valid directory")
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec()  # Show the message box
            return False
        return True

    def start_preprocessing(self, directory):
        """Start preprocessing and ensure only one thread runs at a time"""
        self.progress_bar.setValue(0)
        self.update_label.setText("Counting files...")
        self.thread = PreprocessThread(directory, "count")  # First phase: Count files
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.finished.connect(lambda: self.next_phase("read", directory))  # Start next phase when done
        self.thread.start()
        self.preprocess_done = True

    def next_phase(self, phase, directory):
        """
            control states of preprocessing
        :param phase: state of preprocessing
        :param directory: location that user want for reterival analyzze
        :return:
        """
        if phase == "read":
            self.update_label.setText("reading files...")
            self.progress_bar.setValue(0)
            self.thread = PreprocessThread(directory, 'read')
            self.thread.progress_updated.connect(self.update_progress)
            self.thread.finished.connect(lambda: self.next_phase("language verify", directory))
            self.thread.start()
        elif phase == "language verify":
            self.update_label.setText("verifying language...")
            self.progress_bar.setValue(0)
            self.thread =PreprocessThread(directory, "lanVerify")
            self.thread.progress_updated.connect(self.update_progress)
            self.thread.finished.connect(lambda: self.next_phase("analyze", directory))
            self.thread.start()
        elif phase == "analyze":
            self.update_label.setText("analyzing...")
            self.progress_bar.setValue(0)
            self.thread = PreprocessThread(directory, "analyze")
            self.thread.progress_updated.connect(self.update_progress)
            self.thread.finished.connect(lambda: self.next_phase("done", directory))
            self.thread.start()
        elif phase == "done":
            self.update_label.setText("Preprocessing Complete ✅ Enjoy Files")


    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def search_action(self):
        """Check if preprocessing is done before allowing search."""
        if not self.preprocess_done:
            self.ask_preprocessing()  # Ask again if preprocessing is not started
        else:
            # Proceed with search logic (implement search function here)
            self.results_list.addItem(f"Search results for: {self.search_input.text()}")


