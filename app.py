import json
import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

import fs_tools

# Page Configuration
st.set_page_config(
    page_title="Resume File Assistant",
    page_icon="📄",
    layout="wide"
)

# Load environment variables
load_dotenv()

# Project Directories
RESUMES_DIR = "resumes"
OUTPUTS_DIR = "outputs"
os.makedirs(RESUMES_DIR, exist_ok=True)
os.makedirs(OUTPUTS_DIR, exist_ok=True)

# Custom Styling
st.markdown("""
<style>
    .stChatMessage {
        border-radius: 12px;
        padding: 10px 14px;
        margin-bottom: 8px;
    }
    .tool-badge {
        background-color: #f1f5f9;
        border: 1px solid #cbd5e1;
        color: #0f172a;
        padding: 4px 10px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 0.82rem;
        margin: 4px 0;
        display: inline-block;
    }
    .file-tag {
        font-size: 0.85rem;
        color: #475569;
        margin-bottom: 4px;
    }
</style>
""", unsafe_allow_html=True)


# Sidebar Configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    env_api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY", "")
    api_key = st.text_input("OpenRouter / OpenAI API Key", value=env_api_key, type="password")
    base_url = st.text_input("Base URL", value=os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1"))
    model_name = st.text_input("Model Name", value=os.getenv("MODEL_NAME", "openai/gpt-4o-mini"))
    
    st.divider()
    
    # Resume Upload Section
    st.header("📤 Upload Resumes")
    uploaded_files = st.file_uploader(
        "Upload PDF, DOCX, or TXT resumes",
        type=["pdf", "docx", "txt"],
        accept_multiple_files=True
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            dest_path = os.path.join(RESUMES_DIR, uploaded_file.name)
            with open(dest_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
        st.success(f"Uploaded {len(uploaded_files)} resume(s) to `{RESUMES_DIR}/`")

    st.divider()

    # Manage Stored Resumes
    st.header("📁 Resumes in Library")
    current_files = fs_tools.list_files(RESUMES_DIR)
    if current_files:
        for f in current_files:
            col_a, col_b = st.columns([4, 1])
            with col_a:
                size_kb = round(f['size_bytes'] / 1024, 1)
                st.markdown(f"**{f['name']}**  \n<span class='file-tag'>{size_kb} KB • {f['modified_date']}</span>", unsafe_allow_html=True)
            with col_b:
                if st.button("🗑️", key=f"del_{f['name']}", help="Delete file"):
                    try:
                        os.remove(f["filepath"])
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error: {e}")
    else:
        st.info("No resumes found in `resumes/` folder.")

    st.divider()
    if st.button("🧹 Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.session_state.conversation_history = []
        st.rerun()


# Tool definitions for LLM
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory with optional extension filter (e.g. .pdf, .docx, .txt).",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Directory path (default: 'resumes')"},
                    "extension": {"type": "string", "description": "Optional extension like '.pdf' or '.txt'"}
                },
                "required": ["directory"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read text content and metadata from a PDF, DOCX, or TXT resume file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the resume file"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a destination file (e.g. outputs/summary.txt).",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Destination file path"},
                    "content": {"type": "string", "description": "Text content to write"}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_in_file",
            "description": "Search for a keyword inside a PDF, DOCX, or TXT file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file to search in"},
                    "keyword": {"type": "string", "description": "Keyword to look for"}
                },
                "required": ["filepath", "keyword"]
            }
        }
    }
]


def execute_tool(tool_name: str, args: dict):
    """Execute tool call from fs_tools."""
    if tool_name == "list_files":
        return fs_tools.list_files(args.get("directory", "resumes"), args.get("extension"))
    elif tool_name == "read_file":
        return fs_tools.read_file(args.get("filepath", ""))
    elif tool_name == "write_file":
        return fs_tools.write_file(args.get("filepath", ""), args.get("content", ""))
    elif tool_name == "search_in_file":
        return fs_tools.search_in_file(args.get("filepath", ""), args.get("keyword", ""))
    return {"status": "error", "message": f"Unknown tool: {tool_name}"}


# Main App Layout
st.title("📄 LLM-Powered Resume Assistant")
st.caption("Upload candidate resumes, search keywords/skills, compare qualifications, and generate summary files.")

# Initialize conversation states
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_history" not in st.session_state:
    st.session_state.conversation_history = [
        {
            "role": "system",
            "content": (
                "You are an expert File System Resume Assistant. Use your available tools "
                "(list_files, read_file, write_file, search_in_file) to inspect resumes in the "
                "'resumes/' folder and save generated reports in 'outputs/'. "
                "Always be concise, accurate, and professional."
            )
        }
    ]

# Display conversation messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# User Chat Input
if prompt := st.chat_input("Ask a question (e.g., 'Find all Python developers', 'Summarize resume_alex_rivera.docx')"):
    if not api_key:
        st.error("Please enter your API key in the sidebar configuration.")
        st.stop()

    client = OpenAI(base_url=base_url, api_key=api_key)

    # Render User Query
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.session_state.conversation_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Assistant Response
    with st.chat_message("assistant"):
        tool_container = st.container()
        reply_placeholder = st.empty()

        with st.spinner("Processing..."):
            for _ in range(6):
                try:
                    response = client.chat.completions.create(
                        model=model_name,
                        messages=st.session_state.conversation_history,
                        tools=tools,
                        tool_choice="auto"
                    )
                except Exception as e:
                    err_text = f"⚠️ API Error: {str(e)}"
                    reply_placeholder.error(err_text)
                    st.session_state.messages.append({"role": "assistant", "content": err_text})
                    st.stop()

                msg = response.choices[0].message
                st.session_state.conversation_history.append(msg)

                # Execute tool calls if requested
                if msg.tool_calls:
                    for tool_call in msg.tool_calls:
                        t_name = tool_call.function.name
                        try:
                            t_args = json.loads(tool_call.function.arguments)
                        except Exception:
                            t_args = {}

                        with tool_container:
                            st.markdown(
                                f"<span class='tool-badge'>⚡ Calling: <b>{t_name}</b> {t_args}</span>",
                                unsafe_allow_html=True
                            )

                        result = execute_tool(t_name, t_args)

                        st.session_state.conversation_history.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })
                else:
                    final_reply = msg.content or ""
                    reply_placeholder.markdown(final_reply)
                    st.session_state.messages.append({"role": "assistant", "content": final_reply})
                    break
