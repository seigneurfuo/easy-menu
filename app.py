import json
import os
import sys
from pathlib import Path

from PyQt5.QtCore import QSize, Qt, QProcess
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton, QApplication, QMainWindow, QWidget, QGridLayout, QScrollArea
from PyQt5.uic import loadUi


# noinspection PyShadowingNames
class CategoryTab(QWidget):
    def __init__(self, parent, config, category):
        super().__init__()

        self.parent = parent
        self.config = config
        self.category = category

        self.label = self.category["label"]

        self.icon = QIcon()
        if "icon" in self.category and self.category["icon"]:
            self.icon = self.icon.fromTheme(self.category["icon"])

        self.init_ui()

    def init_ui(self):
        self.scroll_area_widget_contents_layout_layout = QGridLayout()

        self.scroll_area_widget_contents_layout = QGridLayout()
        self.scroll_area_widget_contents_layout.addLayout(self.scroll_area_widget_contents_layout_layout, 0, 0, 0, 0)

        self.scroll_area_widget_contents = QWidget()
        self.scroll_area_widget_contents.setLayout(self.scroll_area_widget_contents_layout)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area.setWidget(self.scroll_area_widget_contents)

        self.layout = QGridLayout()
        self.layout.addWidget(self.scroll_area)
        self.setLayout(self.layout)

    def fill_applications(self, ):
        row_index = 0
        col_index = 0

        for index, application in enumerate(self.category["applications"]):
            application_button = QToolButton()
            application_button.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
            application_button.setText(application["label"])
            application_button.setFixedSize(self.config["buttons_size"], self.config["buttons_size"])

            # Le commentaire n'est pas obligatoire
            #if "comment" in application:
            #    application_button.setToolTip(application["comment"])

            application_button.setToolTip(application["label"])

            # ----- Icone -----

            if "icon" in application and application["icon"]:
                icon = QIcon.fromTheme(application["icon"])
            else:
                icon = QIcon.fromTheme("question")

            application_button.setIcon(icon)
            application_button.setIconSize(
                QSize(int(application_button.height() - 32), int(application_button.width() - 32)))

            # Evenement au clic
            application_button.clicked.connect(
                lambda lamdba, application=application: self.parent.launch_application(application))

            # Ligne suivante si maximal atteinds
            if index != 0 and index % self.config["buttons_per_row"] == 0:
                col_index = 0
                row_index += 1

            self.scroll_area_widget_contents_layout_layout.addWidget(application_button, row_index, col_index)
            col_index += 1


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.app_name = "easymenu"

        self.config_filepath = os.path.join(Path.home(), ".config/{}.json".format(self.app_name.lower()))
        self.config = None

        self.init_ui()
        self.init_events()

        if self.load_config_file():
            self.fill_tabs()
        else:
            msg = "Fichier de configuration non trouvé ! ({})".format(self.config_filepath)
            self.statusbar.showMessage(msg)

    def init_ui(self):
        loadUi(os.path.join(os.path.dirname(__file__), "app.ui"), self)
        self.setWindowTitle(self.app_name)

    def init_events(self):
        self.action_quit.triggered.connect(self.close)
        self.action_reload_config_file.triggered.connect(self.reload_config_file)

    def load_config_file(self):
        if not os.path.isfile(self.config_filepath):
            return False

        with open(self.config_filepath, "r") as config_file:
            self.config = json.load(config_file)
            return True

    def remove_tabs(self):
        self.tab_widget.clear()

    def fill_tabs(self):
        for category in self.config["categories"]:
            category_tab = CategoryTab(self, self.config, category)
            category_tab.fill_applications()

            self.tab_widget.addTab(category_tab, category_tab.icon, category_tab.label)

    def reload_config_file(self):
        self.remove_tabs()
        self.load_config_file()
        self.fill_tabs()

    def launch_application(self, application):
        process = QProcess.startDetached(application["executable"])
        if not process:
            self.statusbar.showMessage("Erreur lors du lancement de l'éxécutable !")


if __name__ == "__main__":
    import cgitb

    cgitb.enable()

    qapplication = QApplication(sys.argv)

    mainwindow = MainWindow()
    mainwindow.move(qapplication.desktop().screen().rect().center() - mainwindow.rect().center())
    # mainwindow.showFullScreen()
    mainwindow.show()

    qapplication.exec()
