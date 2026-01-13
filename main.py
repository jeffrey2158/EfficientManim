"""
EfficientManim: The Definitive Node-Based Manim IDE
Production-Ready PySide6 Application
"""

import os
import sys
import json
import inspect
import subprocess
import tempfile
import zipfile
import logging
import re
import urllib.parse
from datetime import datetime

import manim
from manim import Mobject, ManimColor, Animation

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QSplitter, QTabWidget, QTextEdit, QListWidget, QStatusBar, QFormLayout, QLineEdit, QToolBar, QScrollArea,
    QGraphicsView, QGraphicsScene, QGraphicsItem, QGraphicsRectItem,
    QGraphicsPixmapItem, QGraphicsTextItem, QPushButton, QCheckBox,
    QDoubleSpinBox, QColorDialog, QFileDialog, QLabel, QGraphicsEllipseItem, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QThread, QTimer
from PySide6.QtGui import (
    QTextCursor, QBrush, QPen, QPixmap, QImage, QFont, QPainter, QColor
)

# Gemini SDK Setup
try:
    from google import genai
    from google.genai import types
except ImportError:
    genai = None

# --------------------------------------------------------------------------------
# LOGGING & SETTINGS
# --------------------------------------------------------------------------------

logger = logging.getLogger("EfficientManim")
logger.setLevel(logging.INFO)

class QTextEditLogger(logging.Handler):
    def __init__(self, widget):
        super().__init__()
        self.widget = widget
        self.widget.setReadOnly(True)

    def emit(self, record):
        msg = self.format(record)
        self.widget.append(msg)
        self.widget.moveCursor(QTextCursor.End)
        # Persistent log file
        log_dir = os.path.expanduser("~/.efficientmanim/logs")
        os.makedirs(log_dir, exist_ok=True)
        with open(os.path.join(log_dir, "session.log"), "a", encoding="utf-8") as f:
            f.write(msg + "\n")

def load_settings():
    path = os.path.expanduser("~/.efficientmanim/config/settings.json")
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except: pass
    return {
        "gemini_api_key": os.environ.get("GEMINI_API_KEY", ""),
        "fps": 30,
        "resolution": "1280x720",
        "quality": "ql",
        "theme": "dark"
    }

# --------------------------------------------------------------------------------
# MANIM DISCOVERY
# --------------------------------------------------------------------------------

def discover_manim_classes():
    mobjects = {}
    animations = {}
    for name in dir(manim):
        obj = getattr(manim, name)
        if inspect.isclass(obj):
            try:
                if issubclass(obj, Mobject) and obj is not Mobject:
                    mobjects[name] = obj
                elif issubclass(obj, Animation) and obj is not Animation:
                    animations[name] = obj
            except: pass
    return mobjects, animations

MOBJECT_CLASSES, ANIMATION_CLASSES = discover_manim_classes()

# --------------------------------------------------------------------------------
# RENDER WORKER
# --------------------------------------------------------------------------------

class RenderWorker(QThread):
    finished = Signal(bool, str, str) # Success, Logs, Path

    def __init__(self, code, scene_name="Output"):
        super().__init__()
        self.code = code
        self.scene_name = scene_name
        self.temp_dir = os.path.join(tempfile.gettempdir(), "efficient_manim_workspace")

    def run(self):
        os.makedirs(self.temp_dir, exist_ok=True)
        script_path = os.path.join(self.temp_dir, "scene_gen.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(self.code)

        # Command: manim -ql --format=png --save_last_frame --media_dir <tmp> <script> Output
        cmd = [
            "manim", "-ql", "--format=png", "--save_last_frame",
            "--media_dir", self.temp_dir,
            script_path, self.scene_name
        ]
        
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True)
            logs = proc.stdout + "\n" + proc.stderr
            
            # Find the PNG in media/images/scene_gen/Output...
            png_path = ""
            img_dir = os.path.join(self.temp_dir, "images", "scene_gen")
            if os.path.exists(img_dir):
                for f in os.listdir(img_dir):
                    if f.endswith(".png"):
                        png_path = os.path.join(img_dir, f)
                        break
            
            if png_path and os.path.exists(png_path):
                self.finished.emit(True, logs, png_path)
            else:
                self.finished.emit(False, logs, "")
        except Exception as e:
            self.finished.emit(False, str(e), "")

# --------------------------------------------------------------------------------
# GRAPHICS SYSTEM (NODES & LINKS)
# --------------------------------------------------------------------------------

class Port(QGraphicsEllipseItem):
    def __init__(self, parent, is_input=True):
        super().__init__(-6, -6, 12, 12, parent)
        self.is_input = is_input
        self.setBrush(QBrush(QColor("#4A90E2") if is_input else QColor("#F5A623")))
        self.setPen(QPen(Qt.black, 1))

class NodeItem(QGraphicsRectItem):
    def __init__(self, node_id, name, cls, etype="Mobject"):
        super().__init__(0, 0, 200, 180)
        self.node_id = node_id
        self.display_name = name
        self.internal_class = cls
        self.etype = etype
        self.properties = {}
        
        self.setBrush(QBrush(Qt.white))
        self.setPen(QPen(Qt.black, 2))
        self.setFlags(QGraphicsItem.ItemIsMovable | QGraphicsItem.ItemIsSelectable | QGraphicsItem.ItemSendsGeometryChanges)

        # Title
        self.title_text = QGraphicsTextItem(self.display_name, self)
        self.title_text.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.title_text.setDefaultTextColor(Qt.black)
        self.title_text.setPos(10, 5)

        # Preview Block (Viewport Clipping)
        self.preview_box = QGraphicsRectItem(10, 35, 180, 110, self)
        self.preview_box.setBrush(QBrush(Qt.black))
        self.preview_box.setFlag(QGraphicsItem.ItemClipsChildrenToShape, True)
        
        # Pixmap Parenting
        self.pix = QGraphicsPixmapItem(self.preview_box)
        self.pix.setZValue(1)

        # Ports
        self.input_port = Port(self, True)
        self.input_port.setPos(0, 90)
        self.output_port = Port(self, False)
        self.output_port.setPos(200, 90)

    def update_preview(self, path):
        if not path or not os.path.exists(path):
            self.pix.setPixmap(QPixmap())
            return
            
        img = QImage(path)
        if img.isNull(): return
        
        pixmap = QPixmap.fromImage(img).scaled(
            180, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation
        )
        self.pix.setPixmap(pixmap)
        
        # Center Math
        self.pix.setPos(
            (180 - pixmap.width()) / 2,
            (110 - pixmap.height()) / 2
        )

# --------------------------------------------------------------------------------
# MAIN IDE
# --------------------------------------------------------------------------------

class EfficientManim(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EfficientManim | Production Node IDE")
        self.resize(1600, 1000)
        
        self.nodes = {}
        self.counters = {}
        self.assets = []
        self.settings = load_settings()
        
        self.setup_ui()
        self.setup_logging()
        
        # Debounce timer for auto-rendering
        self.render_timer = QTimer()
        self.render_timer.setSingleShot(True)
        self.render_timer.timeout.connect(self.dispatch_render)

        logger.info("EfficientManim Started.")

    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Toolbar
        self.toolbar = QToolBar()
        self.addToolBar(self.toolbar)
        self.toolbar.addAction("✨ AI Gemini", self.prompt_ai)
        self.toolbar.addAction("🎬 Final Render", self.dispatch_render)
        self.toolbar.addSeparator()
        self.toolbar.addAction("💾 Save Project", self.save_project)
        self.toolbar.addAction("📂 Open Project", self.load_project)

        # Main Splitter
        self.main_splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(self.main_splitter)

        # LEFT: Element Browser
        self.left_panel = QWidget()
        left_layout = QVBoxLayout(self.left_panel)
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search Mobjects...")
        self.search_bar.textChanged.connect(self.filter_elements)
        self.el_list = QListWidget()
        for k in sorted(MOBJECT_CLASSES):
            self.el_list.addItem(k)
        self.el_list.itemDoubleClicked.connect(lambda i: self.create_node(i.text(), "Mobject"))
        left_layout.addWidget(QLabel("<b>Library</b>"))
        left_layout.addWidget(self.search_bar)
        left_layout.addWidget(self.el_list)

        # CENTER: Graphics Scene
        self.scene = QGraphicsScene()
        self.scene.selectionChanged.connect(self.sync_inspector)
        self.view = QGraphicsView(self.scene)
        self.view.setRenderHint(QPainter.Antialiasing)
        self.view.setDragMode(QGraphicsView.RubberBandDrag)

        # RIGHT: Inspector & Panels
        self.right_tabs = QTabWidget()
        
        # Persistent Inspector
        self.inspector_area = QScrollArea()
        self.inspector_area.setWidgetResizable(True)
        self.ins_container = QWidget()
        self.ins_layout = QFormLayout(self.ins_container)
        self.ins_preview = QLabel() # Persistent widget
        self.ins_preview.setFixedSize(200, 120)
        self.ins_preview.setStyleSheet("background: black; border: 1px solid #333;")
        self.ins_preview.setAlignment(Qt.AlignCenter)
        self.inspector_area.setWidget(self.ins_container)

        self.code_view = QTextEdit()
        self.code_view.setReadOnly(True)
        self.code_view.setFont(QFont("Consolas", 10))
        
        self.log_view = QTextEdit()

        self.right_tabs.addTab(self.inspector_area, "Inspector")
        self.right_tabs.addTab(self.code_view, "Python Code")
        self.right_tabs.addTab(self.log_view, "Logs")

        self.main_splitter.addWidget(self.left_panel)
        self.main_splitter.addWidget(self.view)
        self.main_splitter.addWidget(self.right_tabs)
        self.main_splitter.setStretchFactor(1, 2)

        self.setStatusBar(QStatusBar())

    def setup_logging(self):
        handler = QTextEditLogger(self.log_view)
        handler.setFormatter(
            logging.Formatter(
                fmt="%(asctime)s | %(message)s",
                datefmt="%H:%M:%S"
            )
        )
        logger.addHandler(handler)

    # --- LOGIC ---

    def filter_elements(self, text):
        for i in range(self.el_list.count()):
            item = self.el_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())

    def create_node(self, cls_name, etype):
        idx = self.counters.get(cls_name, 0) + 1
        self.counters[cls_name] = idx
        display_name = f"{cls_name}_{idx}"
        nid = f"{cls_name}_{datetime.now().timestamp()}"
        
        node = NodeItem(nid, display_name, cls_name, etype)
        self.scene.addItem(node)
        self.nodes[nid] = node

        # Property Reflection
        cls_obj = MOBJECT_CLASSES.get(cls_name) or ANIMATION_CLASSES.get(cls_name)
        sig = inspect.signature(cls_obj.__init__)
        for k, p in sig.parameters.items():
            if k != "self":
                # identity check fix
                node.properties[k] = p.default if p.default is not inspect._empty else None
        
        self.sync_state()

    def sync_inspector(self):
        # 🧨 Fix: Do not delete self.ins_preview
        while self.ins_layout.count() > 0:
            item = self.ins_layout.takeAt(0)
            if item.widget() and item.widget() != self.ins_preview:
                item.widget().deleteLater()

        sel = self.scene.selectedItems()
        if not sel: return
        node = sel[0]
        if not isinstance(node, NodeItem): return

        self.ins_layout.addRow(self.ins_preview) # Re-add persistent widget
        self.ins_layout.addRow(QLabel(f"<b>{node.display_name}</b>"), QLabel(""))

        for k, v in node.properties.items():
            # 🧨 Crash Fixes for ManimColor & empty checks
            if v is None and k not in ["color", "fill_color", "stroke_color"]: continue
            
            if isinstance(v, ManimColor) or k.lower().endswith("color"):
                btn = QPushButton("Pick Color")
                btn.clicked.connect(lambda _, key=k: self.open_color_picker(node, key))
                self.ins_layout.addRow(k, btn)
            elif isinstance(v, bool):
                w = QCheckBox()
                w.setChecked(v)
                w.toggled.connect(lambda val, key=k: self.update_prop(node, key, val))
                self.ins_layout.addRow(k, w)
            elif isinstance(v, (int, float)):
                w = QDoubleSpinBox()
                w.setRange(-10000, 10000)
                w.setValue(float(v))
                w.valueChanged.connect(lambda val, key=k: self.update_prop(node, key, val))
                self.ins_layout.addRow(k, w)
            else:
                w = QLineEdit("" if v is None else str(v))
                w.textChanged.connect(lambda val, key=k: self.update_prop(node, key, val))
                self.ins_layout.addRow(k, w)

    def open_color_picker(self, node, key):
        color = QColorDialog.getColor()
        if color.isValid():
            node.properties[key] = ManimColor(color.name())
            self.sync_state()

    def update_prop(self, node, key, val):
        node.properties[key] = val
        self.sync_state()

    def sync_state(self):
        code = self.generate_code()
        self.code_view.setPlainText(code)
        self.render_timer.start(300)

    def generate_code(self):
        lines = ["from manim import *", "", "class Output(Scene):", "    def construct(self):"]
        if not self.nodes: lines.append("        pass")
        for n in self.nodes.values():
            args = []
            for k, v in n.properties.items():
                if v is None: continue
                if isinstance(v, str) and not v.strip(): continue
                # 🧨 ManimColor handling
                if hasattr(v, "to_hex"):
                    args.append(f"{k}=ManimColor('{v.to_hex()}')")
                else:
                    args.append(f"{k}={repr(v)}")
            lines.append(f"        {n.display_name} = {n.internal_class}({', '.join(args)})")
            lines.append(f"        self.add({n.display_name})")
        return "\n".join(lines)

    def dispatch_render(self):
        self.worker = RenderWorker(self.code_view.toPlainText())
        self.worker.finished.connect(self.on_render_finished)
        self.worker.start()

    def on_render_finished(self, success, logs, path):
        logger.info("Render finished.")
        self.log_view.append(logs)
        if success:
            img = QImage(path)
            pix = QPixmap.fromImage(img).scaled(
                180, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
            # Update Node Icons
            for n in self.nodes.values():
                n.update_preview(path)
            # Update Inspector Preview
            self.ins_preview.setPixmap(pix)

    # --- PROJECT SYSTEM ---

    def save_project(self):
        path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "EfficientManim (*.efp)")
        if not path: return
        data = {
            "nodes": {
                nid: {
                    "class": n.internal_class,
                    "name": n.display_name,
                    "props": {k: (v.to_hex() if hasattr(v, "to_hex") else v) for k, v in n.properties.items()},
                    "pos": [n.pos().x(), n.pos().y()]
                } for nid, n in self.nodes.items()
            },
            "counters": self.name_counters
        }
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("project.json", json.dumps(data, indent=4))
        logger.info(f"Project saved: {path}")

    def load_project(self):
        path, _ = QFileDialog.getOpenFileName(self, "Open Project", "", "EfficientManim (*.efp)")
        if not path: return
        self.scene.clear()
        self.nodes.clear()
        with zipfile.ZipFile(path) as z:
            data = json.loads(z.read("project.json"))
        self.counters = data["counters"]
        for nid, d in data["nodes"].items():
            node = NodeItem(nid, d["name"], d["class"])
            # Restore props with ManimColor check
            for k, v in d["props"].items():
                if isinstance(v, str) and v.startswith("#"):
                    node.properties[k] = ManimColor(v)
                else:
                    node.properties[k] = v
            node.setPos(*d["pos"])
            self.scene.addItem(node)
            self.nodes[nid] = node
        self.sync_state()

    # --- AI INTEGRATION ---
    def prompt_ai(self):
        if not genai:
            QMessageBox.critical(self, "Error", "google-genai not installed.")
            return

        from PySide6.QtWidgets import QInputDialog
        text, ok = QInputDialog.getMultiLineText(
            self, "Gemini AI Assistant", "Describe changes to the scene:"
        )
        if ok and text:
            self.run_ai_query(text)


    def run_ai_query(self, prompt):
        api_key = self.settings.get("gemini_api_key")
        if not api_key:
            QMessageBox.warning(self, "Settings", "Set Gemini API Key in settings.")
            return

        logger.info("Querying Gemini...")
        try:
            client = genai.Client(api_key=api_key)

            ctx = f"Context: Nodes={list(self.nodes.keys())}\nCode:\n{self.code_view.toPlainText()}"
            full_prompt = f"{ctx}\n\nTask: {prompt}\nRespond ONLY with Python code between ```python ... ``` blocks."

            model = "gemini-3-flash-preview"

            contents = [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(full_prompt)]
                )
            ]

            config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_level="HIGH")
            )

            response_text = ""
            for chunk in client.models.generate_content_stream(
                model=model,
                contents=contents,
                config=config
            ):
                if chunk.text:
                    response_text += chunk.text

            # Extract only Python code between ```python ... ```
            match = re.search(r"```python(.*?)```", response_text, re.DOTALL)
            if match:
                new_code = match.group(1).strip()
                apply = QMessageBox.question(
                    self, "Apply AI Suggestion?", "Apply the AI-generated code?\n\n" + new_code,
                    QMessageBox.Yes | QMessageBox.No
                )
                if apply == QMessageBox.Yes:
                    self.code_view.setPlainText(new_code)
                    self.dispatch_render()
            else:
                logger.warning("AI returned no code.")

        except Exception as e:
            logger.error(f"AI Error: {e}")

    def report_bug(self):
        logs = self.log_view.toPlainText()[-2000:]
        body = f"Bug Report\nLogs:\n{logs}"
        url = f"https://github.com/pro-grammer-SD/MagicalManim/issues/new?title=Bug+Report&body={urllib.parse.quote(body)}"
        import webbrowser
        webbrowser.open(url)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    # Global palette for classic look
    palette = app.palette()
    app.setPalette(palette)
    
    win = EfficientManim()
    win.show()
    sys.exit(app.exec())
