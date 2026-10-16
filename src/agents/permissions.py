DEFAULT_ALLOWED_TOOLS = {"search_documents", "summarize_text"}

def check_permission(tool_name, allowed_tools=None):
    allowed = DEFAULT_ALLOWED_TOOLS if allowed_tools is None else set(allowed_tools)
    return tool_name in allowed
