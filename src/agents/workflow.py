import os
import re

from src.agents.planner import create_plan
from src.agents.task_router import route_task
from src.agents.memory import AgentMemory
from src.agents.audit import audit_event


def _document_texts(value):
    """Yield document text and source from common RAG result formats."""
    if isinstance(value, (list, tuple)):
        for item in value:
            yield from _document_texts(item)
        return

    if not isinstance(value, dict):
        return

    metadata = value.get("metadata")
    metadata = metadata if isinstance(metadata, dict) else {}
    source = str(
        metadata.get("source")
        or value.get("source")
        or value.get("filename")
        or ""
    )

    for key in ("content", "page_content", "text", "document"):
        content = value.get(key)
        if isinstance(content, str) and content.strip():
            yield content.strip(), source
            return

    for key in ("result", "results", "documents", "data"):
        if key in value:
            yield from _document_texts(value[key])


def _extract_answer(question, result):
    """Select a relevant sentence from retrieved documents; do not invent facts."""
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "what", "where",
        "when", "who", "why", "how", "which", "of", "in", "on", "to",
        "for", "and", "or", "please", "tell", "me", "about",
        "\u0995\u09cb\u09a5\u09be\u09af\u09bc", "\u0995\u09cb\u09a5\u09be\u09af\u09bc?",
        "\u0995\u09c0", "\u0995\u09bf", "\u0995\u09c7", "\u0995\u09c7\u09a8",
        "\u0995\u09bf\u09ad\u09be\u09ac\u09c7", "\u0995\u09cb\u09a8",
        "\u09ac\u09b2\u09c1\u09a8", "\u09b9\u09b2\u09cb", "\u09b9\u09af\u09bc",
        "\u098f\u09b0", "\u098f\u09ac\u0982", "\u099f\u09be",
    }

    query_tokens = {
        token for token in re.findall(r"\w+", str(question).lower())
        if len(token) > 1 and token not in stopwords
    }

    candidates = []
    for content, source in _document_texts(result):
        sentences = re.split(r"[.!?\u0964\n]+", content)
        for sentence in sentences:
            sentence = sentence.strip(" \t\r-=:")
            if not sentence:
                continue

            sentence_tokens = set(re.findall(r"\w+", sentence.lower()))
            overlap = query_tokens & sentence_tokens
            if overlap:
                score = (
                    len(overlap),
                    len(overlap) / max(len(query_tokens), 1),
                    -len(sentence),
                )
                candidates.append((score, sentence, source))

    if not candidates:
        return (
            "No clear answer could be extracted from the retrieved documents. "
            "Please review the source documents below.",
            "",
        )

    candidates.sort(key=lambda item: item[0], reverse=True)
    _, answer, source = candidates[0]
    source_name = re.split(r"[\\/]", source)[-1] if source else ""
    return answer, source_name


class AgentWorkflow:
    def __init__(self, executor=None, memory=None):
        self.executor = executor
        self.memory = memory or AgentMemory()

    def run(self, task, **tool_kwargs):
        plan = create_plan(task)
        tool_name = route_task(task)

        if tool_name == "general_response":
            result = {
                "message": "No specialized tool matched this task.",
                "task": task,
            }

        elif self.executor is None:
            result = {
                "error": "No tool executor configured",
                "tool": tool_name,
            }

        elif tool_name == "search_documents":
            result = self.executor.execute(
                tool_name,
                query=tool_kwargs.get("query") or str(task),
                top_k=tool_kwargs.get("top_k", 5),
            )

        elif tool_name == "summarize_text":
            result = self.executor.execute(
                tool_name,
                text=tool_kwargs.get("text") or str(task),
            )

        else:
            result = {
                "message": "Unsupported tool.",
                "tool": tool_name,
            }

        if tool_name == "search_documents":
            answer, answer_source = _extract_answer(task, result)
        elif isinstance(result, dict):
            answer = str(
                result.get("summary")
                or result.get("message")
                or result.get("error")
                or ""
            )
            answer_source = ""
        else:
            answer = ""
            answer_source = ""

        self.memory.remember(task, result)
        audit_event("workflow_completed", {"tool": tool_name})

        return {
            "plan": plan,
            "tool": tool_name,
            "result": result,
            "answer": answer,
            "answer_source": answer_source,
        }
