# EfficientManim

**The Ultimate Node-Based Manim IDE**  
*Create mathematical animations visually with the power of Python, AI, and Type Safety.*

---

## 🚀 Core Features

### 🎬 Node-Based Workflow
*   **Visual Editor:** Drag and drop Mobjects and Animations. Wire them together to create logic flows.
*   **Smart Connections:** The system prevents invalid connections (e.g., connecting two Mobjects directly without an animation).
*   **Live Preview:** See static previews of individual nodes as you tweak parameters.

### 📦 Portable Project Format (.efp)
*   **Bundled Assets:** Images, sounds, and videos are automatically copied and zipped into the project file.
*   **Cross-Platform:** Projects created on Windows work on Linux/Mac. The system automatically handles path conversions (e.g., converting backslashes to forward slashes for Manim).
*   **Self-Contained:** Share a single `.efp` file without worrying about broken file paths.

### 🛡️ Robust Type Safety System
*   **Smart Parsing:** Automatically distinguishes between numeric values, colors, vectors, and asset file paths.
*   **Crash Prevention:** Prevents "ufunc" errors by validating inputs before they reach the Manim renderer.
*   **ImageMobject Support:** Correctly handles UUIDs vs. Filenames to ensure images render without numeric conversion errors.
*   **Color Normalization:** Accepts Hex, RGB tuples, or Manim constants (e.g., `RED`, `BLUE`) and standardizes them.

### 🤖 Gemini AI Integration
*   **Text-to-Animation:** Describe an animation in plain English, and the AI generates the node graph.
*   **Node Extraction:** The AI code is parsed into editable nodes (Mobjects and Animations) rather than just a black box of code.
*   **Merger Logic:** AI-generated nodes are fully integrated into the existing scene graph with preserved parameters.

### 🎬 Professional Video Rendering
*   **Full Scene Export:** Render your complete node graph to MP4/WebM.
*   **Custom Settings:** Control Resolution (up to 4K), Framerate (15-60 FPS), and Render Quality (Low to Ultra).
*   **Background Processing:** Rendering happens in a separate thread, keeping the UI responsive.

---

## 🛠️ The Interface

### 1. The Graph Editor
The central canvas where you arrange your scene.
*   **Mobjects (Blue Headers):** Objects like Circles, Text, Images.
*   **Animations (Purple Headers):** Actions like FadeIn, Transform, Rotate.
*   **Connections:** Define the flow of the animation.

### 2. The Enhanced Inspector
A powerful 3-column property editor located on the right.
*   **Value Input:** Context-aware widgets (Color pickers for colors, File selectors for assets, Spinners for numbers).
*   **Enabled Checkbox:** Toggle parameters on/off. Unchecked parameters are excluded from the generated Python code.
*   **Escape Checkbox:** When checked, removes quotes from string values (useful for passing variable names or raw Python objects).

### 3. Asset Manager
*   **Drag & Drop:** Import images and sounds easily.
*   **Auto-Link:** Assets are referenced by ID, ensuring links survive file renaming or project movement.

---

## ⚙️ Example Workflow

1.  **Import Assets:** Go to the Assets tab and import a `.png` file.
2.  **Add Nodes:**
    *   Add an `ImageMobject` node.
    *   In the Inspector, select your imported image from the dropdown.
    *   Add a `FadeIn` animation node.
3.  **Connect:** Wire the `ImageMobject` output to the `FadeIn` input.
4.  **Preview:** Select the `ImageMobject` to see a static preview in the bottom-left panel.
5.  **Render:** Go to the Video tab, select 1080p/60FPS, and click **Render Full Scene**.

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|:---|:---|
| **Delete** | Delete selected nodes/wires |
| **Ctrl + Z** | Undo last action |
| **Ctrl + Y** | Redo last action |
| **Ctrl + S** | Save project (.efp) |
| **Ctrl + O** | Open project |
| **Ctrl + 0** | Fit scene to view |
| **Ctrl + Alt + Del** | Clear entire scene |

---

## 🐛 Error Handling & Logs

EfficientManim includes a comprehensive logging system (visible in the "Logs" tab):
*   **MANIM logs:** Capture render errors directly from the Manim CLI.
*   **AI logs:** Track generation status and merging issues.
*   **System logs:** Monitor file I/O and asset loading.
*   **Session Log:** A `session.log` file is maintained in your User Data folder for debugging crashes.

---

## 🚀 Getting Started

### Prerequisites
*   Python 3.10+
*   [Manim Community](https://www.manim.community/) (`pip install manim`)
*   [FFmpeg](https://ffmpeg.org/) (Required by Manim)

### Installation
```bash
# 1. Install Dependencies
pip install PySide6 manim google-genai

# 2. Run the Application
python main.py
```

## 📸 Screenshots

![Image 1](gallery/1.png "Starting up a basic project from scratch...")
![Image 2](gallery/2.png "Inserting elements and search for new animations...")
![Image 3](gallery/3.png "Getting better with cool animations, now customizing...")
![Image 4](gallery/4.png "Render working, a beautiful animation is generated...")

---

Made with lots of ❤️💚💙 by Soumalya a.k.a. @pro-grammer-SD.
