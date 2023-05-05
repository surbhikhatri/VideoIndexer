import platform
import os
import sys

from PyQt5 import QtWidgets, QtGui, QtCore
import vlc


class VideoPlayer(QtWidgets.QMainWindow):

    class MyTreeWidgetItem(QtWidgets.QTreeWidgetItem):
        def __init__(self, parent=None, idx=0, frame_position=0):
            super().__init__(parent)
            self.idx = idx
            self.frame_position = frame_position

    def __init__(self, master=None, scenes=None, total_frames=0):
        QtWidgets.QMainWindow.__init__(self, master)
        self.setWindowTitle("Interactive Media Player")

        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()
        self.media = None

        self.scene_list = scenes
        self.total_frames = total_frames

        self.curr_idx = 0
        self.is_paused = True

        self.highlight = QtGui.QBrush(QtGui.QColor(205, 232, 255, 255))
        self.no_highlight = QtGui.QBrush(QtGui.QColor(205, 232, 255, 0))

        self.create_ui()

    def create_ui(self):
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        # File menu
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu("File")
        open_action = QtWidgets.QAction("Load Media File", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        # Hierarchical video table of contents
        self.tree = QtWidgets.QTreeWidget()
        self.tree.setColumnCount(1)
        self.tree.itemClicked.connect(self.handleItemClick)

        # List of items store frame position
        self.item_list = []

        tree_items = []
        content_idx = 0
        for i in range(len(self.scene_list)):
            scene_item = self.MyTreeWidgetItem(None, -1)
            scene_item.setText(0, f'Scene {i}')
            for j, shot in enumerate(self.scene_list[i]):
                if len(shot.subshots) == 0:
                    frame_position = shot.start_frame / self.total_frames
                    shot_item = self.MyTreeWidgetItem(
                        None, content_idx, frame_position)
                    shot_item.setText(0, f'Shot {j}')
                    self.item_list.append(shot_item)
                    content_idx += 1
                    scene_item.addChild(shot_item)
                else:
                    shot_item = self.MyTreeWidgetItem(None, -1)
                    for k, subshot_frame in enumerate(shot.subshots):
                        frame_position = subshot_frame / self.total_frames
                        subshot_item = self.MyTreeWidgetItem(
                            None, content_idx, frame_position)
                        subshot_item.setText(0, f'Subshot {k}')
                        self.item_list.append(subshot_item)
                        shot_item.addChild(subshot_item)
                        content_idx += 1
                    scene_item.addChild(shot_item)
            tree_items.append(scene_item)

        self.tree.insertTopLevelItems(0, tree_items)
        self.tree.expandAll()

        # VLC player frame
        if platform.system() == "Darwin":
            # Mac
            self.videoframe = QtWidgets.QMacCocoaViewContainer(0)
        else:
            # Windows
            self.videoframe = QtWidgets.QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        # Player controls
        self.hbuttonbox = QtWidgets.QHBoxLayout()

        self.playbtn = QtWidgets.QPushButton("Play")
        self.hbuttonbox.addWidget(self.playbtn)
        self.playbtn.clicked.connect(self.play)

        self.pausebtn = QtWidgets.QPushButton("Pause")
        self.hbuttonbox.addWidget(self.pausebtn)
        self.pausebtn.clicked.connect(self.pause)

        self.stopbtn = QtWidgets.QPushButton("Stop")
        self.hbuttonbox.addWidget(self.stopbtn)
        self.stopbtn.clicked.connect(self.stop)

        # Player with frame and controls
        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.vboxlayout.addLayout(self.hbuttonbox)

        # Combine video table and player
        self.hboxlayout = QtWidgets.QHBoxLayout()
        self.hboxlayout.addWidget(self.tree, 1)
        self.hboxlayout.addLayout(self.vboxlayout, 3)
        self.widget.setLayout(self.hboxlayout)

        # Timer to trigger the UI update
        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_ui)

    def play(self):
        if not self.mediaplayer.is_playing():
            if self.mediaplayer.play() == -1:
                self.open_file()
            else:
                self.is_paused = False
                self.timer.start()

    def pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.is_paused = True
            self.timer.stop()

    def stop(self):
        self.pause()
        self.mediaplayer.set_position(
            self.item_list[self.curr_idx].frame_position)

    def open_file(self, filename=None):
        if not filename:
            dialog = "Choose Media File"
            filename = QtWidgets.QFileDialog.getOpenFileName(
                self, dialog, os.path.expanduser('~'))

            if not filename:
                print("Error. No file chosen to be loaded.")
                return
            filename = filename[0]

        self.media = self.instance.media_new(filename)
        self.mediaplayer.set_media(self.media)
        self.media.parse()
        self.setWindowTitle(self.media.get_meta(0))

        # Connect VLC player to QFrame
        if platform.system() == "Linux":
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows":
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin":
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        self.item_list[self.curr_idx].setBackground(0, self.highlight)

        self.play()

    def update_ui(self):
        if not self.mediaplayer.is_playing():
            self.timer.stop()
            return

        curr_position = self.mediaplayer.get_position()

        if len(self.item_list) > self.curr_idx + 1 and curr_position >= self.item_list[self.curr_idx + 1].frame_position:
            self.item_list[self.curr_idx].setBackground(0, self.no_highlight)
            self.curr_idx += 1
            self.item_list[self.curr_idx].setBackground(0, self.highlight)

    def handleItemClick(self, item, col):
        self.item_list[self.curr_idx].setBackground(0, self.no_highlight)
        self.curr_idx = item.idx
        self.mediaplayer.set_position(item.frame_position)
        item.setBackground(0, self.highlight)
        item.setSelected(False)


def main():
    app = QtWidgets.QApplication(sys.argv)
    player = VideoPlayer()
    player.show()
    player.resize(1100, 700)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
