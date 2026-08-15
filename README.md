# LLM-Powered File System Assistant

A file assistant that connects core Python file system tools with an LLM (via OpenRouter / OpenAI API) to read, search, list, and summarize resumes across **PDF**, **DOCX**, and **TXT** formats using tool calling.

---

## 📁 Project Structure

```text
resume-file-assistant/
├── resumes/                      # Resume files folder (.pdf, .docx, .txt)
├── outputs/                      # Generated candidate summaries/reports
├── fs_tools.py                   # Part A: Core file system tools
├── llm_file_assistant.py         # Part B: CLI Assistant with tool calling
├── app.py                        # Web UI (Streamlit) for uploading & chatting
├── requirements.txt              # Project dependencies
├── .env.example                  # Environment variables template
├── .gitignore                    # Git ignore rules (protects API keys & cache)
└── README.md                     # Setup and usage guide
```

---

## 🎯 Deliverables & Features

### Part A: Core File System Tools (`fs_tools.py`)
- **`read_file(filepath: str) -> dict`**:
  - Reads **TXT**, **PDF** (`pypdf`), and **DOCX** (`python-docx`).
  - Returns structured dictionary with extracted content and metadata (`filename`, `extension`, `size_bytes`, `modified_time`).
  - Gracefully handles non-existent files or unsupported formats.
- **`list_files(directory: str, extension: str = None) -> list`**:
  - Lists all files in a directory.
  - Supports extension filtering (e.g., `.pdf`, `.docx`, `.txt`).
  - Returns metadata for each file.
- **`write_file(filepath: str, content: str) -> dict`**:
  - Writes text content to disk.
  - Automatically creates parent directories if they don't exist.
- **`search_in_file(filepath: str, keyword: str) -> dict`**:
  - Performs case-insensitive search across PDF, DOCX, and TXT files.
  - Returns line numbers, matched lines, and surrounding context.

### Part B: LLM Integration & UI
- **CLI Assistant (`llm_file_assistant.py`)**: Command-line interactive chat tool.
- **Web Interface (`app.py`)**: Modern Streamlit web application with:
  - Drag-and-drop file upload for `.pdf`, `.docx`, and `.txt` resumes.
  - Live tool-execution badges showing which tool was called in real-time.
  - Conversational chat interface.

---

## 🚀 Setup & Installation

### 1. Navigate to Project Directory
```bash
cd resume-file-assistant
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
Create or update `.env` in `resume-file-assistant/`:
```env
OPENROUTER_API_KEY=sk-or-v1-your_actual_key_here
OPENAI_BASE_URL=https://openrouter.ai/api/v1
MODEL_NAME=openai/gpt-4o-mini
```

---

## 🧪 How to Run

### 1. Run the Web UI (Streamlit)
```bash
streamlit run app.py
```
*Opens in your browser at `http://localhost:8501`.*

### 2. Run the CLI Assistant (Part B)
```bash
python llm_file_assistant.py
```

### 3. Test Core Tools Directly (Part A)
```bash
python fs_tools.py
```

---

## 💬 Example Queries for Demo Video (2-3 Minutes)

1. **List all resumes:**
   > *"Read all resumes in the resumes folder"*  
   > *(Calls `list_files`)*

2. **Filter by extension:**
   > *"List only the PDF resumes in the resumes folder"*  
   > *(Calls `list_files` with `extension='.pdf'`)*

3. **Keyword search across resumes:**
   > *"Find resumes mentioning Python experience"*  
   > *(Calls `list_files` + `search_in_file` / `read_file`)*

4. **Summarize a candidate:**
   > *"Read resume_john_doe.txt and give me a brief summary of his experience"*  
   > *(Calls `read_file`)*

5. **Generate and save summary file:**
   > *"Create a summary file for resume_john_doe.txt and save it in outputs/john_summary.txt"*  
   > *(Calls `read_file` then `write_file`)*
