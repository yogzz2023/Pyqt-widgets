import sys
import csv
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QLineEdit, QRadioButton, QTextEdit, QGroupBox, QTableWidget,
    QTableWidgetItem, QToolButton, QFileDialog, QSizePolicy, QTabWidget
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import pyqtgraph as pg

class OutputStream:
    def __init__(self, text_edit):
        self.text_edit = text_edit

    def write(self, text):
        self.text_edit.append(text)

    def flush(self):
        pass

class KalmanFilterGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.tracks = []
        self.selected_track_ids = set()
        self.marker_size = 10  # Default marker size
        self.plot_color = 'b'  # Default plot color
        self.input_file = None  # To store the selected input file
        self.initUI()
        self.control_panel_collapsed = False  # Start with the panel expanded

    def initUI(self):
        self.setWindowTitle('Kalman Filter GUI')
        self.setGeometry(100, 100, 1200, 600)
        self.setStyleSheet("""
            QWidget {
                background-color: #2E2E2E;
                color: #FFFFFF;
                font-family: "Arial", sans-serif;
            }
            QPushButton {
                background-color: #5A9;
                color: white;
                border: none;
                padding: 8px 16px;
                text-align: center;
                font-size: 14px;
                margin: 4px 2px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #4A8;
            }
            QLabel {
                color: #FFFFFF;
                font-size: 14px;
            }
            QComboBox {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QComboBox QAbstractItemView {
                background-color: #3A3A3A;
                selection-background-color: #5A9;
                color: white;
            }
            QLineEdit, QTextEdit, QTableWidget {
                background-color: #3A3A3A;
                color: white;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
                font-size: 12px;
            }
            QRadioButton {
                background-color: transparent;
                color: white;
            }
            QGroupBox {
                background-color: #3A3A3A;
                border: 1px solid #555555;
                border-radius: 4px;
                padding: 5px;
            }
            QToolButton {
                background-color: #5A9;
                color: white;
                border: none;
                padding: 8px;
                border-radius: 4px;
            }
            QToolButton:hover {
                background-color: #4A8;
            }
            QTabWidget::pane {
                border: 1px solid #555555;
                background: #3A3A3A;
            }
            QTabBar::tab {
                background: #5A9;
                color: white;
                padding: 10px;
                border-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #4A8;
            }
        """)

        # Main layout
        main_layout = QHBoxLayout()

        # Left side: System Configuration and Controls (Collapsible)
        left_layout = QVBoxLayout()
        main_layout.addLayout(left_layout)

        # Collapse/Expand Button
        self.collapse_button = QToolButton()
        self.collapse_button.setToolButtonStyle(Qt.ToolButtonTextOnly)
        self.collapse_button.setText("=")  # Set the button text to "="
        self.collapse_button.clicked.connect(self.toggle_control_panel)
        left_layout.addWidget(self.collapse_button)

        # Control Panel
        self.control_panel = QWidget()
        self.control_panel.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        control_layout = QVBoxLayout()
        self.control_panel.setLayout(control_layout)
        left_layout.addWidget(self.control_panel)

        # Upload File Button
        self.upload_button = QPushButton("Upload File")
        self.upload_button.clicked.connect(self.select_file)
        control_layout.addWidget(self.upload_button)

        # Process Button
        self.process_button = QPushButton("Process")
        self.process_button.clicked.connect(self.process_data)
        control_layout.addWidget(self.process_button)

        # System Configuration Section
        self.system_config_button = QToolButton()
        self.system_config_button.setText("System Configuration")
        self.system_config_button.setCheckable(True)
        self.system_config_button.setChecked(False)
        self.system_config_button.clicked.connect(self.toggle_system_config)
        control_layout.addWidget(self.system_config_button)

        self.system_config_group = QGroupBox()
        self.system_config_group.setVisible(False)
        system_config_layout = QVBoxLayout()
        self.system_config_group.setLayout(system_config_layout)

        # Track Initiation
        self.track_mode_label = QLabel("Track Initiation")
        self.track_mode_combo = QComboBox()
        self.track_mode_combo.addItems(["3-state", "5-state", "7-state"])
        system_config_layout.addWidget(self.track_mode_label)
        system_config_layout.addWidget(self.track_mode_combo)

        # Association Technique
        self.association_group = QGroupBox("Association Technique")
        association_layout = QVBoxLayout()
        self.jpda_radio = QRadioButton("JPDA")
        self.jpda_radio.setChecked(True)
        association_layout.addWidget(self.jpda_radio)
        self.munkres_radio = QRadioButton("Munkres")
        association_layout.addWidget(self.munkres_radio)
        self.association_group.setLayout(association_layout)
        system_config_layout.addWidget(self.association_group)

        # Filter Modes
        self.filter_group = QGroupBox("Filter Modes")
        filter_layout = QHBoxLayout()
        self.cv_filter_button = QPushButton("CV Filter")
        filter_layout.addWidget(self.cv_filter_button)
        self.ca_filter_button = QPushButton("CA Filter")
        filter_layout.addWidget(self.ca_filter_button)
        self.ct_filter_button = QPushButton("CT Filter")
        filter_layout.addWidget(self.ct_filter_button)
        self.filter_group.setLayout(filter_layout)
        system_config_layout.addWidget(self.filter_group)

        control_layout.addWidget(self.system_config_group)

        # Visualization Section
        self.visualization_button = QToolButton()
        self.visualization_button.setText("Visualization")
        self.visualization_button.setCheckable(True)
        self.visualization_button.setChecked(False)
        self.visualization_button.clicked.connect(self.toggle_visualization)
        control_layout.addWidget(self.visualization_button)

        self.visualization_group = QGroupBox()
        self.visualization_group.setVisible(False)
        visualization_layout = QVBoxLayout()
        self.visualization_group.setLayout(visualization_layout)

        # Visualization Options
        self.range_time_button = QPushButton("Range vs Time")
        visualization_layout.addWidget(self.range_time_button)
        self.azimuth_time_button = QPushButton("Azimuth vs Time")
        visualization_layout.addWidget(self.azimuth_time_button)
        self.elevation_time_button = QPushButton("Elevation vs Time")
        visualization_layout.addWidget(self.elevation_time_button)
        self.ppi_button = QPushButton("PPI")
        visualization_layout.addWidget(self.ppi_button)
        self.rhi_button = QPushButton("RHI")
        visualization_layout.addWidget(self.rhi_button)

        control_layout.addWidget(self.visualization_group)

        # Plot Settings Section
        self.plot_settings_button = QToolButton()
        self.plot_settings_button.setText("Plot Settings")
        self.plot_settings_button.setCheckable(True)
        self.plot_settings_button.setChecked(False)
        self.plot_settings_button.clicked.connect(self.toggle_plot_settings)
        control_layout.addWidget(self.plot_settings_button)

        self.plot_settings_group = QGroupBox()
        self.plot_settings_group.setVisible(False)
        plot_settings_layout = QVBoxLayout()
        self.plot_settings_group.setLayout(plot_settings_layout)

        # Plot Settings Options
        self.range_group = QGroupBox("Range")
        range_layout = QHBoxLayout()
        self.min_range_edit = QLineEdit()
        self.min_range_edit.setPlaceholderText("Min")
        range_layout.addWidget(self.min_range_edit)
        self.max_range_edit = QLineEdit()
        self.max_range_edit.setPlaceholderText("Max")
        range_layout.addWidget(self.max_range_edit)
        self.range_group.setLayout(range_layout)
        plot_settings_layout.addWidget(self.range_group)

        self.azimuth_group = QGroupBox("Azimuth")
        azimuth_layout = QHBoxLayout()
        self.min_azimuth_edit = QLineEdit()
        self.min_azimuth_edit.setPlaceholderText("Min")
        azimuth_layout.addWidget(self.min_azimuth_edit)
        self.max_azimuth_edit = QLineEdit()
        self.max_azimuth_edit.setPlaceholderText("Max")
        azimuth_layout.addWidget(self.max_azimuth_edit)
        self.azimuth_group.setLayout(azimuth_layout)
        plot_settings_layout.addWidget(self.azimuth_group)

        self.elevation_group = QGroupBox("Elevation")
        elevation_layout = QHBoxLayout()
        self.min_elevation_edit = QLineEdit()
        self.min_elevation_edit.setPlaceholderText("Min")
        elevation_layout.addWidget(self.min_elevation_edit)
        self.max_elevation_edit = QLineEdit()
        self.max_elevation_edit.setPlaceholderText("Max")
        elevation_layout.addWidget(self.max_elevation_edit)
        self.elevation_group.setLayout(elevation_layout)
        plot_settings_layout.addWidget(self.elevation_group)

        self.time_group = QGroupBox("Time")
        time_layout = QHBoxLayout()
        self.min_time_edit = QLineEdit()
        self.min_time_edit.setPlaceholderText("Min")
        time_layout.addWidget(self.min_time_edit)
        self.max_time_edit = QLineEdit()
        self.max_time_edit.setPlaceholderText("Max")
        time_layout.addWidget(self.max_time_edit)
        self.time_group.setLayout(time_layout)
        plot_settings_layout.addWidget(self.time_group)

        # Radio Button for Track Selection
        self.track_selection_group = QGroupBox("Track Selection")
        track_selection_layout = QVBoxLayout()
        self.select_all_radio = QRadioButton("Select All Tracks")
        self.select_all_radio.setChecked(True)
        track_selection_layout.addWidget(self.select_all_radio)
        self.track_id_radio = QRadioButton("Track ID")
        track_selection_layout.addWidget(self.track_id_radio)
        self.track_selection_group.setLayout(track_selection_layout)
        plot_settings_layout.addWidget(self.track_selection_group)

        control_layout.addWidget(self.plot_settings_group)

        # Right side: Output and Plot (with Tabs)
        right_layout = QVBoxLayout()
        right_widget = QWidget()
        right_widget.setLayout(right_layout)

        # Tab Widget for Plot and Track Info
        self.tab_widget = QTabWidget()
        self.plot_tab = QWidget()
        self.track_info_tab = QWidget()  # New Track Info Tab
        self.tab_widget.addTab(self.plot_tab, "Plot")
        self.tab_widget.addTab(self.track_info_tab, "Track Info")  # Add Track Info Tab
        right_layout.addWidget(self.tab_widget)

        # Plot Setup
        self.plot_tab.setLayout(QVBoxLayout())

        # Plot Controls
        plot_controls_layout = QHBoxLayout()

        # Plot Configuration button
        self.plot_config_button = QPushButton("Plot Configuration")
        self.plot_config_button.clicked.connect(self.show_config_dialog)
        plot_controls_layout.addWidget(self.plot_config_button)

        # Plot Color dropdown
        self.plot_color_label = QLabel("Plot Color")
        self.plot_color_combo = QComboBox()
        self.plot_color_combo.addItems(["Blue", "Red", "Green", "Yellow", "Black"])
        self.plot_color_combo.currentTextChanged.connect(self.update_plot_color)
        plot_controls_layout.addWidget(self.plot_color_label)
        plot_controls_layout.addWidget(self.plot_color_combo)

        # Marker size selection
        self.marker_size_label = QLabel("Marker Size")
        self.marker_size_combo = QComboBox()
        self.marker_size_combo.addItems(["Small", "Medium", "Large"])
        self.marker_size_combo.currentTextChanged.connect(self.update_marker_size)
        plot_controls_layout.addWidget(self.marker_size_label)
        plot_controls_layout.addWidget(self.marker_size_combo)

        # Clear Plot button
        self.clear_plot_button = QPushButton("Clear Plot")
        self.clear_plot_button.clicked.connect(self.clear_plot)
        plot_controls_layout.addWidget(self.clear_plot_button)

        # Console button
        self.console_button = QPushButton("Console")
        self.console_button.clicked.connect(self.show_console_output)
        plot_controls_layout.addWidget(self.console_button)

        # Add plot controls to the plot tab
        self.plot_tab.layout().addLayout(plot_controls_layout)

        # Plot Widget
        self.plot_widget = pg.GraphicsLayoutWidget()
        self.plot_tab.layout().addWidget(self.plot_widget)

        # Console (Output)
        self.output_display = QTextEdit()
        self.output_display.setFont(QFont('Courier', 10))
        self.output_display.setStyleSheet("background-color: #333333; color: #ffffff;")
        self.output_display.setReadOnly(True)
        self.plot_tab.layout().addWidget(self.output_display)

        # Track Info Setup
        self.track_info_layout = QVBoxLayout()
        self.track_info_tab.setLayout(self.track_info_layout)

        # Buttons to load CSV files
        self.load_detailed_log_button = QPushButton("Load Detailed Log")
        self.load_detailed_log_button.clicked.connect(lambda: self.load_csv('detailed_log.csv'))
        self.track_info_layout.addWidget(self.load_detailed_log_button)

        self.load_track_summary_button = QPushButton("Load Track Summary")
        self.load_track_summary_button.clicked.connect(lambda: self.load_csv('track_summary.csv'))
        self.track_info_layout.addWidget(self.load_track_summary_button)

        # Table to display CSV data
        self.csv_table = QTableWidget()
        self.csv_table.setStyleSheet("background-color: black; color: red;")  # Set text color to white
        self.track_info_layout.addWidget(self.csv_table)

        main_layout.addWidget(right_widget)

        # Redirect stdout to the output display
        sys.stdout = OutputStream(self.output_display)

        # Set main layout
        self.setLayout(main_layout)

        # Initial settings
        self.config_data = {
            "target_speed": (0, 100),
            "target_altitude": (0, 10000),
            "range_gate": (0, 1000),
            "azimuth_gate": (0, 360),
            "elevation_gate": (0, 90),
            "plant_noise": 20  # Default value
        }

        # Add connections to filter buttons
        self.cv_filter_button.clicked.connect(lambda: self.select_filter("CV"))
        self.ca_filter_button.clicked.connect(lambda: self.select_filter("CA"))
        self.ct_filter_button.clicked.connect(lambda: self.select_filter("CT"))

        # Set initial filter mode
        self.filter_mode = "CV"  # Start with CV Filter
        self.update_filter_selection()

    def toggle_control_panel(self):
        self.control_panel_collapsed = not self.control_panel_collapsed
        self.control_panel.setVisible(not self.control_panel_collapsed)
        self.adjustSize()

    def toggle_system_config(self):
        self.system_config_group.setVisible(self.system_config_button.isChecked())

    def toggle_visualization(self):
        self.visualization_group.setVisible(self.visualization_button.isChecked())

    def toggle_plot_settings(self):
        self.plot_settings_group.setVisible(self.plot_settings_button.isChecked())

    def select_file(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Input File", "", "CSV Files (*.csv);;All Files (*)", options=options
        )
        if file_name:
            self.input_file = file_name
            print(f"File selected: {self.input_file}")

    def process_data(self):
        input_file = getattr(self, "input_file", None)
        track_mode = self.track_mode_combo.currentText()
        association_type = "JPDA" if self.jpda_radio.isChecked() else "Munkres"
        filter_option = self.filter_mode

        if not input_file:
            print("Please select an input file.")
            return

        print(
            f"Processing with:\nInput File: {input_file}\nTrack Mode: {track_mode}\nFilter Option: {filter_option}\nAssociation Type: {association_type}"
        )

        self.tracks = main(
            input_file, track_mode, filter_option, association_type
        )  # Process data with selected parameters

        if self.tracks is None:
            print("No tracks were generated.")
        else:
            print(f"Number of tracks: {len(self.tracks)}")

            # Update the plot after processing
            self.update_plot()

    def update_plot(self):
        if not self.tracks:
            print("No tracks to plot.")
            return

        self.plot_widget.clear()  # Clear the plot widget before plotting
        plot = self.plot_widget.addPlot()

        # Example plot: Range vs Time
        for track in self.tracks:
            times = [m[0][3] for m in track['measurements']]
            measurements_x = [(m[0][:3])[0] for m in track['measurements']]

            marker_size = self.marker_size  # Use the selected marker size
            plot_color = self.plot_color  # Use the selected plot color

            plot.plot(times, measurements_x, pen=None, symbol='o', symbolSize=marker_size, symbolBrush=plot_color, name=f'Track {track["track_id"]} Measurement X')

        plot.setLabel('bottom', 'Time')
        plot.setLabel('left', 'X Coordinate')
        plot.setTitle("Range vs Time")
        plot.addLegend()

    def update_marker_size(self, size):
        if size == "Small":
            self.marker_size = 5
        elif size == "Medium":
            self.marker_size = 10
        elif size == "Large":
            self.marker_size = 15
        self.update_plot()  # Update the plot to reflect the new marker size

    def update_plot_color(self, color):
        color_map = {
            "Blue": 'b',
            "Red": 'r',
            "Green": 'g',
            "Yellow": 'y',
            "Black": 'k'
        }
        self.plot_color = color_map.get(color, 'b')
        self.update_plot()  # Update the plot to reflect the new color

    def show_config_dialog(self):
        dialog = PlotConfigDialog(self)
        if dialog.exec_():
            plot_config_data = dialog.get_config_data()
            print(f"Plot Configuration Updated: {plot_config_data}")

    def select_filter(self, filter_type):
        self.filter_mode = filter_type
        self.update_filter_selection()

    def update_filter_selection(self):
        self.cv_filter_button.setChecked(self.filter_mode == "CV")
        self.ca_filter_button.setChecked(self.filter_mode == "CA")
        self.ct_filter_button.setChecked(self.filter_mode == "CT")

    def clear_plot(self):
        self.plot_widget.clear()

    def load_csv(self, file_path):
        try:
            with open(file_path, 'r') as file:
                reader = csv.reader(file)
                headers = next(reader)
                self.csv_table.setColumnCount(len(headers))
                self.csv_table.setHorizontalHeaderLabels(headers)

                # Clear existing rows
                self.csv_table.setRowCount(0)

                # Add rows from CSV
                for row_data in reader:
                    row = self.csv_table.rowCount()
                    self.csv_table.insertRow(row)
                    for column, data in enumerate(row_data):
                        self.csv_table.setItem(row, column, QTableWidgetItem(data))
        except Exception as e:
            print(f"Error loading CSV file: {e}")

    def show_console_output(self):
        # This method can be used to show or hide the console output
        self.output_display.setVisible(not self.output_display.isVisible())

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = KalmanFilterGUI()
    ex.show()
    sys.exit(app.exec_())
