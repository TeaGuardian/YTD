import sys
import os
import sqlite3
import time

from PyQt5.QtWidgets import QWidget, QTabWidget, QProgressBar, QPushButton, QLabel, QFrame, QLineEdit, QFileDialog
from PyQt5.QtWidgets import QTableWidget, QComboBox, QCheckBox, QSpinBox, QStatusBar, QMainWindow, QApplication
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QDialogButtonBox, QVBoxLayout
from PyQt5.QtCore import QThread, QObject, pyqtSignal, pyqtSlot, QMetaObject, QCoreApplication, QTimer
from PyQt5.QtGui import QPixmap, QColor
from urllib import request
from pytube import YouTube
import psutil
import moviepy.editor as mpe


def format(va):
    """приведение размера файла к удобному виду"""
    mer = ['b', 'Kb', 'Mb', 'Gb']
    for i in range(len(mer)):
        if va // (1024 ** i) <= 1024:
            return str(round(va / (1024 ** i), i)) + mer[i]
    return 'too big'


class MainWindow(object):
    def setupUi(self, window):
        """создание объектов формы"""
        window.setObjectName("MainWindow")
        window.resize(570, 575)
        self.w, self.h = self.size().width(), self.size().height()
        self.centralwidget = QWidget(window)
        self.centralwidget.setObjectName("centralwidget")
        self.tabWidget = QTabWidget(self.centralwidget)
        self.tabWidget.setTabPosition(QTabWidget.North)
        self.tabWidget.setTabShape(QTabWidget.Rounded)
        self.tab_1 = QWidget()
        self.progress_v = QProgressBar(self.tab_1)
        self.progress_v.setProperty("value", 0)
        self.progress_l = QProgressBar(self.tab_1)
        self.progress_l.setProperty("value", 0)
        self.queue = QTableWidget(self.tab_1)
        self.queue.setColumnCount(5)
        self.queue.setHorizontalHeaderLabels(["name", "link", "patch", "info", "status"])
        self.label_disk = QLabel(self.tab_1)
        self.tabWidget.addTab(self.tab_1, "")
        self.tab_2 = QWidget()
        self.path = QLabel(self.tab_2)
        self.path.setFrameShape(QFrame.WinPanel)
        self.set_path = QPushButton(self.tab_2)
        self.link = QLineEdit(self.tab_2)
        self.name = QLineEdit(self.tab_2)
        self.name.setFrame(True)
        self.clear_b = QPushButton(self.tab_2)
        self.ok_b = QPushButton(self.tab_2)
        self.list_1 = QComboBox(self.tab_2)
        self.image = QLabel(self.tab_2)
        self.view_image = QCheckBox(self.tab_2)
        self.view_image.setChecked(True)
        self.tabWidget.addTab(self.tab_2, "")
        self.tab_3 = QWidget()
        self.save_q, self.comp = QCheckBox(self.tab_3), QCheckBox(self.tab_3)
        self.save_q.setChecked(True)
        self.save_d, self.show_webm = QCheckBox(self.tab_3), QCheckBox(self.tab_3)
        self.save_d.setChecked(True)
        self.label_text, self.label_text1 = QLabel(self.tab_3), QLabel(self.tab_3)
        self.save_e = QCheckBox(self.tab_3)
        self.save_e.setChecked(True)
        self.save_h = QCheckBox(self.tab_3)
        self.label_text2 = QLabel(self.tab_3)
        self.buffer_size = QSpinBox(self.tab_3)
        self.buffer_size.setMaximum(9999)
        self.clear_b_2 = QPushButton(self.tab_3)
        self.label = QLabel(self.tab_3)
        self.tabWidget.addTab(self.tab_3, "")
        self.tab_4 = QWidget()
        self.history = QTableWidget(self.tab_4)
        self.history.setColumnCount(3)
        self.history.setHorizontalHeaderLabels(["link", "info", "status"])
        self.choose_number = QSpinBox(self.tab_4)
        self.download_b = QPushButton(self.tab_4)
        self.delete_b = QPushButton(self.tab_4)
        self.tabWidget.addTab(self.tab_4, "")
        window.setCentralWidget(self.centralwidget)
        self.statusbar = QStatusBar(window)
        window.setStatusBar(self.statusbar)
        self.retranslateUi(window)
        QMetaObject.connectSlotsByName(window)
        self.pixmap = QPixmap()
        self.history.setEditTriggers(self.history.NoEditTriggers)
        self.queue.setEditTriggers(self.queue.NoEditTriggers)
        a, a1 = lambda o, t: o.setChecked(bool(int(t))), lambda o: str(1 if o.isChecked() else 0)
        b, b1 = lambda o, t: o.setText(t), lambda o: o.text()
        c, c1 = lambda o, t: o.setValue(int(t)), lambda o: str(o.value())
        self.setable_flags = {'image_f': [self.view_image, a, a1], 'patch': [self.path, b, b1],
                              'save_d': [self.save_d, a, a1], 'save_q': [self.save_q, a, a1],
                              'save_e': [self.save_e, a, a1], 'save_h': [self.save_h, a, a1],
                              'buffer_size': [self.buffer_size, c, c1], 'webm': [self.show_webm, a, a1],
                              'compensate': [self.comp, a, a1]}

    def retranslateUi(self, MainWindow):
        """назначение подсказок и имён"""
        _translate = QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "YouTube Downloader v0.0.0"))
        self.progress_v.setToolTip(_translate("MainWindow", "video download progress"))
        self.progress_v.setAccessibleName(_translate("MainWindow", "progress"))
        self.progress_l.setToolTip(_translate("MainWindow", "list progress"))
        self.progress_l.setAccessibleName(_translate("MainWindow", "progress"))
        self.queue.setToolTip(_translate("MainWindow", "download queue"))
        self.label_disk.setToolTip(_translate("MainWindow", "remaining free disk space"))
        self.label_disk.setText(_translate("MainWindow", "remaining free disk space:"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_1), _translate("MainWindow", "loading"))
        self.path.setToolTip(_translate("MainWindow", "save path"))
        self.path.setText(_translate("MainWindow", "path"))
        self.set_path.setToolTip(_translate("MainWindow", "choose save path"))
        self.set_path.setText(_translate("MainWindow", "..."))
        self.link.setToolTip(_translate("MainWindow", "link to the source from YouTube"))
        self.link.setText(_translate("MainWindow", "link"))
        self.name.setToolTip(_translate("MainWindow", "under what name to save the file"))
        self.name.setText(_translate("MainWindow", "name"))
        self.clear_b.setText(_translate("MainWindow", "CANCEL"))
        self.ok_b.setText(_translate("MainWindow", "OK"))
        self.list_1.setToolTip(_translate("MainWindow", "video resolution"))
        self.image.setText(_translate("MainWindow", ""))
        self.view_image.setToolTip(_translate("MainWindow", "show the cover image of the video"))
        self.view_image.setText(_translate("MainWindow", "view image"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("MainWindow", "download"))
        self.save_q.setText(_translate("MainWindow", "in the queue"))
        self.comp.setText(_translate("MainWindow", "compensate for the lack of sound"))
        self.comp.setToolTip(_translate("MainWindow", "adds an audio track if it is not present by default"))
        self.save_d.setText(_translate("MainWindow", "downloaded"))
        self.show_webm.setText(_translate("MainWindow", "show *.webm in list"))
        self.label_text.setText(_translate("MainWindow", "Save in history:"))
        self.label_text1.setText(_translate("MainWindow", "Downloading settings:"))
        self.save_e.setText(_translate("MainWindow", "errors"))
        self.save_h.setText(_translate("MainWindow", "clear history when closing"))
        self.label_text2.setToolTip(_translate("MainWindow", "at zero is not limited"))
        self.label_text2.setText(_translate("MainWindow", "max buffer size:"))
        self.buffer_size.setToolTip(_translate("MainWindow", "at zero is not limited"))
        self.clear_b_2.setText(_translate("MainWindow", "clear history"))
        self.label.setText("designed by " + '<a href="https://github.com/TeaGuardian">TeaGuardian</a>')
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_3), _translate("MainWindow", "settings"))
        self.choose_number.setPrefix(_translate("MainWindow", "number: "))
        self.download_b.setText(_translate("MainWindow", "download by number"))
        self.delete_b.setText(_translate("MainWindow", "delete by number"))
        self.delete_b.setToolTip(_translate("MainWindow", "delete from history"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_4), _translate("MainWindow", "history"))

    def resizeEvent(self, event):
        """настройка зависимости размеров элементов от размеров окна"""
        w1, h1 = self.size().width(), self.size().height()
        w, h = w1 / self.w, h1 / self.h
        self.tabWidget.setGeometry(*map(int, (0 * w, 0 * h, 570 * w, 570 * h)))
        self.progress_v.setGeometry(*map(int, (0 * w, 480 * h, 560 * w, 23 * h)))
        self.progress_l.setGeometry(*map(int, (0 * w, 450 * h, 561 * w, 23 * h)))
        self.queue.setGeometry(*map(int, (0 * w, 0 * h, 561 * w, 440 * h)))
        self.save_e.setGeometry(*map(int, (10 * w, 80 * h, 91 * w, 21 * h)))
        self.label_text.setGeometry(*map(int, (10 * w, 10 * h, 101 * w, 21 * h)))
        self.label_text1.setGeometry(*map(int, (280 * w, 10 * h, 111 * w, 21 * h)))
        self.save_d.setGeometry(*map(int, (10 * w, 40 * h, 101 * w, 17 * h)))
        self.show_webm.setGeometry(*map(int, (280 * w, 40 * h, 131 * w, 17 * h)))
        self.save_q.setGeometry(*map(int, (10 * w, 60 * h, 101 * w, 20 * h)))
        self.comp.setGeometry(*map(int, (280 * w, 60 * h, 181 * w, 20 * h)))
        self.view_image.setGeometry(*map(int, (469 * w, 130 * h, 81 * w, 21 * h)))
        self.image.setGeometry(*map(int, (0 * w, 160 * h, 561 * w, 355 * h)))
        self.list_1.setGeometry(*map(int, (0 * w, 130 * h, 310 * w, 22 * h)))
        self.ok_b.setGeometry(*map(int, (320 * w, 130 * h, 71 * w, 23 * h)))
        self.clear_b.setGeometry(*map(int, (394 * w, 130 * h, 71 * w, 23 * h)))
        self.name.setGeometry(*map(int, (0 * w, 90 * h, 561 * w, 31 * h)))
        self.link.setGeometry(*map(int, (0 * w, 50 * h, 561 * w, 31 * h)))
        self.set_path.setGeometry(*map(int, (510 * w, 10 * h, 41 * w, 31 * h)))
        self.path.setGeometry(*map(int, (0 * w, 10 * h, 501 * w, 31 * h)))
        self.label_disk.setGeometry(*map(int, (0 * w, 510 * h, 561 * w, 16 * h)))
        self.download_b.setGeometry(*map(int, (240 * w, 10 * h, 150 * w, 31 * h)))
        self.delete_b.setGeometry(*map(int, (400 * w, 10 * h, 150 * w, 31 * h)))
        self.choose_number.setGeometry(*map(int, (10 * w, 10 * h, 221 * w, 31 * h)))
        self.history.setGeometry(*map(int, (0 * w, 60 * h, 561 * w, 471 * h)))
        self.label.setGeometry(*map(int, (0 * w, 510 * h, 561 * w, 20 * h)))
        self.clear_b_2.setGeometry(*map(int, (10 * w, 160 * h, 161 * w, 31 * h)))
        self.buffer_size.setGeometry(*map(int, (100 * w, 130 * h, 71 * w, 22 * h)))
        self.label_text2.setGeometry(*map(int, (10 * w, 130 * h, 91 * w, 16 * h)))
        self.save_h.setGeometry(*map(int, (10 * w, 100 * h, 151 * w, 30 * h)))
        self.image.setPixmap(self.pixmap.scaled(int(561 * self.size().width() / self.w),
                                                int(400 * self.size().height() / self.h)))


class MyWidget(QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.colors = {"or": [230, 150, 40], "re": [180, 20, 20], "bl": [80, 180, 255], "gr": [90, 230, 100]}
        self.setupUi(self)
        self.tabWidget.setCurrentWidget(self.tab_2)
        self.initUI()

    def initUI(self):
        self.link.editingFinished.connect(self.url_imagen)
        self.set_path.clicked.connect(self.choose_patch)
        if self.try_open('settings.ytb'):
            self.import_setings()
        self.view_image.stateChanged.connect(self.hide_image)
        self.show_webm.stateChanged.connect(self.hide_webm)
        self.thread = QThread()
        self.thread_info = GetVideoInfo()
        self.thread_info.moveToThread(self.thread)
        self.thread_info.s_w = self.show_webm.isChecked()
        self.thread_info.text_value.connect(self.work_with_ds)
        self.thread_info.name_value.connect(self.set_name)
        self.thread_info.image.connect(self.set_pixmap)
        self.lo_thread = QThread()
        self.lo_function = Download()
        self.lo_function.moveToThread(self.lo_thread)
        self.lo_function.finished.connect(self.progress)
        self.lo_function.progress.connect(self.progress)
        self.lo_function.error_load.connect(self.load_error)
        self.ok_b.clicked.connect(self.add_in_queue)
        self.queue_now, self.content, self.selec = [], {}, []
        self.download_b.clicked.connect(self.add_video)
        self.delete_b.clicked.connect(self.delete_video)
        self.timer = QTimer()
        self.timer.timeout.connect(self.step)
        self.timer.start(500)


    def closeEvent(self, event):
        """сохранение настроек и списка после закрытия"""
        settings = []
        for i in self.setable_flags.keys():
            settings.append(f'{i}={self.setable_flags[i][2](self.setable_flags[i][0])}\n')
        with open('settings.ytb', encoding='UTF-8', mode='w+') as fi:
            fi.writelines(settings)
        self.set_bd()

    def try_open(self, file):
        """проверка файла настроек на доступность"""
        mes = "the file '{file}' is damaged\n(manual removal is required)\nContinue ignoring the error?"
        try:
            f = open(file)
            f.close()
            return True
        except FileNotFoundError:
            return False
        except Exception as ex:
            dlg = ErrorDialog(mes)
            if dlg.exec():
                return False
            else:
                raise Exception(f"the error wasn't ignored: {ex}")
            return False

    def hide_image(self, sta):
        """настройка отображения привью видео"""
        if self.view_image.isChecked():
            self.image.show()
        else:
            self.image.hide()

    def hide_webm(self, sta):
        """настройка отображения webm варианта видео"""
        self.thread_info.s_w = self.show_webm.isChecked()

    def choose_patch(self):
        """выбор деректории для сохранения"""
        dirlist = QFileDialog.getExistingDirectory(self, "выбрать папку", ".")
        self.path.setText(dirlist)

    def import_setings(self):
        """применение настроек из файла"""
        settings = {}
        with open('settings.ytb', encoding='UTF-8', mode='r+') as fi:
            for i in fi.readlines():
                try:
                    data = i.rstrip('\n').split('=')
                    settings[data[0]] = data[1]
                except Exception:
                    fi.close()
                    os.remove('settings.ytb')
                    return True
        for i in settings.keys():
            if i in self.setable_flags.keys():
                self.setable_flags[i][1](self.setable_flags[i][0], settings[i])
        self.start_bd()

    def progress(self, prs):
        """визуализации загрузки"""
        self.progress_v.setValue(prs)
        if self.comp.isChecked() and prs == 100 and "audio: no (" in self.selec[3]\
                and self.lo_thread.isFinished():
            os.remove(self.lo_function.name_v)
            os.remove(self.lo_function.name_a)
        if prs == 100:
            row = self.selec[6]
            self.queue_now[row][4] = "done"
            self.selec[4] = "done"
            self.queue.setItem(row, 4, QTableWidgetItem("done"))
            self.queue.item(row, 4).setBackground(QColor(*self.colors["gr"]))

    def load_error(self, signal):
        self.lo_thread.terminate()
        row = self.selec[6]
        self.queue_now[row][4] = "error"
        self.queue.setItem(row, 4, QTableWidgetItem("error"))
        self.queue.item(row, 4).setBackground(QColor(*self.colors["re"]))
        self.progress_v.setValue(0)
        dlg = ErrorDialog(f'{self.selec[0]}\n{self.selec[1]}\n{signal}\nset "waiting" state?')
        self.selec[4] = "error"
        if dlg.exec():
            self.queue_now[row][4] = "waiting"
            self.queue.setItem(row, 4, QTableWidgetItem("waiting"))
            self.queue.item(row, 4).setBackground(QColor(*self.colors["or"]))
        else:
            os.remove(self.selec[0])
            return True

    def select(self):
        for i in range(len(self.queue_now) - 1, -1, -1):
            if "waiting" in self.queue_now[i][4]:
                return self.queue_now[i]
        return None

    def step(self):
        if len(self.selec) == 0 or self.selec[4] == "done" or self.selec[4] == "error":
            rez = self.select()
            if rez is not None:
                self.selec = rez[:]
                self.download(rez[1], rez[0], rez[5], rez[3])
                bar = len(list(map(lambda x: x[4] == "done", self.queue_now))) / len(self.queue_now)
                self.progress_l.setValue(int(bar * 100))
        if self.selec:
            if self.selec[4] in ["loading", "waiting"] and not self.lo_thread.isRunning():
                self.load_error("thread disconected with errors")
            if self.selec[4] == "loading":
                try:
                    code = request.urlopen(self.selec[1], timeout=2).getcode()
                    if code != 200:
                        self.load_error(f"HTTP error code: {code}")
                except Exception as ex:
                    self.load_error(f"unexpected error\n{str(ex)}\n(possible connection problems)")

    def download(self, link, name, id, data):
        time.sleep(1)
        self.lo_thread.terminate()
        self.lo_function.teg = id
        self.lo_function.link = link
        self.lo_function.name = name
        row = self.selec[6]
        self.queue.setItem(row, 4, QTableWidgetItem("loading"))
        self.queue.item(row, 4).setBackground(QColor(*self.colors["bl"]))
        self.queue_now[row][4] = "loading"
        self.selec[4] = "loading"
        self.lo_function.comp_f = self.comp.isChecked() if "audio: no (" in data else False
        self.lo_thread.started.connect(self.lo_function.run)
        self.lo_thread.start()
        self.progress_v.setValue(10)

    def work_with_ds(self, text):
        """обработка предлагаемых к загрузке вариантов"""
        if 'rez' in text:
            name, itag, value = text.split('=')
            self.list_1.addItem(value)
            self.content[value] = int(itag)

    def add_in_queue(self):
        """добавление в очередь загрузки"""
        if len(self.content.keys()) < 1:
            self.url_imagen(True)
            return True
        files, index = list(map(lambda x: x.split('.')[0], os.listdir(self.path.text()))), 0
        queue_files, name_f = list(map(lambda x: x[0], self.queue_now)), self.name.text()
        if any([i in name_f for i in '\/|?.><":']):
            dlg = ErrorDialog('cannot contain\n\/|?.><":\nreplace?')
            if dlg.exec():
                for i in '\/|?.><":':
                    name_f = "".join(name_f.split(i))
                self.name.setText(name_f)
            else:
                return True
        name_f_2 = self.path.text() + "/" + name_f + "." + self.list_1.currentText().split(":")[0]
        if name_f in files or name_f_2 in queue_files:
            while f'{name_f}_{index}' in files or name_f_2 in queue_files:
                index += 1
                name_f_2 = self.path.text() + f"/{name_f}_{index}." + self.list_1.currentText().split(":")[0]
            name_f_2 = self.path.text() + f"/{name_f}_{index}." + self.list_1.currentText().split(":")[0]
            name_f = f'{name_f}_{index}'
            dlg = ErrorDialog(f'{self.name.text()}\nexists, save as\n{name_f} ?')
            if dlg.exec():
                pass
            else:
                return True
        row = self.queue.rowCount()
        set = [name_f_2, self.link.text(), self.path.text(), self.list_1.currentText(), 'waiting',
               self.content[self.list_1.currentText()], row]
        if set not in self.queue_now:
            self.queue.insertRow(row)
            for i in range(5):
                self.queue.setItem(row, i, QTableWidgetItem(set[i]))
            self.queue_now.append(set[:])
        self.queue.item(row, 4).setBackground(QColor(*self.colors["or"]))
        disk = self.path.text().split(":")[0] + ":"
        self.label_disk.setText(f"remaining free disk space: {format(psutil.disk_usage(disk).free)}")

    def set_name(self, text):
        """установка имени файла"""
        self.name.setText(text)

    def set_pixmap(self, pix):
        """открытие картинки привью"""
        if pix == bytes('error'.encode()):
            self.image.setText(' ' * 40 + 'SERVER ERROR')
        else:
            self.pixmap.loadFromData(pix)
            self.image.setPixmap(self.pixmap.scaled(int(561 * self.size().width() / self.w),
                                                    int(400 * self.size().height() / self.h)))
            self.hide_image(False)

    def url_imagen(self, osf=False):
        """получение информации о видео"""
        if self.thread_info.link == self.link.text() or osf:
            return True
        try:
            self.list_1.clear()
            self.content.clear()
            self.thread.terminate()
            self.thread_info.link = self.link.text()
            self.thread.started.connect(self.thread_info.run)
            self.name.setText("")
            self.thread.start()
        except Exception:
            self.image.setText(' ' * 40 + 'ERROR')

    def add_video(self):
        row = self.choose_number.value() - 1
        try:
            link_d = self.history.model().index(row, 0).data()
        except Exception as ex:
            dlg = ErrorDialog(f'WARNING: {ex}')
            if dlg.exec():
                pass
            return True
        self.link.setText(link_d)
        self.tabWidget.setCurrentWidget(self.tab_2)

    def delete_video(self):
        row = self.choose_number.value() - 1
        try:
            link_d = self.history.model().index(row, 0).data()
            info_d = self.history.model().index(row, 1).data()
            state_d = self.history.model().index(row, 2).data()
        except Exception as ex:
            dlg = ErrorDialog(f'WARNING: {ex}')
            if dlg.exec():
                pass
            return True
        con = sqlite3.connect("YTD_list.db")
        cur = con.cursor()
        cur.execute(f"""delete from videos where state == '{state_d}' and link == '{link_d}' 
        and info == '{info_d}'""")
        self.history.removeRow(row)
        con.commit()
        con.close()

    def set_bd(self):
        if self.save_h.isChecked():
            return True
        con = sqlite3.connect("YTD_list.db")
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS videos(
           link TEXT,
           info TEXT,
           state TEXT);
        """)
        con.commit()
        for i in self.queue_now:
            for j in [(self.save_d.isChecked(), "done"), (self.save_q.isChecked(), "waiting"),
                      (self.save_e.isChecked(), "error"), (self.save_q.isChecked(), "loading"),]:
                if j[0] and i[4] == j[1]:
                    cur.execute(f"""INSERT INTO videos(link, info, state) 
                    VALUES('{i[1]}', '{i[3]}', '{i[4]}');""")
                elif not j[0]:
                    dat = cur.execute(f"""SELECT link, info, state from videos where state == '{j[1]}'""").fetchmany(2)
                    for poi in dat:
                        cur.execute(f"""UPDATE videos set state = 'to delete' where link = '{poi[0]}' 
                        and info = '{poi[1]}' and state = '{poi[2]}'""")
                con.commit()
        dater = cur.execute("""SELECT COUNT(state) from videos""").fetchone()
        self.choose_number.setMaximum(dater[0] + 2)
        if dater[0] >= self.buffer_size.value():
            cur.execute(f"""delete from videos where state == 'to delete'""")
            con.commit()
        con.close()

    def start_bd(self):
        if not self.try_open("YTD_list.db"):
            return True
        con = sqlite3.connect("YTD_list.db")
        cur = con.cursor()
        dat = cur.execute("""SELECT link, info, state from videos""").fetchall()
        if len(dat) >= self.buffer_size.value():
            dlg = ErrorDialog(f'WARNING: buffer full.')
            if dlg.exec():
                pass
        for i in dat:
            row = self.history.rowCount()
            self.history.insertRow(row)
            for x in range(3):
                self.history.setItem(row, x, QTableWidgetItem(i[x]))
                col = {"waiting": self.colors["or"], "error": self.colors["re"], "done": self.colors["gr"],
                       "to delite": [150, 150, 200], "loading": self.colors["or"]}
            self.history.item(row, 2).setBackground(QColor(*col[i[2]]))


class ErrorDialog(QDialog):
    """конструктор сообщений об ошибках"""
    def __init__(self, mes):
        super().__init__()
        self.setWindowTitle("SOMETHING WENT WRONG")
        QBtn = QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        self.buttonBox = QDialogButtonBox(QBtn)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        self.layout = QVBoxLayout()
        message = QLabel(mes)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)


class GetVideoInfo(QObject):
    """получение информации о видео в параллельном потоке"""
    text_value = pyqtSignal(str)
    name_value = pyqtSignal(str)
    image = pyqtSignal(bytes)
    comp_f = False

    def __init__(self):
        super().__init__()
        self.link, self.s_w, self.comp = '', True, False

    def get_image(self, link):
        error = 'https://ih1.redbubble.net/image.585700572.9015/flat,1000x1000,075,f.jpg'
        if 'yout' not in link:
            link = ''
        else:
            link = link.split('/')[-1]
            if '?f' in link:
                id = link.split('?f')[0]
            elif '?v=' in link:
                id = link.split('?v=')[-1]
            else:
                id = link
            link = f"http://i1.ytimg.com/vi/{id}/maxresdefault.jpg"
        try:
            data = request.urlopen(link).read()
        except Exception:
            try:
                data = request.urlopen(error).read()
            except Exception:
                return bytes('error'.encode())
        return data

    @pyqtSlot()
    def run(self):
        try:
            yt = YouTube(self.link)
            self.name_value.emit(yt.title)
            a_v = format(yt.streams.filter(only_audio=True).first().filesize_approx)
            streams = yt.streams.filter(type='video')
            for video in streams:
                lct = f'rez={video.itag}={video.mime_type.split("/")[-1]}: {video.resolution}; ' \
                      f'{video.fps}fps; {format(video.filesize_approx)}; ' \
                      f'audio: {"yes" if video.is_progressive else f"no ({a_v})"}'
                if 'webm' not in lct or self.s_w:
                    self.text_value.emit(lct)
        except Exception as ex:
            print(ex)
            self.name_value.emit(f'ERROR SIGNAL: {ex}')
        self.image.emit(self.get_image(self.link))


class Download(QObject):
    """скачивание видео в параллельном потоке"""
    progress = pyqtSignal(int)
    error_load = pyqtSignal(str)
    finished = pyqtSignal(int)
    link, name, teg, name_v, name_a = "", "", 22, "", ""
    comp_f = False

    def __init__(self):
        super().__init__()

    @pyqtSlot()
    def run(self):
        try:
            self.name_v = self.name
            if self.comp_f:
                self.name_v, self.name_a = "_d.".join(self.name.split(".")), self.name.split(".")[0] + "_d.mp3"
                YouTube(self.link).streams.filter(only_audio=True).first().download(filename=self.name_a)
            self.yt = YouTube(self.link, on_progress_callback=self.progress_fun, on_complete_callback=self.final())
            self.streams = self.yt.streams.filter(type='video')
            self.st = self.streams.get_by_itag(int(self.teg))
            self.st.download(filename=self.name_v)
        except Exception as ex:
            print(400, ex)
            self.error_load.emit(str(ex))

    def progress_fun(self, stream, chunk, bytes_remaining):
        prs = 100 - int((float(bytes_remaining) / float(stream.filesize)) * 100)
        if self.comp_f and prs == 100:
            video, audio = mpe.VideoFileClip(self.name_v), mpe.AudioFileClip(self.name_a)
            final = video.set_audio(audio)
            final.write_videofile(self.name)
            audio.close(), video.close()
        self.progress.emit(prs)

    def final(self, *arg):
        self.finished.emit(100)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MyWidget()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec_())