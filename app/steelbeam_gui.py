import sys
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QMessageBox,
    QGroupBox,
    QHBoxLayout,
    QRadioButton,
    QButtonGroup,
)

from PySide6.QtWebEngineWidgets import QWebEngineView

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from steelbeam import SteelBeam, profile_type, get_profiles_by_type

import utils

class SteelBeamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        
        ##----CONSTRUCTION OF THE GUI----

        self.setWindowTitle("steelbeam")
        self.resize(800, 650)

        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        main_layout = QVBoxLayout(self.central)

        # Group 'Beam geometry'
        input_group = QGroupBox("Beam geometry")
        input_layout = QVBoxLayout(input_group)

        # Manual or Database selection
        mode_layout = QHBoxLayout()
        
        self.db_radio = QRadioButton("Database")
        self.db_radio.setChecked(True)
        
        self.manual_radio = QRadioButton("Manual")
        
        self.mode_group = QButtonGroup(self)
        self.mode_group.addButton(self.db_radio)
        self.mode_group.addButton(self.manual_radio)
        
        mode_layout.addWidget(self.db_radio)
        mode_layout.addWidget(self.manual_radio)
        mode_layout.addStretch()
        
        input_layout.addLayout(mode_layout)
        
        # Visual separator
        input_layout.addWidget(QLabel(""))

        form = QFormLayout()

        # Input lines for beam geometry
        self.code_combo = QComboBox()
        self.code_combo.addItems(["EC", "AISC"])
        self.code_combo.setCurrentText("EC")

        self.length_edit = QLineEdit("6.0")
        self.elastic_modulus_edit = QLineEdit("210000")
        self.f_yk_edit = QLineEdit("355")
        self.area_edit = QLineEdit("")
        self.area_shear_y_edit = QLineEdit("")
        self.area_shear_z_edit = QLineEdit("")
        self.inertia_y_edit = QLineEdit("")
        self.inertia_z_edit = QLineEdit("")
        self.w_pl_y_edit = QLineEdit("")
        self.w_pl_z_edit = QLineEdit("")


        # Database profile selection
        self.profile_type = QComboBox()
        self.profile_type.addItems(profile_type)

        self.profile_designation = QComboBox()
        self.profile_designation.clear()

        # ----POPULATION OF ALL THE FIELDS -----
        
        self.profile_type.currentTextChanged.connect(self._on_profile_type_changed)
        initial_selection = self.profile_type.currentText()
        if initial_selection:
            self._update_profiles(initial_selection)

        form.addRow("Analysis code", self.code_combo)
        form.addRow("Profile type", self.profile_type)
        form.addRow("Profile designation", self.profile_designation)
        form.addRow("Length [m]", self.length_edit)
        form.addRow("Elastic modulus [MPa]", self.elastic_modulus_edit)
        form.addRow("Yield strength [MPa]", self.f_yk_edit)
        form.addRow("Area [mm²]", self.area_edit)
        form.addRow("Shear area y [mm²]", self.area_shear_y_edit)
        form.addRow("Shear area z [mm²]", self.area_shear_z_edit)
        form.addRow("Inertia y [mm⁴]", self.inertia_y_edit)
        form.addRow("Inertia z [mm⁴]", self.inertia_z_edit)
        form.addRow("Plastic modulus y [mm³]", self.w_pl_y_edit)
        form.addRow("Plastic modulus z [mm³]", self.w_pl_z_edit)
        input_layout.addLayout(form)

        button_row = QHBoxLayout()
        self.calculate_button = QPushButton("Run calculation")
        self.calculate_button.clicked.connect(self.run_calculation)
        button_row.addWidget(self.calculate_button)
        button_row.addStretch()
        input_layout.addLayout(button_row)

        main_layout.addWidget(input_group)

        main_layout.addWidget(QLabel("Results"))

        self.result_box = QWebEngineView(self.central)
        self.result_box.setMinimumHeight(400)
        main_layout.addWidget(self.result_box)
        
        self.db_radio.toggled.connect(self._on_mode_changed)
        self.manual_radio.toggled.connect(self._on_mode_changed)
        self.profile_designation.currentTextChanged.connect(self._on_profile_changed)
        
        self._update_field_editability()

    def _on_mode_changed(self):
        """Manages mode switching:
        'Database' or 'Manual'
        """
        self._update_field_editability()
        
    def _on_profile_changed(self, profile_name):
        """Handles the selection of the profile from the database"""
        if self.db_radio.isChecked():
            self._load_profile_data(profile_name)
        self._update_field_editability()
        
    def _load_profile_data(self, profile_name):
        """Load the data from the profile by instantiating a temporary SteelBeam object"""
        try:
            beam = SteelBeam(
                length=1.0,                  # placeholder
                elastic_modulus=210000,      # placeholder
                f_yk=355,                   # placeholder
                profile=profile_name,
            )
            # Populate the fields with the object’s actual attributes
            self.area_edit.setText(str(beam.section_area.magnitude))
            self.area_shear_y_edit.setText(str(beam.section_area_shear_y.magnitude))
            self.area_shear_z_edit.setText(str(beam.section_area_shear_z.magnitude))
            self.inertia_y_edit.setText(str(beam.section_inertia_y.magnitude))
            self.inertia_z_edit.setText(str(beam.section_inertia_z.magnitude))
            self.w_pl_y_edit.setText(str(beam.section_w_pl_y.magnitude))
            self.w_pl_z_edit.setText(str(beam.section_w_pl_z.magnitude))
        except Exception as exc:
            QMessageBox.warning(self, "Warning", f"Error in loading the profile: {exc}")

    def _update_field_editability(self):
        """Enable/disable fields depending on the mode"""
        is_manual = self.manual_radio.isChecked()
        
        self.length_edit.setEnabled(is_manual)
        self.elastic_modulus_edit.setEnabled(is_manual)
        self.f_yk_edit.setEnabled(is_manual)
        self.area_edit.setEnabled(is_manual)
        self.area_shear_y_edit.setEnabled(is_manual)
        self.area_shear_z_edit.setEnabled(is_manual)
        self.inertia_y_edit.setEnabled(is_manual)
        self.inertia_z_edit.setEnabled(is_manual)
        self.w_pl_y_edit.setEnabled(is_manual)
        self.w_pl_z_edit.setEnabled(is_manual)
        
        # The profile drop-down menu is always enabled, but it only makes sense in the Database
        self.profile_designation.setEnabled(not is_manual)

    def _on_profile_type_changed(self, selected_text):
        if selected_text:
            self._update_profiles(selected_text)
        else:
            self.profile_designation.clear()

    def _update_profiles(self, profile_type_text):
        """Update the profiles based on the selected type"""
        self.profile_designation.blockSignals(True)  # Avoid loops during the update
        self.profile_designation.clear()
        profiles = get_profiles_by_type(profile_type_text)  # Make sure this returns a valid list
        if profiles:
            self.profile_designation.addItems(profiles)
        self.profile_designation.blockSignals(False)

    def run_calculation(self):
        try:
            # Check that the data is consistent
            if self.db_radio.isChecked():
                if not self.profile_designation.currentText():
                    raise ValueError("Select a profile from the database")
                
            beam = SteelBeam(
                length=float(self.length_edit.text()),
                elastic_modulus=float(self.elastic_modulus_edit.text()),
                f_yk=float(self.f_yk_edit.text()),
                profile=self.profile_designation.currentText() if not self.manual_radio.isChecked() else "User defined",
                section_area=float(self.area_edit.text()),
                section_area_shear_y=float(self.area_shear_y_edit.text()),
                section_area_shear_z=float(self.area_shear_z_edit.text()),
                section_inertia_y=float(self.inertia_y_edit.text()),
                section_inertia_z=float(self.inertia_z_edit.text()),
                section_w_pl_y=float(self.w_pl_y_edit.text()),
                section_w_pl_z=float(self.w_pl_z_edit.text()),
                units="SI",
            )
            beam.analysis(self.code_combo.currentText())

            latex_clean = utils.clean_handcalcs_latex(beam.normal_force_tension(render=True))

            html_content = f"""<!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <script id="MathJax-script" async
                    src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js">
                </script>
                <style>
                    body {{ font-family: Arial, sans-serif; padding: 20px; margin: 0; }}
                    h2 {{ color: #6d4aff; margin-bottom: 15px; }}
                    .calc-section {{
                        background: white; padding: 25px; border-radius: 8px;
                        border-left: 4px solid #6d4aff; overflow-x: auto;
                    }}
                    mjx-container {{ font-size: 110% !important; }}
                </style>
            </head>
            <body>
                <h2>Calculation results</h2>
                <div class="calc-section">
                    $$ {latex_clean} $$
                </div>
            </body>
            </html>"""

            self.result_box.setHtml(html_content)

        except Exception as exc:
            QMessageBox.critical(self, "Errore", str(exc))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SteelBeamApp()
    window.show()
    sys.exit(app.exec())
