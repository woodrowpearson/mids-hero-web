using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Newtonsoft.Json;

namespace DataExporter
{
    /// <summary>
    /// Simple MHD parser that handles the actual binary format used by Homecoming files
    /// </summary>
    public class SimpleMhdParser
    {
        public static void ParseAndConvert(string inputPath, string outputPath)
        {
            var i12File = Path.Combine(inputPath, "I12.mhd");
            if (!File.Exists(i12File))
            {
                Console.WriteLine($"I12.mhd not found at {i12File}");
                return;
            }

            try
            {
                // Read the file and analyze its structure
                var bytes = File.ReadAllBytes(i12File);
                Console.WriteLine($"File size: {bytes.Length:N0} bytes");
                
                // Based on hex dump analysis:
                // 0x00: Length byte (0x1b = 27)
                // 0x01-0x1b: "Mids Reborn Powers Database"
                // 0x1c: Length byte (0x0b = 11) 
                // 0x1d-0x27: "2025.7.1111" (version)
                
                var pos = 0;
                
                // Read header string
                var headerLen = bytes[pos++];
                var header = Encoding.UTF8.GetString(bytes, pos, headerLen);
                pos += headerLen;
                Console.WriteLine($"Header: {header}");
                
                // Read version string
                var versionLen = bytes[pos++];
                var version = Encoding.UTF8.GetString(bytes, pos, versionLen);
                pos += versionLen;
                Console.WriteLine($"Version: {version}");
                
                // Skip unknown bytes (appears to be 16 bytes of data)
                pos += 16;
                
                // Read sections
                var result = new
                {
                    Header = header,
                    Version = version,
                    FileInfo = new
                    {
                        Size = bytes.Length,
                        ParsedBytes = pos,
                        Note = "Binary format requires full reverse engineering"
                    },
                    Archetypes = ExtractArchetypeNames(bytes, pos)
                };
                
                // Save what we can parse
                var outputFile = Path.Combine(outputPath, "i12_partial.json");
                File.WriteAllText(outputFile, JsonConvert.SerializeObject(result, Formatting.Indented));
                Console.WriteLine($"Saved partial parse to {outputFile}");
                
                // Also create a hex dump for analysis
                CreateHexDump(bytes, Path.Combine(outputPath, "i12_hexdump.txt"), 1000);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error parsing: {ex.Message}");
            }
        }
        
        private static List<string> ExtractArchetypeNames(byte[] bytes, int startPos)
        {
            var names = new List<string>();
            
            // Look for archetype names in the binary
            // Based on hex dump, we can see "Blaster" at position 0x55
            var searchStrings = new[] { "Blaster", "Controller", "Defender", "Scrapper", "Tanker", "Brute", "Stalker", "Mastermind", "Dominator", "Corruptor" };
            
            foreach (var searchStr in searchStrings)
            {
                var searchBytes = Encoding.UTF8.GetBytes(searchStr);
                var index = IndexOf(bytes, searchBytes, startPos);
                if (index >= 0)
                {
                    names.Add(searchStr);
                    Console.WriteLine($"Found archetype: {searchStr} at position 0x{index:X}");
                }
            }
            
            return names;
        }
        
        private static int IndexOf(byte[] haystack, byte[] needle, int start = 0)
        {
            for (int i = start; i <= haystack.Length - needle.Length; i++)
            {
                bool found = true;
                for (int j = 0; j < needle.Length; j++)
                {
                    if (haystack[i + j] != needle[j])
                    {
                        found = false;
                        break;
                    }
                }
                if (found) return i;
            }
            return -1;
        }
        
        private static void CreateHexDump(byte[] bytes, string outputFile, int maxLines)
        {
            using var writer = new StreamWriter(outputFile);
            var bytesPerLine = 16;
            var lines = Math.Min(maxLines, (bytes.Length + bytesPerLine - 1) / bytesPerLine);
            
            for (int line = 0; line < lines; line++)
            {
                var offset = line * bytesPerLine;
                writer.Write($"{offset:X8}: ");
                
                // Hex bytes
                for (int i = 0; i < bytesPerLine; i++)
                {
                    if (offset + i < bytes.Length)
                    {
                        writer.Write($"{bytes[offset + i]:X2} ");
                    }
                    else
                    {
                        writer.Write("   ");
                    }
                }
                
                writer.Write(" ");
                
                // ASCII representation
                for (int i = 0; i < bytesPerLine; i++)
                {
                    if (offset + i < bytes.Length)
                    {
                        var b = bytes[offset + i];
                        writer.Write(b >= 32 && b < 127 ? (char)b : '.');
                    }
                }
                
                writer.WriteLine();
            }
            
            if (lines < (bytes.Length + bytesPerLine - 1) / bytesPerLine)
            {
                writer.WriteLine($"... ({bytes.Length - lines * bytesPerLine} more bytes)");
            }
        }
    }
}