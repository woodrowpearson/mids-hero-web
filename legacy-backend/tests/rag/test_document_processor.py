"""Tests for document processor."""

import json
from pathlib import Path

import pytest

from app.rag import DocumentProcessingError, DocumentProcessor


@pytest.fixture
def processor():
    """Create a document processor."""
    return DocumentProcessor(chunk_size=100, chunk_overlap=20)


@pytest.fixture
def temp_files(tmp_path):
    """Create temporary test files."""
    files = {}

    # Python file
    python_file = tmp_path / "test.py"
    python_file.write_text('''
def calculate_damage(base_damage, enhancements):
    """Calculate total damage with enhancements."""
    total = base_damage
    for enhancement in enhancements:
        total *= (1 + enhancement.bonus)
    return total

class PowerSet:
    """Represents a character powerset."""

    def __init__(self, name):
        self.name = name
        self.powers = []

    def add_power(self, power):
        """Add a power to the set."""
        self.powers.append(power)
''')
    files["python"] = python_file

    # TypeScript file
    ts_file = tmp_path / "component.tsx"
    ts_file.write_text('''
interface PowerData {
  id: number;
  name: string;
  damage: number;
}

type EnhancementType = "damage" | "accuracy" | "recharge";

export function PowerSelector({ powers }: { powers: PowerData[] }) {
  return (
    <div>
      {powers.map(power => (
        <div key={power.id}>{power.name}</div>
      ))}
    </div>
  );
}

const calculateEnhancement = (base: number, bonus: number): number => {
  return base * (1 + bonus);
};
''')
    files["typescript"] = ts_file

    # Markdown file
    md_file = tmp_path / "readme.md"
    md_file.write_text('''
# RAG System Documentation

This is the main documentation for the RAG system.

## Features

- Gemini embeddings
- ChromaDB storage
- Multi-format support

### Installation

Run the following commands:

```bash
uv pip install -r requirements.txt
```

## Usage

Import and use the system:

```python
from app.rag import EmbeddingClient
```
''')
    files["markdown"] = md_file

    # JSON file
    json_file = tmp_path / "config.json"
    json_file.write_text(json.dumps({
        "api": {
            "endpoint": "http://localhost:8000",
            "version": "v1"
        },
        "database": {
            "host": "localhost",
            "port": 5432
        },
        "features": ["rag", "auth", "api"]
    }, indent=2))
    files["json"] = json_file

    # SQL file
    sql_file = tmp_path / "schema.sql"
    sql_file.write_text('''
CREATE TABLE powers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT
);

CREATE INDEX idx_powers_name ON powers(name);

ALTER TABLE powers ADD COLUMN damage_type VARCHAR(50);

INSERT INTO powers (name, description) VALUES
    ('Fire Blast', 'A blast of fire'),
    ('Ice Shield', 'Protective ice barrier');

SELECT * FROM powers WHERE damage_type = 'Fire';
''')
    files["sql"] = sql_file

    # C# file
    cs_file = tmp_path / "Power.cs"
    cs_file.write_text('''
using System;

namespace MidsReborn
{
    public class Power
    {
        public int Id { get; set; }
        public string Name { get; set; }

        public float CalculateDamage(float baseDamage)
        {
            return baseDamage * DamageModifier;
        }
    }

    internal class PowerSet
    {
        private List<Power> powers = new List<Power>();

        public void AddPower(Power power)
        {
            powers.Add(power);
        }
    }
}
''')
    files["csharp"] = cs_file

    # Plain text file
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("These are some notes about the project. " * 50)
    files["text"] = txt_file

    return files


class TestDocumentProcessor:
    """Test document processor functionality."""

    @pytest.mark.asyncio
    async def test_process_python_file(self, processor, temp_files):
        """Test processing Python files."""
        chunks = await processor.process_file(temp_files["python"])

        assert len(chunks) > 0

        # Check for function/class extraction
        chunk_types = [chunk["metadata"]["type"] for chunk in chunks]
        assert "python_function" in chunk_types
        assert "python_class" in chunk_types
        assert "python_file" in chunk_types

        # Check metadata
        for chunk in chunks:
            assert "file_path" in chunk["metadata"]
            assert "file_name" in chunk["metadata"]
            assert "file_type" in chunk["metadata"]
            assert chunk["metadata"]["file_type"] == ".py"
            assert "chunk_id" in chunk["metadata"]
            assert "token_count" in chunk

    @pytest.mark.asyncio
    async def test_process_typescript_file(self, processor, temp_files):
        """Test processing TypeScript files."""
        chunks = await processor.process_file(temp_files["typescript"])

        assert len(chunks) > 0

        # Check for interface/function extraction
        chunk_texts = [chunk["text"] for chunk in chunks]
        assert any("interface PowerData" in text for text in chunk_texts)
        assert any("PowerSelector" in text for text in chunk_texts)

        # Check metadata
        chunk_types = [chunk["metadata"].get("type", "") for chunk in chunks]
        assert any("typescript" in t for t in chunk_types)

    @pytest.mark.asyncio
    async def test_process_markdown_file(self, processor, temp_files):
        """Test processing Markdown files."""
        chunks = await processor.process_file(temp_files["markdown"])

        assert len(chunks) > 0

        # Check for section awareness
        has_sections = False
        for chunk in chunks:
            if chunk["metadata"].get("type") == "markdown_section":
                has_sections = True
                assert "title" in chunk["metadata"]
                assert "header_level" in chunk["metadata"]

        assert has_sections

    @pytest.mark.asyncio
    async def test_process_json_file(self, processor, temp_files):
        """Test processing JSON files."""
        chunks = await processor.process_file(temp_files["json"])

        assert len(chunks) > 0

        # Small JSON should be single chunk
        assert any(
            chunk["metadata"].get("type") == "json_file"
            for chunk in chunks
        )

    @pytest.mark.asyncio
    async def test_process_sql_file(self, processor, temp_files):
        """Test processing SQL files."""
        chunks = await processor.process_file(temp_files["sql"])

        assert len(chunks) > 0

        # Check for statement types
        statement_types = [
            chunk["metadata"].get("statement_type", "")
            for chunk in chunks
            if chunk["metadata"].get("type") == "sql_statement"
        ]

        assert "create_table" in statement_types
        assert "create_index" in statement_types
        assert "alter_table" in statement_types
        assert "insert" in statement_types
        assert "select" in statement_types

    @pytest.mark.asyncio
    async def test_process_csharp_file(self, processor, temp_files):
        """Test processing C# files."""
        chunks = await processor.process_file(temp_files["csharp"])

        assert len(chunks) > 0

        # Check for class/method extraction
        chunk_types = [chunk["metadata"].get("type", "") for chunk in chunks]
        assert any("csharp_class" in t for t in chunk_types)
        assert any("csharp_method" in t for t in chunk_types)

    @pytest.mark.asyncio
    async def test_process_text_file(self, processor, temp_files):
        """Test processing plain text files."""
        chunks = await processor.process_file(temp_files["text"])

        assert len(chunks) > 0

        # Should use text chunking
        for chunk in chunks:
            assert chunk["metadata"]["type"] == "text_file"
            assert len(chunk["text"]) > 0

    @pytest.mark.asyncio
    async def test_chunking_overlap(self, processor, tmp_path):
        """Test that chunking includes overlap."""
        # Create file with predictable content
        test_file = tmp_path / "chunking_test.txt"
        content = " ".join([f"word{i}" for i in range(1000)])
        test_file.write_text(content)

        chunks = await processor.process_file(test_file)

        assert len(chunks) > 1

        # Check overlap between consecutive chunks
        for i in range(len(chunks) - 1):
            chunk1_end = chunks[i]["text"].split()[-10:]
            chunk2_start = chunks[i + 1]["text"].split()[:10]

            # Should have some overlap
            overlap = set(chunk1_end) & set(chunk2_start)
            assert len(overlap) > 0

    @pytest.mark.asyncio
    async def test_file_not_found(self, processor):
        """Test handling of non-existent files."""
        with pytest.raises(DocumentProcessingError):
            await processor.process_file(Path("/nonexistent/file.py"))

    @pytest.mark.asyncio
    async def test_process_directory(self, processor, temp_files):
        """Test processing an entire directory."""
        directory = temp_files["python"].parent

        chunks = await processor.process_directory(
            directory,
            patterns=["**/*.py", "**/*.md", "**/*.json"]
        )

        assert len(chunks) > 0

        # Check we got chunks from different file types
        file_types = {chunk["metadata"]["file_type"] for chunk in chunks}
        assert ".py" in file_types
        assert ".md" in file_types
        assert ".json" in file_types

    @pytest.mark.asyncio
    async def test_ignore_patterns(self, processor, tmp_path):
        """Test that ignore patterns work."""
        # Create test structure
        (tmp_path / "src").mkdir()
        (tmp_path / "src" / "main.py").write_text("# Main file")

        (tmp_path / "node_modules").mkdir()
        (tmp_path / "node_modules" / "lib.py").write_text("# Should be ignored")

        (tmp_path / "__pycache__").mkdir()
        (tmp_path / "__pycache__" / "cache.py").write_text("# Should be ignored")

        chunks = await processor.process_directory(
            tmp_path,
            patterns=["**/*.py"],
            ignore_patterns=["**/node_modules/**", "**/__pycache__/**"]
        )

        # Should only find main.py
        file_names = {chunk["metadata"]["file_name"] for chunk in chunks}
        assert "main.py" in file_names
        assert "lib.py" not in file_names
        assert "cache.py" not in file_names

    def test_chunk_id_generation(self, processor):
        """Test that chunk IDs are unique and consistent."""
        file_path = Path("/test/file.py")

        id1 = processor._generate_chunk_id(file_path, 0)
        id2 = processor._generate_chunk_id(file_path, 1)
        id3 = processor._generate_chunk_id(file_path, 0)

        # Different chunks should have different IDs
        assert id1 != id2

        # Same file and chunk index should have same ID
        assert id1 == id3

        # IDs should be 16 characters
        assert len(id1) == 16
        assert len(id2) == 16

    @pytest.mark.asyncio
    async def test_large_file_handling(self, processor, tmp_path):
        """Test handling of large files."""
        # Create a large file
        large_file = tmp_path / "large.txt"
        large_content = "This is a test sentence. " * 10000
        large_file.write_text(large_content)

        chunks = await processor.process_file(large_file)

        # Should create multiple chunks
        assert len(chunks) > 10

        # Each chunk should respect size limits
        for chunk in chunks:
            assert chunk["token_count"] <= processor.chunk_size

    @pytest.mark.asyncio
    async def test_unicode_handling(self, processor, tmp_path):
        """Test handling of Unicode content."""
        unicode_file = tmp_path / "unicode.txt"
        unicode_file.write_text("Hello 世界! 🌍 Émojis and special çharacters.")

        chunks = await processor.process_file(unicode_file)

        assert len(chunks) > 0
        assert "世界" in chunks[0]["text"]
        assert "🌍" in chunks[0]["text"]

    @pytest.mark.asyncio
    async def test_malformed_json(self, processor, tmp_path):
        """Test handling of malformed JSON files."""
        bad_json = tmp_path / "bad.json"
        bad_json.write_text('{"invalid": json content}')

        # Should fall back to text processing
        chunks = await processor.process_file(bad_json)

        assert len(chunks) > 0
        assert chunks[0]["metadata"]["type"] == "json_file"
        assert chunks[0]["metadata"].get("parse_error") is True

    @pytest.mark.asyncio
    async def test_syntax_error_python(self, processor, tmp_path):
        """Test handling of Python files with syntax errors."""
        bad_python = tmp_path / "bad.py"
        bad_python.write_text("""
def broken_function(
    # Missing closing parenthesis
    pass

class Also broken
""")

        # Should fall back to text chunking
        chunks = await processor.process_file(bad_python)

        assert len(chunks) > 0
        assert chunks[0]["metadata"]["type"] == "python_file"
        assert chunks[0]["metadata"].get("parse_error") is True
