from PyQt5 import QtWidgets
from PyQt5 import QtGui
import sys
import os
from ftplib import FTP
from ftplib import error_perm


class Waffle():
    __instance = None

    @staticmethod
    def tea():
        if not Waffle.__instance:
            raise Exception("Woops. You must instantiate a Waffle instance first.")
        return Waffle.__instance

    @staticmethod
    def reset():
        Waffle.__instance = None

    def __init__(self, banana):
        if Waffle.__instance:
            raise Exception("Hey, you already have an instance. Why not using it?")
        Waffle.__instance = banana


class LoginWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.compileUiFile()

        from login_ui import Ui_LoginWindow
        self.ui = Ui_LoginWindow()
        self.ui.setupUi(self)
        self.doConnections()

    def compileUiFile(self):
        from PyQt5.uic import compileUi
        with open('login_ui.py', 'w') as fen:
            compileUi('fenestra_login.ui', fen)

    def doConnections(self):
        self.ui.btn_login.clicked.connect(self.login)

    def login(self):
        user = self.ui.ln_user.text()
        password = self.ui.ln_pass.text()
        remote = self.ui.ln_remote.text()

        Waffle.reset()
        Waffle(FTP(remote))
        Waffle.tea().encoding = 'utf-8'
        result = Waffle.tea().login(user, password)

        if result and result.split(' ')[0] == '230':
            self.mainWindow = MainWindow()
            self.mainWindow.show()
            self.close()
        else:
            print("Something went wrong.")


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.compileUiFile()

        self.local_path =  None
        self.remote_path = None
        self.curr_local = None
        self.curr_remote = None

        from fen import Ui_MainWindow
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.ln_rename.hide()
        self.ui.btn_apply_rn.hide()

        self.populate_local()
        self.populate_remote()

        self.doConnections()

    def compileUiFile(self):
        from PyQt5.uic import compileUi
        with open('fen.py', 'w') as fen:
            compileUi('fenestra_main.ui', fen)

    def populate_local(self):
        self.local_path = os.getcwd()
        self.fs_model = QtWidgets.QFileSystemModel()
        self.fs_model.setRootPath(self.local_path)
        self.ui.tree_l.setModel(self.fs_model)
        self.ui.tree_l.setRootIndex(self.fs_model.index(self.local_path))
        print('local_path:', self.local_path)
        self.ui.tree_l.selectionModel().selectionChanged.connect(self.update_curr_local)

    def populate_remote(self):
        self.remote_path = Waffle.tea().pwd()
        remote_listing = Waffle.tea().nlst()
        self.dir_model = QtGui.QStandardItemModel()
        for ls in remote_listing:
            self.dir_model.appendRow(QtGui.QStandardItem(ls))
        self.ui.list_r.setModel(self.dir_model)
        print('remote_path: ', self.remote_path)
        self.ui.list_r.selectionModel().selectionChanged.connect(self.update_curr_remote)

    def doConnections(self):
        self.ui.btn_retr.clicked.connect(self.retr)
        self.ui.btn_stor.clicked.connect(self.stor)
        self.ui.btn_rn.clicked.connect(self.rnfr_rnto)
        self.ui.btn_dele.clicked.connect(self.dele)
        self.ui.btn_rmd.clicked.connect(self.rmd)
        self.ui.btn_mkd.clicked.connect(self.mkd)
        self.ui.btn_enter_remote.clicked.connect(self.remote_enter)
        self.ui.btn_up_remote.clicked.connect(self.remote_up)
        self.ui.btn_enter_local.clicked.connect(self.local_enter)
        self.ui.btn_up_local.clicked.connect(self.local_up)

    def retr(self):
        self.tidy_up()
        if self.curr_remote is not None:
            try:
                r = Waffle.tea().retrbinary('RETR' + ' ' + self.curr_remote, open(self.curr_remote, 'wb').write)
                self.ui.label.setText(r + ' ' + self.curr_remote)
            except:
                self.ui.label.setText('Are you sure it is a file?')
                try:
                    os.remove(self.curr_remote)
                except:
                    pass
        else:
            self.ui.label.setText('Are you sure you have selected a remote file to retrieve?')

    def stor(self):
        self.tidy_up()
        if self.curr_local is not None:
            try:
                r = Waffle.tea().storbinary('STOR ' + self.curr_local, open(self.curr_local, 'rb'))
                self.ui.label.setText(r + ' ' + self.curr_local)
                self.populate_remote()
            except error_perm:
                self.ui.label.setText('Hmm... Unsuccessful. Maybe a permission issue on the server side.')
            except:
                self.ui.label.setText('Are you sure it is a file?')
                import traceback
                traceback.print_exc()


    def dele(self):
        self.tidy_up()
        if self.curr_remote is not None:
            try:
                r = Waffle.tea().delete(self.curr_remote)
                self.ui.label.setText(r + ' : ' + self.curr_remote)
                self.populate_remote()
            except error_perm:
                self.ui.label.setText('Hmm... Unsuccessful. Maybe a permission issue on the server side.')
            except:
                self.ui.label.setText('Are you sure it is a file?')
                import traceback
                traceback.print_exc()

    def rmd(self):
        self.tidy_up()
        if self.curr_remote is not None:
            try:
                r = Waffle.tea().rmd(self.curr_remote)
                self.ui.label.setText(r + ' : ' + self.curr_remote)
                self.populate_remote()
            except error_perm:
                self.ui.label.setText('Hmm... Unsuccessful. Maybe a permission issue on the server side.')
                import traceback
                traceback.print_exc()
            except:
                self.ui.label.setText('Are you sure it is a directory?')
                import traceback
                traceback.print_exc()

    def mkd(self):
        self.tidy_up()
        if self.remote_path is not None:
            try: self.ui.btn_apply_rn.clicked.disconnect()
            except: pass
            self.ui.btn_apply_rn.clicked.connect(self.apply_mkd)
            self.ui.ln_rename.show()
            self.ui.btn_apply_rn.show()
            self.ui.label.hide()

    def apply_mkd(self):
        new_name = self.ui.ln_rename.text()
        if new_name != '':
            try:
                r = Waffle.tea().mkd(new_name)
                self.tidy_up()
                self.ui.label.setText('new directory: ' + r)
                self.populate_remote()
            except error_perm:
                self.ui.label.setText('Hmm... Unsuccessful. Maybe a permission issue on the server side.')
                import traceback
                traceback.print_exc()
            except:
                self.ui.label.setText('Are you sure it is a directory?')
                import traceback
                traceback.print_exc()

    def rnfr_rnto(self):
        if self.curr_remote is not None:
            try: self.ui.btn_apply_rn.clicked.disconnect()
            except: pass
            self.ui.btn_apply_rn.clicked.connect(self.apply_rn)
            self.ui.ln_rename.show()
            self.ui.btn_apply_rn.show()
            self.ui.label.hide()
        else:
            self.ui.label.setText('Which file should I rename?')

    def apply_rn(self):
        new_name = self.ui.ln_rename.text()
        if new_name != '':
            try:
                r = Waffle.tea().rename(self.curr_remote, new_name)
                self.tidy_up()
                self.ui.label.setText(r + ': ' + new_name)
                self.populate_remote()
            except error_perm:
                self.ui.label.setText('Hmm... Unsuccessful. Maybe a permission issue on the server side.')
            except:
                self.ui.label.setText('Are you sure it is a file?')
                import traceback
                traceback.print_exc()

    def tidy_up(self):
        self.ui.label.show()
        self.ui.btn_apply_rn.hide()
        self.ui.ln_rename.hide()
        self.ui.label.setText('Ready.')

    def update_curr_local(self):
        self.tidy_up()
        index = self.ui.tree_l.selectedIndexes()[0]
        self.curr_local = index.model().itemData(index).get(0)
        print('curr_local: ', self.curr_local)

    def update_curr_remote(self):
        self.tidy_up()
        index = self.ui.list_r.selectedIndexes()[0]
        self.curr_remote = index.model().itemData(index).get(0)
        print('curr_remote: ', self.curr_remote)

    def remote_enter(self):
        self.tidy_up()
        if self.curr_remote:
            Waffle.tea().cwd(os.path.join(self.remote_path, self.curr_remote))
            self.populate_remote()
            self.curr_remote = None

    def remote_up(self):
        self.tidy_up()
        Waffle.tea().cwd((os.sep).join(self.remote_path.split(os.sep)[:-1]))
        self.populate_remote()

    def local_enter(self):
        self.tidy_up()
        if self.curr_local:
            os.chdir(os.path.join(self.local_path, self.curr_local))
            self.populate_local()
            self.curr_local = None

    def local_up(self):
        self.tidy_up()
        os.chdir('..')
        self.populate_local()

app = QtWidgets.QApplication(sys.argv)
login = LoginWindow()
login.show()

sys.exit(app.exec_())
