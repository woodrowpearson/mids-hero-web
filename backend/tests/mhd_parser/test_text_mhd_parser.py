"""Tests for parsing text-based MHD files."""

import io
from typing import List, Dict, Union

import pytest

from app.mhd_parser.text_mhd_parser import (
    parse_text_mhd, detect_file_format, TextMhdFile, FileFormat
)


class TestFileFormatDetection:
    """Test cases for detecting binary vs text file formats."""
    
    def test_detect_binary_format(self):
        """Test detecting binary MHD format."""
        # Binary file starts with a 7-bit encoded string length
        data = io.BytesIO(b'\x1CMids Reborn Powers Database')
        assert detect_file_format(data) == FileFormat.BINARY
        
    def test_detect_text_format_with_version(self):
        """Test detecting text format with version header."""
        data = io.BytesIO(b'Version 1.0\nData line 1\nData line 2')
        assert detect_file_format(data) == FileFormat.TEXT_WITH_VERSION
        
    def test_detect_text_format_tsv(self):
        """Test detecting tab-delimited text format."""
        data = io.BytesIO(b'Name\tValue\tDescription\nTest\t123\tA test value')
        assert detect_file_format(data) == FileFormat.TEXT_TSV
        
    def test_detect_empty_file(self):
        """Test detecting empty file."""
        data = io.BytesIO(b'')
        with pytest.raises(EOFError):
            detect_file_format(data)


class TestTextMhdParser:
    """Test cases for parsing text-based MHD files."""
    
    def test_parse_origins_mhd(self):
        """Test parsing Origins.mhd file format."""
        content = """Version 1.5.0
Science
Technology
Mutation
Magic
Natural"""
        
        data = io.BytesIO(content.encode())
        result = parse_text_mhd(data)
        
        assert isinstance(result, TextMhdFile)
        assert result.version == "1.5.0"
        assert result.headers == []
        assert len(result.data) == 5
        assert result.data[0] == ["Science"]
        assert result.data[1] == ["Technology"]
        assert result.data[4] == ["Natural"]
    
    def test_parse_nlevels_mhd(self):
        """Test parsing NLevels.mhd (tab-delimited) format."""
        content = """Level\tExperience\tInfluence
1\t0\t0
2\t106\t50
3\t337\t150
4\t582\t300
5\t800\t500"""
        
        data = io.BytesIO(content.encode())
        result = parse_text_mhd(data)
        
        assert result.version is None
        assert result.headers == ["Level", "Experience", "Influence"]
        assert len(result.data) == 5
        assert result.data[0] == ["1", "0", "0"]
        assert result.data[1] == ["2", "106", "50"]
        assert result.data[4] == ["5", "800", "500"]
    
    def test_parse_eclasses_mhd(self):
        """Test parsing EClasses.mhd file format."""
        content = """Version 2.0.3
Blaster_Ranged
Blaster_Support
Controller_Control
Controller_Buff
Defender_Buff
Defender_Ranged"""
        
        data = io.BytesIO(content.encode())
        result = parse_text_mhd(data)
        
        assert result.version == "2.0.3"
        assert len(result.data) == 6
        assert result.data[0] == ["Blaster_Ranged"]
        assert result.data[5] == ["Defender_Ranged"]
    
    def test_parse_rlevels_mhd(self):
        """Test parsing RLevels.mhd (recipe levels) format."""
        content = """Level\tCost_Common\tCost_Uncommon\tCost_Rare\tCost_VeryRare
10\t1000\t2000\t5000\t10000
15\t1500\t3000\t7500\t15000
20\t2000\t4000\t10000\t20000
25\t2500\t5000\t12500\t25000"""
        
        data = io.BytesIO(content.encode())
        result = parse_text_mhd(data)
        
        assert result.headers == ["Level", "Cost_Common", "Cost_Uncommon", "Cost_Rare", "Cost_VeryRare"]
        assert len(result.data) == 4
        assert result.data[0] == ["10", "1000", "2000", "5000", "10000"]
        assert result.data[3] == ["25", "2500", "5000", "12500", "25000"]
    
    def test_parse_text_with_empty_lines(self):
        """Test parsing text file with empty lines."""
        content = """Version 1.0

Line 1

Line 2


Line 3"""
        
        data = io.BytesIO(content.encode())
        result = parse_text_mhd(data)
        
        assert result.version == "1.0"
        # Empty lines should be skipped
        assert len(result.data) == 3
        assert result.data[0] == ["Line 1"]
        assert result.data[1] == ["Line 2"]
        assert result.data[2] == ["Line 3"]
    
    def test_parse_text_with_comments(self):
        """Test parsing text file with comment lines."""
        content = """Version 1.0
# This is a comment
Data line 1
# Another comment
Data line 2
// C-style comment
Data line 3"""
        
        data = io.BytesIO(content.encode())
        result = parse_text_mhd(data)
        
        assert result.version == "1.0"
        # Comments should be included as-is (parser doesn't filter them)
        assert len(result.data) == 6
        assert result.data[0] == ["# This is a comment"]
        assert result.data[1] == ["Data line 1"]
    
    def test_parse_mixed_delimiters(self):
        """Test parsing with mixed tab and space delimiters."""
        content = """Name\tValue Description
Test1\t100 A test value
Test2\t200 Another value"""
        
        data = io.BytesIO(content.encode())
        result = parse_text_mhd(data)
        
        # Should be parsed as TSV (tabs take precedence)
        assert result.headers == ["Name", "Value Description"]
        assert result.data[0] == ["Test1", "100 A test value"]