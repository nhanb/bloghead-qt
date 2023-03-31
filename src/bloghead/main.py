import argparse
import sys
from pathlib import Path

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
    QListWidget,
    QMainWindow,
    QPlainTextEdit,
    QPushButton,
    QTextEdit,
    QToolBar,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from . import resources  # noqa
from . import djot_ipc
from .persistence import Blog

FILE_EXTENSION = "bloghead"


def autoupdate_preview(content: QPlainTextEdit, preview: QTextEdit):
    """
    Whenever djot content changes, update the preview panel accordingly.
    """
    djot = djot_ipc.Djot()

    def put_preview_task():
        input = content.toPlainText()
        output = djot.to_html(input)
        preview.setHtml(output)

    content.textChanged.connect(put_preview_task)


class MainWindow(QMainWindow):
    def __init__(self, *, quit_func, file_name: str):
        super().__init__()
        self.setWindowTitle("Bloghead")

        # Left block: article navigaion, files list
        left = QVBoxLayout()
        self.left = left

        left.articles = QGroupBox("Articles")
        left.articles.setLayout(QVBoxLayout())
        left.addWidget(left.articles)

        left.articles.tree = QTreeWidget()
        left.articles.tree.setHeaderHidden(True)
        left.articles.layout().addWidget(left.articles.tree)

        left.articles.buttons = QHBoxLayout()
        left.articles.layout().addLayout(left.articles.buttons)
        left.articles.buttons.addStretch(1)
        left.articles.buttons.addWidget(
            QPushButton("Add post...", icon=QIcon(":icons/document-new"))
        )
        left.articles.buttons.addWidget(
            QPushButton("Add page...", icon=QIcon(":icons/document-new"))
        )
        left.articles.buttons.addWidget(
            QPushButton("Delete...", enabled=False, icon=QIcon(":icons/edit-delete"))
        )

        def on_select_article(item):
            id = getattr(item, "article_id", None)
            if id is None:
                return

            # font = item.font(0)
            # font.setBold(True)
            # item.setFont(0, font)

            self.set_article(id)

        left.articles.tree.itemActivated.connect(on_select_article)

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
        right = QWidget()
        right.setLayout(QVBoxLayout())
        self.right = right

        right.form = QFormLayout()
        right.layout().addLayout(right.form)
        right.form.title = QLineEdit()
        right.form.addRow("Title:", right.form.title)
        right.form.slug = QLineEdit()
        right.form.addRow("Slug:", right.form.slug)

        right.editor = QGridLayout()
        right.layout().addLayout(right.editor)

        right.editor.buttons = QHBoxLayout()
        right.editor.addLayout(right.editor.buttons, 0, 0)
        right.editor.addWidget(QLabel("Preview:"), 0, 1)

        right.editor.content = QPlainTextEdit()
        right.editor.addWidget(right.editor.content, 1, 0)

        right.editor.preview = QTextEdit()
        right.editor.preview.setReadOnly(True)
        right.editor.preview.document().setDefaultStyleSheet(
            """
            code { background-color:#eee; padding:10px; font-family:"Ubuntu Mono";}
            """
        )
        right.editor.addWidget(right.editor.preview, 1, 1)

        autoupdate_preview(right.editor.content, right.editor.preview)

        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QHBoxLayout()
        widget.setLayout(layout)
        layout.addLayout(left)
        layout.addWidget(right, stretch=1)
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
        posts_data = blog.list_posts()
        pages_data = blog.list_pages()

        tree = self.left.articles.tree
        tree.clear()
        posts = QTreeWidgetItem(tree)
        posts.setIcon(0, QIcon(":icons/folder"))
        posts.setText(0, f"Posts: {len(posts_data)}")
        pages = QTreeWidgetItem(tree)
        pages.setIcon(0, QIcon(":icons/folder"))
        pages.setText(0, f"Pages: {len(pages_data)}")

        for id, title in posts_data:
            post = QTreeWidgetItem(posts)
            post.setText(0, title)
            post.article_id = id

        for id, title in pages_data:
            page = QTreeWidgetItem(pages)
            page.setText(0, title)
            page.article_id = id

        self.right.setEnabled(False)
        self.centralWidget().setEnabled(True)
        self.blog = blog

    def set_article(self, id: int):
        self.article = self.blog.get_article(id)

        self.right.form.title.setText(self.article.title)
        self.right.form.slug.setText(self.article.slug)
        self.right.editor.content.setPlainText(self.article.content)

        self.right.setEnabled(True)
        self.statusBar().showMessage(f"Selected article: {self.article.title}")


def start():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", nargs="?")
    filename = parser.parse_args().filename

    app = QApplication(sys.argv)
    window = MainWindow(quit_func=app.quit, file_name=filename)
    window.resize(800, 600)
    window.show()
    sys.exit(app.exec_())
