import argparse
import sys
from pathlib import Path

from PySide2.QtCore import QAbstractListModel, QModelIndex, Qt
from PySide2.QtGui import QIcon, QKeySequence
from PySide2.QtWidgets import (
    QAction,
    QApplication,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListView,
    QListWidget,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QTabWidget,
    QTextBrowser,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from . import resources  # noqa
from .persistence import Blog

FILE_EXTENSION = "bloghead"


class MainWindow(QMainWindow):
    def __init__(self, *, quit_func, file_name: str):
        super().__init__()
        self.setWindowTitle("Bloghead")

        # Left block: article navigaion, files list
        left = QVBoxLayout()
        self.left = left

        left.articles = QTabWidget()
        left.addWidget(left.articles)

        left.articles.posts = QWidget()
        left.articles.addTab(left.articles.posts, "Posts")
        left.articles.posts.setLayout(QVBoxLayout())
        left.articles.posts.list = QListView()
        left.articles.posts.layout().addWidget(left.articles.posts.list)
        left.articles.posts.buttons = QHBoxLayout()
        left.articles.posts.layout().addLayout(left.articles.posts.buttons)
        left.articles.posts.buttons.addStretch(1)
        left.articles.posts.buttons.addWidget(
            QPushButton("Add post...", icon=QIcon(":icons/document-new"))
        )
        left.articles.posts.buttons.addWidget(
            QPushButton("Delete...", enabled=False, icon=QIcon(":icons/edit-delete"))
        )

        left.articles.pages = QWidget()
        left.articles.addTab(left.articles.pages, "Pages")
        left.articles.pages.setLayout(QVBoxLayout())
        left.articles.pages.list = QListView()
        left.articles.pages.layout().addWidget(left.articles.pages.list)
        left.articles.pages.buttons = QHBoxLayout()
        left.articles.pages.layout().addLayout(left.articles.pages.buttons)
        left.articles.pages.buttons.addStretch(1)
        left.articles.pages.buttons.addWidget(
            QPushButton("Add page...", icon=QIcon(":icons/document-new"))
        )
        left.articles.pages.buttons.addWidget(
            QPushButton("Delete...", enabled=False, icon=QIcon(":icons/edit-delete"))
        )

        left.files = QGroupBox("Article's uploaded files")
        left.files.setLayout(QVBoxLayout())
        left.addWidget(left.files)

        left.files.list = QListWidget()
        left.files.layout().addWidget(left.files.list)

        left.files.buttons = QHBoxLayout()
        left.files.layout().addLayout(left.files.buttons)
        left.files.buttons.addStretch(1)
        left.files.buttons.addWidget(
            QPushButton("Upload...", icon=QIcon(":icons/upload-media"))
        )
        left.files.buttons.addWidget(
            QPushButton("Rename...", icon=QIcon(":icons/document-edit"))
        )
        left.files.buttons.addWidget(
            QPushButton("Delete...", enabled=False, icon=QIcon(":icons/edit-delete"))
        )

        # Right block: article editor
        right = QVBoxLayout()

        right.form = QFormLayout()
        right.addLayout(right.form)
        right.form.addRow("Title:", QLineEdit())
        right.form.addRow("Slug:", QLineEdit())

        right.editor = QGridLayout()
        right.addLayout(right.editor)

        right.editor.buttons = QHBoxLayout()
        right.editor.addLayout(right.editor.buttons, 0, 0)
        right.editor.addWidget(QLabel("Preview:"), 0, 1)
        right.editor.addWidget(QPlainTextEdit(), 1, 0)
        right.editor.addWidget(QTextBrowser(), 1, 1)

        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QHBoxLayout()
        widget.setLayout(layout)
        layout.addLayout(left)
        layout.addLayout(right, stretch=1)
        widget.setDisabled(True)

        # "Table stakes" actions e.g. New, Open, Save, Quit:

        new_action = QAction("&New", self, icon=QIcon(":/icons/document-new"))
        new_action.setShortcut(QKeySequence.New)
        new_action.triggered.connect(self.action_new)

        open_action = QAction("&Open", self, icon=QIcon(":/icons/document-open"))
        open_action.setShortcut(QKeySequence.Open)
        open_action.triggered.connect(self.action_open)

        save_action = QAction(
            "&Save",
            self,
            icon=QIcon(":/icons/document-save"),
            enabled=False,
        )
        save_action.setShortcut(QKeySequence.Save)

        save_as_action = QAction(
            "Save &As...",
            self,
            icon=QIcon(":/icons/document-save-as"),
            enabled=False,
        )
        save_as_action.setShortcut(QKeySequence.SaveAs)

        quit_action = QAction("&Quit", self, icon=QIcon(":/icons/application-exit"))
        quit_action.triggered.connect(quit_func)
        quit_action.setShortcut(QKeySequence.Quit)

        toolbar = QToolBar("Main toolbar", movable=False)
        toolbar.addAction(new_action)
        toolbar.addAction(open_action)
        toolbar.addSeparator()
        toolbar.addAction(save_action)
        toolbar.addAction(save_as_action)
        toolbar.addSeparator()
        toolbar.addAction(quit_action)
        self.addToolBar(toolbar)

        menu = self.menuBar()

        file_menu = menu.addMenu("&File")
        file_menu.addAction(new_action)
        file_menu.addAction(open_action)
        file_menu.addSeparator()
        file_menu.addAction(save_action)
        file_menu.addAction(save_as_action)
        file_menu.addSeparator()
        file_menu.addAction(quit_action)

        publish_menu = menu.addMenu("&Publish")
        publish_menu.addAction("&Manage...")
        publish_menu.setDisabled(True)

        export_menu = menu.addMenu("E&xport")
        export_menu.addAction("&Manage...")
        export_menu.setDisabled(True)

        self.statusBar().showMessage("Tip: Open or create a New blog to start")

        if file_name and Path(file_name).exists():
            self.set_blog(Path(file_name))
            self.statusBar().showMessage(f"Opened {file_name}")

    def action_new(self):
        path, _ = QFileDialog.getSaveFileName(
            self,
            caption="Create new blog",
            filter=f"Bloghead files (*.{FILE_EXTENSION})",
            dir=".",
        )
        if not path:
            self.statusBar().showMessage("Aborted new blog creation")
            return

        ext = f".{FILE_EXTENSION}"
        if not path.endswith(ext):
            path += ext

        path = Path(path)
        if path.exists():
            # QFileDialog should have already asked user to confirm to overwrite.
            path.unlink()

        self.set_blog(path)
        self.blog.init_schema()
        self.statusBar().showMessage(f"Created {path}")

    def action_open(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            caption="Open blog",
            filter=f"Bloghead files (*.{FILE_EXTENSION})",
            dir=".",
        )
        if not path:
            self.statusBar().showMessage("Aborted open blog")
            return

        self.set_blog(Path(path))
        self.statusBar().showMessage(f"Opened {path}")

    def set_blog(self, path: Path):
        blog = Blog(path)

        self.left.articles.pages.list.setModel(PagesModel(blog))
        self.left.articles.posts.list.setModel(PostsModel(blog))

        self.centralWidget().setEnabled(True)
        self.blog = blog


class PostsModel(QAbstractListModel):
    def __init__(self, blog: Blog):
        super().__init__()
        self.blog = blog

    def rowCount(self, parent: QModelIndex):
        return self.blog.count_posts()

    def data(self, index: QModelIndex, role):
        if role != Qt.DisplayRole:
            return

        _, title = self.blog.get_post_title(index.row())
        return title


class PagesModel(QAbstractListModel):
    def __init__(self, blog: Blog):
        super().__init__()
        self.blog = blog

    def rowCount(self, parent: QModelIndex):
        return self.blog.count_pages()

    def data(self, index: QModelIndex, role):
        if role != Qt.DisplayRole:
            return

        _, title = self.blog.get_page_title(index.row())
        return title


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="?")
    filename = parser.parse_args().filename

    app = QApplication(sys.argv)
    window = MainWindow(quit_func=app.quit, file_name=filename)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
