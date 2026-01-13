# 🎬 EfficientManim

> **Motion Graphics at the Speed of Thought.**  
> *The ultimate production-grade, node-based IDE for Manim Community Edition.*

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Manim CE](https://img.shields.io/badge/manim-community-brightgreen.svg)](https://www.manim.community/)
[![Gemini AI](https://img.shields.io/badge/AI-Gemini--3--Flash--Preview-orange.svg)](https://deepmind.google/technologies/gemini/)
[![PySide6](https://img.shields.io/badge/GUI-PySide6-blueviolet.svg)](https://doc.qt.io/qtforpython/)

---

## 🧠 What is EfficientManim?

**EfficientManim** transforms the way you create math animations. Instead of wrestling with code desync and slow render loops, EfficientManim provides a **ComfyUI-style node graph** where every Mobject is a node, and every animation is a connection.

Think **Blender Geometry Nodes** meets **After Effects**, powered by the raw math precision of **Manim**.

---

## ✨ God-Level Features

### 🧩 Node-Based Workflow
*   **Visual Logic:** Drag-and-drop Mobjects (Circles, Squares, Text) into the workspace.
*   **Automatic Numbering:** Create `Circle_1`, `Circle_2` instantly with incremental logic.
*   **Live Node Previews:** Every node contains a **Live PNG Preview** rendered directly by Manim. No more "rendering in your head."

### 💎 Gemini AI Integration
*   **Flashy Intelligence:** Uses `gemini-3-flash-preview` to generate complex scenes.
*   **Regex Extraction:** Automatically pulls Python code from AI responses.
*   **Safe Merging:** Preview AI suggestions and accept/reject before they touch your project.

### 🔍 Signature-Driven Inspector
*   **Dynamic Reflection:** Uses `inspect.signature` to read Manim class constructors on the fly.
*   **Type-Safe Widgets:** Automatically generates Color Pickers, Sliders, Checkboxes, and ComboBoxes based on Python types.
*   **Identity Precision:** Zero-crash property management—no `ManimColor` comparison errors.

### 🎞️ Unified Render Pipeline
*   **Source of Truth:** All previews (Nodes, Inspector, Global) are driven by real Manim CLI PNG outputs.
*   **Fast Preview:** Uses `-ql --format=png --save_last_frame` for sub-500ms feedback loops.
*   **No Glitches:** Buffered rendering prevents the "black box" jitter common in Qt/Manim integrations.

### 💾 Pro Project System (.efp)
*   **Zip-Based Persistence:** Save your entire workspace, node positions, properties, and assets into a single `.efp` file.
*   **Asset Management:** Drag and drop PNGs, MP3s, and MP4s directly into your inspector.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have [Manim](https://docs.manim.community/en/stable/installation.html) installed on your system.

### 2. Install Dependencies
```bash
pip install PySide6 manim google-genai
```

### 3. Setup Gemini API (Optional for AI)
```bash
# Windows
set GEMINI_API_KEY=your_key_here
# Linux/Mac
export GEMINI_API_KEY=your_key_here
```

### 4. Run the Engine
```bash
python main.py
```

---

## ⌨️ Keybindings

| Key | Action |
| :--- | :--- |
| **Space** | Trigger Preview Render |
| **Delete** | Remove selected Node |
| **Ctrl + S** | Save Project (.efp) |
| **Ctrl + D** | Duplicate Node |
| **Arrow Keys** | Nudge Node position |

---

## 🛠️ Tech Stack

*   **GUI:** [PySide6](https://doc.qt.io/qtforpython/) (Qt for Python)
*   **Animation Engine:** [Manim Community Edition](https://www.manim.community/)
*   **AI:** [Google GenAI SDK](https://github.com/google/generative-ai-python)
*   **Reflection:** Python `inspect` module
*   **Data:** JSON & Zip-based storage

---

## 🐞 Bug Reporting

Found a glitch? Want to report a "black preview" (though we fixed that)?  
Hit the **Report Issue** button in the app to auto-generate a bug report at:  
[EfficientManim Issues](https://github.com/pro-grammer-SD/MagicalManim/issues/new)

---

## 📜 License

EfficientManim is production-ready and open-source. Build something beautiful.

**"Stop coding animations. Start building them."** 🚀🔥
