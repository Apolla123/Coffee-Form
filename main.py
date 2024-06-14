import sys
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QSpinBox, QDialog, QLabel
from PyQt5.QtWidgets import QAction
import sqlite3


class AddEditCoffeeForm(QDialog):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi('addEditCoffeeForm.ui', self)

        self.setWindowTitle("Добавление/Редактирование записи о кофе")

        self.ui.save_button.clicked.connect(self.save_coffee)
        self.ui.cancel_button.clicked.connect(self.close)

        add_action = QAction("Добавить", self)
        add_action.triggered.connect(self.open_add_coffee_form)
        self.ui.menubar.addAction(add_action)

        edit_action = QAction("Редактировать", self)
        edit_action.triggered.connect(self.open_edit_coffee_form)
        self.ui.menubar.addAction(edit_action)

        self.selected_id = None

    def open_add_coffee_form(self):
        form = AddEditCoffeeForm()
        form.add_coffee()
        form.exec_()

    def open_edit_coffee_form(self):
        selected_id = self.ui.id_spinbox.value()
        coffee_info = self.get_coffee_info()

        for info in coffee_info:
            if info['ID'] == selected_id:
                form = AddEditCoffeeForm()
                form.edit_coffee(info)
                form.exec_()

    def add_coffee(self):
        self.selected_id = None
        self.clear_fields()
        self.show()

    def edit_coffee(self, coffee_info):
        self.selected_id = coffee_info['ID']
        self.fill_fields(coffee_info)
        self.show()

    def clear_fields(self):
        self.ui.id_spinbox.setValue(0)
        self.ui.name_lineedit.clear()
        self.ui.roast_lineedit.clear()
        self.ui.grind_combobox.setCurrentIndex(0)
        self.ui.taste_textedit.clear()
        self.ui.price_spinbox.setValue(0.0)
        self.ui.volume_spinbox.setValue(0)

    def fill_fields(self, coffee_info):
        self.ui.id_spinbox.setValue(coffee_info['ID'])
        self.ui.name_lineedit.setText(coffee_info['Название сорта'])
        self.ui.roast_lineedit.setText(coffee_info['Степень обжарки'])
        grind_index = self.ui.grind_combobox.findText(coffee_info['Молотый/В зёрнах'])
        self.ui.grind_combobox.setCurrentIndex(grind_index)
        self.ui.taste_textedit.setText(coffee_info['Описание вкуса'])
        self.ui.price_spinbox.setValue(float(coffee_info['Цена']))
        self.ui.volume_spinbox.setValue(coffee_info['Объем упаковки'])

    def save_coffee(self):
        selected_id = self.ui.id_spinbox.value()
        name = self.ui.name_lineedit.text()
        roast = self.ui.roast_lineedit.text()
        grind = self.ui.grind_combobox.currentText()
        taste = self.ui.taste_textedit.toPlainText()
        price = self.ui.price_spinbox.value()
        volume = self.ui.volume_spinbox.value()

        if self.selected_id is None:
            self.add_new_coffee(name, roast, grind, taste, price, volume)
        else:
            self.update_coffee(selected_id, name, roast, grind, taste, price, volume)

        self.close()

    def add_new_coffee(self, name, roast, grind, taste, price, volume):
        connection = sqlite3.connect('data/coffee.sqlite')
        cursor = connection.cursor()

        cursor.execute("INSERT INTO coffee (name, roast, grind, taste, price, volume) VALUES (?, ?, ?, ?, ?, ?)",
                       (name, roast, grind, taste, price, volume))

        connection.commit()

        cursor.close()
        connection.close()

    def update_coffee(self, selected_id, name, roast, grind, taste, price, volume):
        connection = sqlite3.connect('data/coffee.sqlite')
        cursor = connection.cursor()

        cursor.execute("UPDATE coffee SET name=?, roast=?, grind=?, taste=?, price=?, volume=? WHERE ID=?",
                       (name, roast, grind, taste, price, volume, selected_id))

        connection.commit()

        cursor.close()
        connection.close()


class CoffeeApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.ui = uic.loadUi('data/main.ui', self)

        self.setWindowTitle("Кофе")

        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)

        layout = QVBoxLayout(self.centralWidget)

        layout.addWidget(self.ui.id_spinbox)
        layout.addWidget(self.ui.name_label)
        layout.addWidget(self.ui.roast_label)
        layout.addWidget(self.ui.grind_label)
        layout.addWidget(self.ui.taste_label)
        layout.addWidget(self.ui.price_label)
        layout.addWidget(self.ui.volume_label)

        coffee_info = self.get_coffee_info()

        for info in coffee_info:
            coffee_widget = QSpinBox()
            coffee_widget.setValue(info['ID'])
            layout.addWidget(coffee_widget)

            coffee_widget = QLabel()
            coffee_widget.setText(info['Название сорта'])
            layout.addWidget(coffee_widget)

            coffee_widget = QLabel()
            coffee_widget.setText(info['Степень обжарки'])
            layout.addWidget(coffee_widget)

            coffee_widget = QLabel()
            coffee_widget.setText(info['Молотый/в зернах'])
            layout.addWidget(coffee_widget)

            coffee_widget = QLabel()
            coffee_widget.setText(info['Описание вкуса'])
            layout.addWidget(coffee_widget)

            coffee_widget = QSpinBox()
            coffee_widget.setValue(info['Цена'])
            layout.addWidget(coffee_widget)

            coffee_widget = QSpinBox()
            coffee_widget.setValue(info['Объем упаковки'])
            layout.addWidget(coffee_widget)

        self.ui.add_coffee_button.clicked.connect(self.open_add_coffee_form)
        self.ui.edit_coffee_button.clicked.connect(self.open_edit_coffee_form)

    def open_add_coffee_form(self):
        form = AddEditCoffeeForm()
        form.add_coffee()
        form.exec_()

    def open_edit_coffee_form(self):
        form = AddEditCoffeeForm()
        form.open_edit_coffee_form()
        form.exec_()

    def get_coffee_info(self):
        connection = sqlite3.connect('data/coffee.sqlite')
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM coffe")
        rows = cursor.fetchall()

        coffee_info = []
        for row in rows:
            coffee_info.append({
                'ID': row[0],
                'Название сорта': row[1],
                'Степень обжарки': row[2],
                'Молотый/В зёрнах': row[3],
                'Описание вкуса': row[4],
                'Цена': row[5],
                'Объем упаковки': row[6]
            })

        cursor.close()
        connection.close()

        return coffee_info


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CoffeeApp()
    window.show()
    sys.exit(app.exec_())
