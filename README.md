# HashCraft Tool


A lightweight, cross-platform CLI tool built in Python for cryptographic file integrity verification, checksum generation, directory hashing, and multi-format result logging.

---

## 🌟 Key Features

- **🛡️ Cryptographic Hash Support:** Compute checksums using **MD5**, **SHA-1**, **SHA-256**, and **SHA-512**.
- **🌐 True Cross-Platform:** Native support for **Windows**, **macOS**, and **Linux** with dynamic user path & OneDrive resolution.
- **📂 Flexible Input Modes:**
  - Single File Hashing
  - Multiple Selected Files
  - Recursive Directory Scanning (Folder Hashing)
- **⚡ Memory Efficient:** Uses stream chunking (`4096-byte` buffer) to hash large files seamlessly without RAM overload.
- **📊 Multi-Format Export Engine:** Save generated hashes to 10+ structured formats:
  - `.txt`, `.log`, `.json`, `.csv`, `.md`, `.yaml`, `.xml`, `.ini`, `.properties`, `.conf`
- **🔄 Interactive Lifecycle Management:** Clear 5-stage progress tracking with built-in history auto-clearing for secure operations.
- **📦 Zero External Dependencies:** Built entirely using Python's standard libraries and custom lightweight modules.

---

## 🖥️ Cross-Platform Compatibility

The project automatically detects the underlying operating system and normalizes path formats accordingly:

| Operating System | Path Resolution | Features & Integration |
| :--- | :--- | :--- |
| **Windows 10 / 11** | Full Support | Detects system `Documents`, active **OneDrive** paths, and standard drive letters. |
| **macOS** | Full Support | Resolves `~/Documents`, iCloud Drive paths, and POSIX syntax natively. |
| **Linux / Unix** | Full Support | Resolves home directories (`~`), mount points, and standard Linux file structures. |

---

## 🛠️ Project Structure

```text
.
├── main.py            # Main application entry point & interactive execution loop
├── hasher.py          # Core Hasher class & stage lifecycle controller
├── verification.py    # Input validators, path resolvers, and multi-format exporters
└── ui.py              # Terminal UI utilities, progress bars, and screen management
```
---

🚀 Quick Start
Prerequisites
Python 3.8 or higher (No third-party packages required).

Execution
Simply run the main script in your terminal or command prompt:

Bash
python main.py

---

🔄 How It Works (Execution Lifecycle)
The suite guides users through a structured 5-stage workflow:

*Stage 1*: Input Setup — Select the target hash algorithm (e.g., SHA-256) and provide a file path, multiple files, or a folder.

*Stage 2*: Checksum Calculation — The engine reads files in binary chunks with real-time visual progress indicators.

*Stage 3*: Result Display — Hashes are displayed with customizable path formatting (Full Path, Short Path, or Filename only).

*Stage 4*: File Export (Optional) — Results are serialized and saved to your chosen format and path.

*Stage 5*: Clean Exit — Memory and execution history are cleared safely before returning or exiting.

---

📄 Output Formats Overview
When saving calculation logs, the built-in export system formats output automatically based on your selected file extension:

 •  JSON (.json): Formatted key-value dictionary structure.

 •  CSV (.csv): Standard comma-separated layout suitable for Excel/data tools.

 •  Markdown (.md): Formatted Markdown table ready for documentation.

 •  YAML (.yaml): Clean key-value structural data.

 •  INI / Config (.ini, .conf): Configuration section layout.

---

📜 License

    ◌ Distributed under the MIT License. See LICENSE for details.
