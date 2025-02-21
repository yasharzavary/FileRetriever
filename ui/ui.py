from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel,
    QHBoxLayout, QProgressBar, QMessageBox, QFileDialog, QScrollArea, QFrame,
    QToolBar
)
from PySide6.QtCore import QThread, Signal, QTimer, Qt, QSize

from PySide6.QtGui import QIcon, QAction


# Import the Preprocessor class from the external file
from algorithms.preprocess import Preprocess  # Ensure preprocess_module.py is in the same directory

import os
import sys
import subprocess
from pathlib import Path

# Import searcher
from tools.searcher import Search

preprocess = Preprocess('all')  # our preprocessor
searcher = Search()

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

        self.setWindowTitle("File Reterival")
        self.setGeometry(100, 100, 600, 400)  # Window size

        # Main Layout
        main_layout = QVBoxLayout()

        # Search Bar Layout
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Binary search query...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_action)  # Connect search button
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # Scrollable Search Results Section
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)  # Allows resizing

        # Create a container for search results
        self.results_container = QWidget()
        self.results_layout = QVBoxLayout(self.results_container)
        self.results_layout.setAlignment(Qt.AlignTop)  # Align results to the top
        self.scroll_area.setWidget(self.results_container)


        # menu settings.
        menu = QVBoxLayout()
        reProcess_button = QPushButton()
        reProcess_button.setIcon(QIcon("ui/media/icons/reProcess.ico"))  # Replace with your folder icon file
        reProcess_button.setIconSize(QSize(16, 16))  # Set the size of the folder icon
        reProcess_button.setFixedSize(20, 20)  # Make the button smaller
        reProcess_button.setToolTip("reProcess")  # Tooltip for the button
        reProcess_button.setStyleSheet("border: none;")  # Remove the border around the button
        reProcess_button.clicked.connect(self.ask_preprocessing)

        menu.addWidget(reProcess_button)  # add re process button to the toolbar.

        # Future Updates Bar with Progress Bar
        update_layout = QHBoxLayout()
        self.update_label = QLabel("")
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        update_layout.addWidget(self.update_label)
        update_layout.addWidget(self.progress_bar)

        # Adding widgets to layout
        main_layout.addLayout(menu)
        main_layout.addLayout(search_layout)
        main_layout.addWidget(self.scroll_area)
        main_layout.addLayout(update_layout)

        self.setLayout(main_layout)

        self.update()
        self.repaint()

        # Flag to track preprocessing
        self.preprocess_done = False
        self.readBinaryDict = True
        self.running = False


        # Show preprocessing confirmation AFTER the window appears
        QTimer.singleShot(500, self.ask_preprocessing)  # Delay to show after UI loads

    def onMyToolBarButtonClick(self):
        print('hello')

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

    def open_file_location(self, path):
        """
            open related file location in one sub process

        :param path: path that user choose
        :return:
        """
        subprocess.call(['open', path])

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

    def show_error(self, message):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("warning")
        msg.setText(message)
        msg.setStandardButtons(QMessageBox.Ok)
        msg.exec()  # Show the message box

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
        self.running = True
        self.progress_bar.setValue(0)
        self.update_label.setText("Counting files...")
        self.thread = PreprocessThread(directory, "count")  # First phase: Count files
        self.thread.progress_updated.connect(self.update_progress)
        self.thread.finished.connect(lambda: self.next_phase("read", directory))  # Start next phase when done
        self.thread.start()
        self.preprocess_done = True
        self.running = False
        

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

    def clear_results(self):
        # Clear previous results
        for i in reversed(range(self.results_layout.count())):
            widget = self.results_layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()  # Remove old results

    def display_search_results(self, results: dict):
        self.clear_results()  # Clear previous results

        for file_name, file_path in results.items():  # Assume results contain (file name, file path) pairs
            # Create a horizontal layout for each result
            result_layout = QHBoxLayout()

            # File name label
            file_label = QLabel(file_name)
            file_label.setWordWrap(True)
            file_label.setStyleSheet("font-size: 14px; padding: 2px;")  # Optional styling

            # Folder button with a small icon
            folder_button = QPushButton()
            folder_button.setIcon(QIcon("ui/media/icons/folder_icon.ico"))  # Replace with your folder icon file
            folder_button.setIconSize(QSize(16, 16))  # Set the size of the folder icon
            folder_button.setFixedSize(20, 20)  # Make the button smaller
            folder_button.setToolTip("Open Folder")  # Tooltip for the button
            folder_button.setStyleSheet("border: none;")  # Remove the border around the button
            folder_button.clicked.connect(lambda checked, path=file_path: self.open_file_location(path))

            # Add the file name and folder button to the result layout
            result_layout.addWidget(file_label)
            result_layout.addWidget(folder_button, alignment=Qt.AlignRight)  # Align the folder button to the right

            # Create a QWidget to hold the layout and add it to the results container
            result_widget = QWidget()
            result_widget.setLayout(result_layout)
            self.results_layout.addWidget(result_widget)

    def search_action(self):
        """
            search manager
        :return:
        """
        if not self.preprocess_done:
            self.ask_preprocessing()  # Ask again if preprocessing is not started
            return
        elif not Path('data/binary_dict.json').is_file():
            self.show_error('preprocess doesn\'t done yet...please wait.')
            return
        elif self.readBinaryDict:
            # read binary dict if it doesn't
            try:
                searcher.readBinaryDict()
            except:
                self.show_error('unknown error happend...please redo preprocess.')
            self.readBinaryDict = False

        self.clear_results()  # clear result of the results bar
        query = self.search_input.text() # read query
        results = searcher.search(query)  # Assume searcher returns a list of results

        if not results:
            self.show_error("No results found for this query.")
            return

        self.display_search_results(results)



