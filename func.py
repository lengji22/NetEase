__author__ = 'weiy'
"""功能模块。"""

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtNetwork import *
import os
import api
import shutil


class LoginWindow(QDialog):

    """我来组成Login !"""
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.main = parent
        self.setObjectName("Login")
        self.resize(200, 100)
        self.setWindowIcon(QIcon('icons/login.png'))
        self.setWindowTitle('Login')
        # 按钮start.
        self.btn_login = QPushButton('登陆', self)
        # 按钮end.
        # 标签start.
        self.lbe_user = QLabel('用户名:', self)
        self.lbe_password = QLabel('密码:', self)
        self.text_user = QLineEdit()
        self.text_pswd = QLineEdit()
        self.lbe_hide = QLabel(self)
        # 标签end.
        # -------
        # 头像下载。
        self.down_manager = QNetworkAccessManager()
        # -------
        # 布局与属性设置。
        self.set_buttons()
        self.set_login_frame()
        self.setLayout(self.vlay())
        # -------
        # 其他功能。

    def set_buttons(self):
        """
            设置所有按钮。
        """
        self.btn_login.setObjectName('logins')
        self.btn_login.clicked.connect(self.lgn)

    def set_login_frame(self):
        """
            设置基本的登陆框架。
        """
        self.text_user.setPlaceholderText("邮箱地址")
        self.text_pswd.setPlaceholderText("密码")
        self.text_pswd.setEchoMode(QLineEdit.Password)

    def vlay(self):
        """
            主布局。
        """
        vbox = QVBoxLayout()
        vbox.addWidget(self.lbe_user)
        vbox.addWidget(self.text_user)
        vbox.addWidget(self.lbe_password)
        vbox.addWidget(self.text_pswd)
        vbox.addWidget(self.lbe_hide)
        vbox.addWidget(self.btn_login)
        vbox.addStretch(1)
        return vbox

    def lgn(self):
        """
            登陆功能。
        """
        user = self.text_user.text()
        pwd = self.text_pswd.text()
        func = api.WebApi()
        # 离线功能。
        try:
            result = func.login(user, pwd)[1]
        except:
            self.lbe_hide.setText("网络不通，请检查网络。")
            return
        if result['code'] == 200:
            self.save_cookies(result['account']['userName'], result['profile']['nickname'],\
                             result['profile']['userId'])  # 保存cookies.
            self.main.btn_login.setText(result['profile']['nickname'])   # 加载昵称。
            self.main.btn_login.disconnect()
            self.main.btn_login.clicked.connect(self.main.quit_login)
            tdata = self.down_manager.get(QNetworkRequest(QUrl(result['profile']['avatarUrl'])))
            self.down_manager.finished.connect(lambda: self.load_finish(tdata, result))    # 加载头像并保存。
            self.main.result['uid'] = result['profile']['userId']
            self.main.btn_login.setToolTip("登出")
            self.main.playlist.set_list()  # 加载歌单。
        else:
            self.lbe_hide.setText('登陆失败，检查后重试。')

    def save_cookies(self, email, name, uid):
        """
            保存cookies.
        """
        try:
            os.chdir('.' + '/data' + '/cookies')
        except:
            os.mkdir('.' + '/data' + '/cookies')
            os.chdir('.' + '/data' + '/cookies')
        with open(email + '.dta', 'w') as f:
            f.write(name + '\n' + str(uid) + '\n')
        os.chdir('..')
        os.chdir('..')

    def load_finish(self, res, result):
        """
            加载头像并保存。
        """
        data = res.readAll()
        header = QFile('data/cookies/header' + result['profile']['avatarUrl'][-4:])
        header.open(QIODevice.WriteOnly)
        header.write(data)
        # 保存二进制文件。
        img = QPixmap()
        img.loadFromData(data)
        self.main.lbe_pic.setStyleSheet('border: 0px;')
        # 图片不是圆角。
        self.main.lbe_pic.setPixmap(img.scaled(40, 40))
        self.accept()

    """重写鼠标事件，实现窗口拖动。"""
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_drag = True
            self.m_DragPosition = event.globalPos()-self.pos()
            event.accept()

    def mouseMoveEvent(self, event):
        try:
            if event.buttons() and Qt.LeftButton:
                self.move(event.globalPos()-self.m_DragPosition)
                event.accept()
        except AttributeError:
            pass

    def mouseReleaseEvent(self, event):
        self.m_drag=False


class PlayList(QListWidget):
    """我是歌单列表。"""
    def __init__(self, parent):
        super(PlayList, self).__init__(parent)
        self.main = parent
        # 一些属性设置。
        self.setObjectName("playlist")
        # 加载样式。
        with open('func.qss', 'r') as q:
            self.setStyleSheet(q.read())
        # 功能区start。
        self.menu = QMenu(self)
        self.act_remove = QAction("删除", self)
        # 功能区end.
        # 加载函数。
        self.set_action()

    def set_list(self):
        """
            歌单列表。
        """
        for i in self.main.function.user_playlist(self.main.result['uid']):
            self.addItem(QListWidgetItem(QIcon('icons/Heart.png'), i['name']))
            self.main.result[i['name']] = i['id']
            # 对应歌单的id添加。
        self.clicked.connect(lambda: self.main.show_playlist(self.currentItem().text()))

    def set_action(self):
        self.act_remove.triggered.connect(self.remove_play)

    def remove_play(self):
        """
            删除歌单。
        """
        pass

    def contextMenuEvent(self, event):
        """
            右键菜单事件。
        """
        item = self.itemAt(self.mapFromGlobal(QCursor.pos()))
        if not item:
            pass
        else:
            self.menu.addAction(self.act_remove)
            self.menu.exec_(QCursor.pos())


class SongsWindow(QListWidget):
    """我来组成歌曲列表。"""
    def __init__(self, parent=None):
        super(SongsWindow, self).__init__(parent)
        # 一些属性的设置。
        self.setObjectName("currentlist")
        self.flag = True
        self.main = parent
        self.setParent(self.main)
        # 读入样式表。
        with open('func.qss', 'r') as q:
            self.setStyleSheet(q.read())
        # 默认隐藏。
        self.hide()
        # 功能区start。
        self.menu = QMenu(self)
        self.act_clear = QAction('清空', self)
        self.act_remove = QAction('删除', self)
        # 功能区end.
        # 加载函数。
        self.set_action()
        self.set_menu()
        # 连接信号。
        self.itemDoubleClicked.connect(lambda: self.main.set_song(self.currentItem().text().split(' - ')[1]\
            ,self.currentItem().text().split(' - ')[0]))
        self.itemDoubleClicked.connect(lambda: self.main.play_song())

    def set_menu(self):
        """
            设置右键菜单。
        """
        self.menu.setObjectName("rightmenu")

    def set_action(self):
        """
            设置所有的action.
        """
        self.act_clear.triggered.connect(self.clears)
        self.act_remove.triggered.connect(self.remove)

    def clears(self):
        """
            清空功能。
        """
        self.clear()
        self.main.stop_song()
        shutil.rmtree('data/music/')
        os.makedirs('.' + '/data/music')
        os.makedirs('.' + '/data/music/load')

    def remove(self):
        """
            删除功能。
        """
        os.remove('data/music/' + self.currentItem().text().replace(':', '.'))
        self.takeItem(self.currentRow())
        self.main.stop_song()
        try:
            content = self.currentItem().text().split(' - ')
            name = content[0]
            author = content[1]
            self.main.set_song(name, author)
            self.main.play_song()
        except AttributeError:
            pass

    def contextMenuEvent(self, event):
        """
            右键点击事件。
        """
        item = self.itemAt(self.mapFromGlobal(QCursor.pos()))
        if not item:
            self.menu.addAction(self.act_clear)
        else:
            self.menu.addAction(self.act_remove)
            self.menu.addAction(self.act_clear)
        self.menu.exec_(QCursor.pos())



