import json
import os
from dotenv import load_dotenv
from openai import OpenAI

import fs_tools

# Load environment variables
load_dotenv()

api_key = os.getenv("OPENROUTER_API_KEY") or os.getenv("OPENAI_API_KEY")
base_url = os.getenv("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")
model = os.getenv("MODEL_NAME", "openai/gpt-4o-mini")

client = OpenAI(
    base_url=base_url,
    api_key=api_key
)

# Tool definitions
tools = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "List files in a directory with optional extension filter.",
            "parameters": {
                "type": "object",
                "properties": {
                    "directory": {"type": "string", "description": "Folder path (e.g. 'resumes')"},
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
            "description": "Read text content and metadata from a PDF, DOCX, or TXT file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Path to the file"}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write text content to a file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Destination file path"},
                    "content": {"type": "string", "description": "Text to write into the file"}
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
                    "filepath": {"type": "string", "description": "Path to the file"},
                    "keyword": {"type": "string", "description": "Keyword to look for"}
                },
                "required": ["filepath", "keyword"]
            }
        }
    }
]


def execute_tool(tool_name: str, args: dict):
    """Run the matching function from fs_tools."""
    print(f" -> Calling tool: {tool_name}({args})")

    if tool_name == "list_files":
        return fs_tools.list_files(args.get("directory", "."), args.get("extension"))
    elif tool_name == "read_file":
        return fs_tools.read_file(args.get("filepath", ""))
    elif tool_name == "write_file":
        return fs_tools.write_file(args.get("filepath", ""), args.get("content", ""))
    elif tool_name == "search_in_file":
        return fs_tools.search_in_file(args.get("filepath", ""), args.get("keyword", ""))
    return {"status": "error", "message": f"Unknown tool: {tool_name}"}


def chat(prompt: str, messages: list) -> str:
    """Send user message to LLM, handle tool calls, and return final answer."""
    messages.append({"role": "user", "content": prompt})

    # Allow model to call tools up to 5 times per query
    for _ in range(5):
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto"
        )
        msg = response.choices[0].message
        messages.append(msg)

        if not msg.tool_calls:
            return msg.content

        # Handle tool calls
        for tool_call in msg.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)
            result = execute_tool(name, args)

            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "content": json.dumps(result)
            })

    return "Could not complete request within step limit."


def main():
    print("=" * 50)
    print("File System Assistant (Resume Manager)")
    print("Type 'exit' to quit.")
    print("=" * 50)

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful file system assistant. Use your tools to read, "
                "search, list, and write resume files whenever requested."
            )
        }
    ]

    while True:
        user_input = input("\nYou: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ["exit", "quit"]:
            print("Bye!")
            break

        print("\nThinking...")
        answer = chat(user_input, messages)
        print(f"\nAssistant:\n{answer}")


if __name__ == "__main__":
    main()
