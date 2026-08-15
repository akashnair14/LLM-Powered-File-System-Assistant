import os
from datetime import datetime
from pypdf import PdfReader
from docx import Document


def read_file(filepath: str) -> dict:
    """Read content and metadata from a text, PDF, or DOCX file."""
    # Normalize path and check if file exists
    clean_path = filepath.strip().replace("\\", "/")
    
    # Auto-resolve relative paths if missing 'resumes/' prefix
    if not os.path.exists(clean_path) and not os.path.isabs(clean_path):
        candidate_path = os.path.join("resumes", clean_path)
        if os.path.exists(candidate_path):
            clean_path = candidate_path

    if not os.path.exists(clean_path) or not os.path.isfile(clean_path):
        return {"status": "error", "message": f"File not found: {filepath}"}

    ext = os.path.splitext(clean_path)[1].lower()
    stat = os.stat(clean_path)

    metadata = {
        "filename": os.path.basename(clean_path),
        "extension": ext,
        "size_bytes": stat.st_size,
        "modified_time": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
    }

    try:
        if ext == ".txt":
            with open(clean_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

        elif ext == ".pdf":
            reader = PdfReader(clean_path)
            content = "\n".join([page.extract_text() or "" for page in reader.pages])

        elif ext == ".docx":
            doc = Document(clean_path)
            content = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

        else:
            return {"status": "error", "message": f"Unsupported format: {ext}"}

        return {
            "status": "success",
            "filepath": clean_path,
            "metadata": metadata,
            "content": content
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


def list_files(directory: str = "resumes", extension: str = None) -> list:
    """List files in a directory, optionally filtered by extension."""
    clean_dir = (directory or "resumes").strip().replace("\\", "/")
    if not os.path.exists(clean_dir) or not os.path.isdir(clean_dir):
        return []

    if extension and not extension.startswith("."):
        extension = f".{extension}"

    results = []
    for filename in os.listdir(clean_dir):
        full_path = os.path.join(clean_dir, filename)

        if os.path.isfile(full_path):
            if extension and not filename.lower().endswith(extension.lower()):
                continue

            stat = os.stat(full_path)
            results.append({
                "name": filename,
                "filepath": full_path.replace("\\", "/"),
                "size_bytes": stat.st_size,
                "modified_date": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
            })

    return results


def write_file(filepath: str, content: str) -> dict:
    """Write text to a file, creating parent directories if needed."""
    try:
        clean_path = filepath.strip().replace("\\", "/")
        parent_dir = os.path.dirname(clean_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        with open(clean_path, "w", encoding="utf-8") as f:
            f.write(content)

        return {"status": "success", "filepath": clean_path, "message": f"Saved to {clean_path}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def search_in_file(filepath: str, keyword: str) -> dict:
    """Case-insensitive keyword search in a file, returning matching lines and context."""
    file_data = read_file(filepath)
    if file_data["status"] != "success":
        return {"status": "error", "message": file_data["message"]}

    lines = file_data["content"].splitlines()
    matches = []
    keyword_lower = keyword.strip().lower()

    for idx, line in enumerate(lines):
        if keyword_lower in line.lower():
            start = max(0, idx - 1)
            end = min(len(lines), idx + 2)
            context = "\n".join(lines[start:end])

            matches.append({
                "line_number": idx + 1,
                "matched_line": line.strip(),
                "context": context
            })

    return {
        "status": "success",
        "filepath": file_data["filepath"],
        "keyword": keyword,
        "match_count": len(matches),
        "matches": matches
    }


if __name__ == "__main__":
    print("Testing fs_tools.py...")
    print("1. Write file:", write_file("test.txt", "John Doe\nPython developer\n5 years experience"))
    print("2. List files:", list_files("resumes"))
    print("3. Read file:", read_file("test.txt")["metadata"])
    print("4. Search in file:", search_in_file("test.txt", "python"))
    
    if os.path.exists("test.txt"):
        os.remove("test.txt")
