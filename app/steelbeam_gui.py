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
    QTextEdit,
    QVBoxLayout,
    QMessageBox,
    QGroupBox,
    QHBoxLayout,
)

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from steelbeam import SteelBeam, get_profiles_by_type


class SteelBeamApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("steelbeam GUI")
        self.resize(800, 650)

        self.central = QWidget(self)
        self.setCentralWidget(self.central)

        main_layout = QVBoxLayout(self.central)

        input_group = QGroupBox("Dati beam")
        input_layout = QVBoxLayout(input_group)
        form = QFormLayout()

        self.code_combo = QComboBox()
        self.code_combo.addItems(["EC", "AISC", "NBR"])
        self.code_combo.setCurrentText("EC")

        self.length_edit = QLineEdit("6.0")
        self.elastic_modulus_edit = QLineEdit("210000")
        self.f_yk_edit = QLineEdit("355")
        self.area_edit = QLineEdit("5380")
        self.area_shear_y_edit = QLineEdit("2675")
        self.area_shear_z_edit = QLineEdit("2130")
        self.inertia_y_edit = QLineEdit("83560000")
        self.inertia_z_edit = QLineEdit("6040000")
        self.w_pl_y_edit = QLineEdit("628000")
        self.w_pl_z_edit = QLineEdit("125000")
        self.profile_combo = QComboBox()
        self.profile_combo.addItems(get_profiles_by_type("I_SECTION")[:50])
        self.profile_combo.setCurrentText("IPE300")

        form.addRow("Codice", self.code_combo)
        form.addRow("Profile", self.profile_combo)
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
        self.calculate_button = QPushButton("Calcola")
        self.calculate_button.clicked.connect(self.run_calculation)
        button_row.addWidget(self.calculate_button)
        button_row.addStretch()
        input_layout.addLayout(button_row)

        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setPlainText("Compila i valori e premi Calcola.")

        main_layout.addWidget(input_group)
        main_layout.addWidget(QLabel("Risultato"))
        main_layout.addWidget(self.result_box)

    def run_calculation(self):
        try:
            beam = SteelBeam(
                length=float(self.length_edit.text()),
                elastic_modulus=float(self.elastic_modulus_edit.text()),
                f_yk=float(self.f_yk_edit.text()),
                profile=self.profile_combo.currentText(),
                section_area=float(self.area_edit.text()),
                section_area_shear_y=float(self.area_shear_y_edit.text()),
                section_area_shear_z=float(self.area_shear_z_edit.text()),
                section_inertia_y=float(self.inertia_y_edit.text()),
                section_inertia_z=float(self.inertia_z_edit.text()),
                section_w_pl_y=float(self.w_pl_y_edit.text()),
                section_w_pl_z=float(self.w_pl_z_edit.text()),
                units="SI",
            )
            code = self.code_combo.currentText()
            beam.analysis(code)

            if code == "EC":
                result = beam.bending_moment_y()
                detail = f"bending_moment_y: {result}"
            elif code == "AISC":
                result = beam.normal_force_tension()
                detail = f"normal_force_tension: {result}"
            else:
                result = beam.bending_moment_y()
                detail = f"bending_moment_y (NBR placeholder): {result}"

            self.result_box.setPlainText(
                f"Codice: {code}\n"
                f"Profilo: {beam.profile}\n"
                f"Lunghezza: {beam.length} m\n"
                f"Area: {beam.section_area} mm²\n"
                f"{detail}"
            )
        except Exception as exc:
            QMessageBox.critical(self, "Errore", str(exc))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SteelBeamApp()
    window.show()
    sys.exit(app.exec())
