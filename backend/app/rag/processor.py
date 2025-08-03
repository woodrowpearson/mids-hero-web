"""Multi-format document processor for RAG indexing."""

import ast
import hashlib
import json
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles
import tiktoken

from .exceptions import DocumentProcessingError

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """Process various document formats for RAG indexing."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        """Initialize document processor."""
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # File type handlers
        self.handlers = {
            ".py": self._process_python,
            ".ts": self._process_typescript,
            ".tsx": self._process_typescript,
            ".js": self._process_javascript,
            ".jsx": self._process_javascript,
            ".md": self._process_markdown,
            ".json": self._process_json,
            ".yaml": self._process_yaml,
            ".yml": self._process_yaml,
            ".txt": self._process_text,
            ".sql": self._process_sql,
            ".cs": self._process_csharp,
        }

    async def process_file(self, file_path: Path) -> list[dict[str, Any]]:
        """Process a single file and return chunks with metadata."""
        if not file_path.exists():
            raise DocumentProcessingError(f"File not found: {file_path}")

        suffix = file_path.suffix.lower()
        handler = self.handlers.get(suffix, self._process_text)

        try:
            async with aiofiles.open(file_path, encoding="utf-8") as f:
                content = await f.read()

            # Process content with appropriate handler
            chunks = await handler(content, file_path)

            # Add common metadata to all chunks
            for i, chunk in enumerate(chunks):
                chunk["metadata"].update(
                    {
                        "file_path": str(file_path),
                        "file_name": file_path.name,
                        "file_type": suffix,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                        "processed_at": datetime.now().isoformat(),
                        "chunk_id": self._generate_chunk_id(file_path, i),
                    }
                )

            return chunks

        except Exception as e:
            raise DocumentProcessingError(f"Failed to process {file_path}: {e}")

    def _generate_chunk_id(self, file_path: Path, chunk_index: int) -> str:
        """Generate unique ID for a chunk."""
        id_string = f"{file_path}:{chunk_index}"
        return hashlib.sha256(id_string.encode()).hexdigest()[:16]

    def _chunk_text(
        self, text: str, metadata: dict[str, Any] = None
    ) -> list[dict[str, Any]]:
        """Split text into overlapping chunks."""
        tokens = self.tokenizer.encode(text)
        chunks = []

        for i in range(0, len(tokens), self.chunk_size - self.chunk_overlap):
            chunk_tokens = tokens[i : i + self.chunk_size]
            chunk_text = self.tokenizer.decode(chunk_tokens)

            chunks.append(
                {
                    "text": chunk_text,
                    "metadata": metadata or {},
                    "token_count": len(chunk_tokens),
                }
            )

        return chunks

    async def _process_python(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Process Python files with AST parsing."""
        chunks = []

        try:
            tree = ast.parse(content)

            # Extract classes and functions
            for node in ast.walk(tree):
                if isinstance(
                    node, ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef
                ):
                    # Get the source code for this node
                    start_line = node.lineno - 1
                    end_line = node.end_lineno or start_line + 1
                    lines = content.split("\n")[start_line:end_line]
                    node_content = "\n".join(lines)

                    # Get docstring
                    docstring = ast.get_docstring(node) or ""

                    metadata = {
                        "type": "python_"
                        + node.__class__.__name__.lower().replace("def", ""),
                        "name": node.name,
                        "line_start": node.lineno,
                        "line_end": end_line,
                        "has_docstring": bool(docstring),
                    }

                    # Combine docstring with code for context
                    if docstring:
                        chunk_text = f"{node.name}: {docstring}\n\n{node_content}"
                    else:
                        chunk_text = node_content

                    chunks.append(
                        {
                            "text": chunk_text,
                            "metadata": metadata,
                            "token_count": len(self.tokenizer.encode(chunk_text)),
                        }
                    )

            # Also create chunks for the full file
            file_chunks = self._chunk_text(content, {"type": "python_file"})
            chunks.extend(file_chunks)

        except SyntaxError:
            # Fallback to simple chunking if parsing fails
            chunks = self._chunk_text(
                content, {"type": "python_file", "parse_error": True}
            )

        return chunks

    async def _process_typescript(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Process TypeScript/TSX files."""
        chunks = []

        # Extract interfaces, types, and functions using regex
        patterns = [
            (r"interface\s+(\w+)", "interface"),
            (r"type\s+(\w+)", "type"),
            (r"class\s+(\w+)", "class"),
            (r"function\s+(\w+)", "function"),
            (r"const\s+(\w+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>", "arrow_function"),
            (r"export\s+(?:default\s+)?(?:function|const)\s+(\w+)", "export"),
        ]

        for pattern, node_type in patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1)
                start = match.start()

                # Try to find the end of the definition
                # Simple heuristic: look for next definition or end of file
                end = len(content)
                for next_match in re.finditer(
                    r"\n(?:export\s+)?(?:interface|type|class|function|const)\s+\w+",
                    content[start + 1 :],
                ):
                    end = start + next_match.start() + 1
                    break

                definition = content[start:end].strip()

                metadata = {
                    "type": f"typescript_{node_type}",
                    "name": name,
                    "char_start": start,
                    "char_end": end,
                }

                chunks.append(
                    {
                        "text": definition,
                        "metadata": metadata,
                        "token_count": len(self.tokenizer.encode(definition)),
                    }
                )

        # Also create chunks for the full file
        file_chunks = self._chunk_text(content, {"type": "typescript_file"})
        chunks.extend(file_chunks)

        return chunks

    async def _process_javascript(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Process JavaScript/JSX files."""
        # Similar to TypeScript but without type annotations
        return await self._process_typescript(content, file_path)

    async def _process_markdown(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Process Markdown files with section awareness."""
        chunks = []

        # Split by headers
        sections = re.split(r"\n(?=#+ )", content)

        for section in sections:
            if not section.strip():
                continue

            # Extract header
            header_match = re.match(r"^(#+)\s+(.+)$", section, re.MULTILINE)
            if header_match:
                level = len(header_match.group(1))
                title = header_match.group(2)

                metadata = {
                    "type": "markdown_section",
                    "header_level": level,
                    "title": title,
                }
            else:
                metadata = {"type": "markdown_content"}

            # Chunk the section if it's too large
            if len(self.tokenizer.encode(section)) > self.chunk_size:
                section_chunks = self._chunk_text(section, metadata)
                chunks.extend(section_chunks)
            else:
                chunks.append(
                    {
                        "text": section,
                        "metadata": metadata,
                        "token_count": len(self.tokenizer.encode(section)),
                    }
                )

        return chunks

    async def _process_json(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Process JSON files."""
        try:
            data = json.loads(content)

            # For small JSON files, keep as single chunk
            if len(content) < self.chunk_size * 4:  # Approximate
                return [
                    {
                        "text": content,
                        "metadata": {
                            "type": "json_file",
                            "keys": list(data.keys()) if isinstance(data, dict) else [],
                        },
                        "token_count": len(self.tokenizer.encode(content)),
                    }
                ]

            # For large JSON, chunk by top-level keys
            chunks = []
            if isinstance(data, dict):
                for key, value in data.items():
                    chunk_content = json.dumps({key: value}, indent=2)
                    chunks.append(
                        {
                            "text": chunk_content,
                            "metadata": {"type": "json_object", "key": key},
                            "token_count": len(self.tokenizer.encode(chunk_content)),
                        }
                    )
            else:
                # Fall back to text chunking
                chunks = self._chunk_text(content, {"type": "json_array"})

            return chunks

        except json.JSONDecodeError:
            # Fallback to text processing
            return self._chunk_text(content, {"type": "json_file", "parse_error": True})

    async def _process_yaml(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Process YAML files."""
        # For now, treat as text with yaml type
        return self._chunk_text(content, {"type": "yaml_file"})

    async def _process_sql(self, content: str, file_path: Path) -> list[dict[str, Any]]:
        """Process SQL files."""
        chunks = []

        # Split by statements (simple approach)
        statements = re.split(r";\s*\n", content)

        for statement in statements:
            if not statement.strip():
                continue

            # Identify statement type
            statement_type = "unknown"
            if re.match(r"^\s*CREATE\s+TABLE", statement, re.IGNORECASE):
                statement_type = "create_table"
            elif re.match(r"^\s*CREATE\s+INDEX", statement, re.IGNORECASE):
                statement_type = "create_index"
            elif re.match(r"^\s*ALTER\s+TABLE", statement, re.IGNORECASE):
                statement_type = "alter_table"
            elif re.match(r"^\s*INSERT\s+INTO", statement, re.IGNORECASE):
                statement_type = "insert"
            elif re.match(r"^\s*SELECT", statement, re.IGNORECASE):
                statement_type = "select"

            chunks.append(
                {
                    "text": statement + ";",
                    "metadata": {
                        "type": "sql_statement",
                        "statement_type": statement_type,
                    },
                    "token_count": len(self.tokenizer.encode(statement)),
                }
            )

        return chunks

    async def _process_csharp(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Process C# files (for MidsReborn code)."""
        chunks = []

        # Extract classes, methods, and properties using regex
        patterns = [
            (
                r"(?:public|private|protected|internal)\s+(?:static\s+)?class\s+(\w+)",
                "class",
            ),
            (
                r"(?:public|private|protected|internal)\s+(?:static\s+)?(?:async\s+)?(?:\w+\s+)+(\w+)\s*\([^)]*\)",
                "method",
            ),
            (
                r"(?:public|private|protected|internal)\s+(?:static\s+)?(?:\w+\s+)+(\w+)\s*{",
                "property",
            ),
        ]

        for pattern, node_type in patterns:
            for match in re.finditer(pattern, content):
                name = match.group(1)
                start = match.start()

                # Find the end of the definition (simple brace matching)
                brace_count = 0
                end = start
                for i, char in enumerate(content[start:], start):
                    if char == "{":
                        brace_count += 1
                    elif char == "}":
                        brace_count -= 1
                        if brace_count == 0:
                            end = i + 1
                            break

                definition = content[start:end].strip()

                metadata = {
                    "type": f"csharp_{node_type}",
                    "name": name,
                    "char_start": start,
                    "char_end": end,
                }

                chunks.append(
                    {
                        "text": definition,
                        "metadata": metadata,
                        "token_count": len(self.tokenizer.encode(definition)),
                    }
                )

        # Also create chunks for the full file
        file_chunks = self._chunk_text(content, {"type": "csharp_file"})
        chunks.extend(file_chunks)

        return chunks

    async def _process_text(
        self, content: str, file_path: Path
    ) -> list[dict[str, Any]]:
        """Process plain text files."""
        return self._chunk_text(content, {"type": "text_file"})

    async def process_directory(
        self,
        directory: Path,
        patterns: list[str] | None = None,
        ignore_patterns: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Process all files in a directory."""
        if not directory.is_dir():
            raise DocumentProcessingError(f"Not a directory: {directory}")

        # Default patterns
        if patterns is None:
            patterns = [
                "**/*.py",
                "**/*.ts",
                "**/*.tsx",
                "**/*.js",
                "**/*.jsx",
                "**/*.md",
                "**/*.json",
                "**/*.yaml",
                "**/*.yml",
            ]

        # Default ignore patterns
        if ignore_patterns is None:
            ignore_patterns = [
                "**/node_modules/**",
                "**/.git/**",
                "**/__pycache__/**",
                "**/dist/**",
                "**/build/**",
                "**/.next/**",
            ]

        all_chunks = []
        processed_files = 0

        for pattern in patterns:
            for file_path in directory.glob(pattern):
                # Check ignore patterns
                if any(file_path.match(ignore) for ignore in ignore_patterns):
                    continue

                try:
                    chunks = await self.process_file(file_path)
                    all_chunks.extend(chunks)
                    processed_files += 1

                    if processed_files % 10 == 0:
                        logger.info(f"Processed {processed_files} files...")

                except Exception as e:
                    logger.error(f"Failed to process {file_path}: {e}")

        logger.info(
            f"Processed {processed_files} files, generated {len(all_chunks)} chunks"
        )
        return all_chunks
