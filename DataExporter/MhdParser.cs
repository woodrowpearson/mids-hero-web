using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace DataExporter
{
    /// <summary>
    /// Parser for MHD (Mids Hero Designer) binary files
    /// </summary>
    public class MhdParser
    {
        private readonly string _outputPath;

        public MhdParser(string outputPath)
        {
            _outputPath = outputPath;
        }

        public void ParseMhdFiles(string dataPath)
        {
            Console.WriteLine("\n=== MHD Parser - Structured Data Extraction ===\n");

            var mhdFiles = Directory.GetFiles(dataPath, "*.mhd");
            foreach (var mhdFile in mhdFiles)
            {
                var fileName = Path.GetFileName(mhdFile);
                Console.WriteLine($"Parsing: {fileName}");
                
                try
                {
                    ParseMhdFile(mhdFile);
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"  Error: {ex.Message}");
                }
            }
        }

        private void ParseMhdFile(string filePath)
        {
            var fileName = Path.GetFileNameWithoutExtension(filePath);
            var outputFile = Path.Combine(_outputPath, $"{fileName}.json");

            using (var stream = File.OpenRead(filePath))
            using (var reader = new BinaryReader(stream))
            {
                // Read header
                var header = ReadString(reader, 35); // "Mids' Hero Designer Database MK II"
                if (!header.StartsWith("Mids' Hero Designer"))
                {
                    Console.WriteLine($"  Warning: Invalid header - {header}");
                }

                // Based on the file name, parse differently
                if (fileName == "I9" || fileName == "I12")
                {
                    ParseArchetypesAndPowersets(reader, outputFile);
                }
                else if (fileName == "EnhDB")
                {
                    ParseEnhancements(reader, outputFile);
                }
                else if (fileName == "Recipe")
                {
                    ParseRecipes(reader, outputFile);
                }
                else if (fileName == "Salvage")
                {
                    ParseSalvage(reader, outputFile);
                }
                else
                {
                    // Generic extraction for other files
                    ExtractAllData(reader, outputFile);
                }
            }
        }

        private void ParseArchetypesAndPowersets(BinaryReader reader, string outputFile)
        {
            var result = new JObject();
            var archetypes = new JArray();
            var powersets = new JArray();
            var powers = new JArray();

            // Skip to data sections
            string line;
            while ((line = ReadLine(reader)) != null)
            {
                if (line.StartsWith("BEGIN:ARCHETYPES"))
                {
                    Console.WriteLine("  Found ARCHETYPES section");
                    archetypes = ParseArchetypesSection(reader);
                }
                else if (line.StartsWith("BEGIN:POWERSETS"))
                {
                    Console.WriteLine("  Found POWERSETS section");
                    powersets = ParsePowersetsSection(reader);
                }
                else if (line.StartsWith("BEGIN:POWERS"))
                {
                    Console.WriteLine("  Found POWERS section");
                    powers = ParsePowersSection(reader);
                }
            }

            result["archetypes"] = archetypes;
            result["powersets"] = powersets;
            result["powers"] = powers;

            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
            Console.WriteLine($"  Saved: {Path.GetFileName(outputFile)}");
        }

        private JArray ParseArchetypesSection(BinaryReader reader)
        {
            var archetypes = new JArray();
            var currentArchetype = new JObject();
            var origins = new JArray();

            string line;
            while ((line = ReadLine(reader)) != null && !line.StartsWith("BEGIN:"))
            {
                // Check if this is an origin
                if (line == "Magic" || line == "Mutation" || line == "Natural" || 
                    line == "Science" || line == "Technology")
                {
                    origins.Add(line);
                }
                else if (!string.IsNullOrWhiteSpace(line))
                {
                    // This is a new archetype
                    if (currentArchetype.Count > 0)
                    {
                        currentArchetype["origins"] = origins;
                        archetypes.Add(currentArchetype);
                        origins = new JArray();
                    }
                    currentArchetype = new JObject();
                    currentArchetype["name"] = line;
                }
            }

            // Add the last archetype
            if (currentArchetype.Count > 0)
            {
                currentArchetype["origins"] = origins;
                archetypes.Add(currentArchetype);
            }

            return archetypes;
        }

        private JArray ParsePowersetsSection(BinaryReader reader)
        {
            var powersets = new JArray();
            string name = null;

            string line;
            while ((line = ReadLine(reader)) != null && !line.StartsWith("BEGIN:"))
            {
                if (line.EndsWith(".png"))
                {
                    // This is an icon file
                    if (name != null)
                    {
                        var powerset = new JObject();
                        powerset["name"] = name;
                        powerset["icon"] = line;
                        powersets.Add(powerset);
                        name = null;
                    }
                }
                else if (!string.IsNullOrWhiteSpace(line))
                {
                    name = line;
                }
            }

            return powersets;
        }

        private JArray ParsePowersSection(BinaryReader reader)
        {
            // This would be more complex - powers have many attributes
            // For now, just collect power names
            var powers = new JArray();
            
            string line;
            while ((line = ReadLine(reader)) != null && !line.StartsWith("BEGIN:"))
            {
                if (!string.IsNullOrWhiteSpace(line) && !line.Contains(".png"))
                {
                    powers.Add(line);
                }
            }

            return powers;
        }

        private void ParseEnhancements(BinaryReader reader, string outputFile)
        {
            var enhancements = new JArray();
            // Enhancement parsing logic would go here
            var result = new JObject();
            result["enhancements"] = enhancements;
            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
        }

        private void ParseRecipes(BinaryReader reader, string outputFile)
        {
            var recipes = new JArray();
            // Recipe parsing logic would go here
            var result = new JObject();
            result["recipes"] = recipes;
            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
        }

        private void ParseSalvage(BinaryReader reader, string outputFile)
        {
            var salvage = new JArray();
            // Salvage parsing logic would go here
            var result = new JObject();
            result["salvage"] = salvage;
            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
        }

        private void ExtractAllData(BinaryReader reader, string outputFile)
        {
            var data = new JArray();
            string line;
            while ((line = ReadLine(reader)) != null)
            {
                if (!string.IsNullOrWhiteSpace(line))
                {
                    data.Add(line);
                }
            }

            var result = new JObject();
            result["data"] = data;
            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
        }

        private string ReadString(BinaryReader reader, int maxLength)
        {
            var sb = new StringBuilder();
            for (int i = 0; i < maxLength && reader.BaseStream.Position < reader.BaseStream.Length; i++)
            {
                var b = reader.ReadByte();
                if (b == 0) break;
                if (b >= 32 && b <= 126) sb.Append((char)b);
            }
            return sb.ToString();
        }

        private string ReadLine(BinaryReader reader)
        {
            if (reader.BaseStream.Position >= reader.BaseStream.Length)
                return null;

            var sb = new StringBuilder();
            byte b;
            while (reader.BaseStream.Position < reader.BaseStream.Length)
            {
                b = reader.ReadByte();
                if (b == 0 || b == 10 || b == 13) // null, LF, or CR
                {
                    if (sb.Length > 0) break;
                    continue;
                }
                if (b >= 32 && b <= 126) sb.Append((char)b);
                else if (sb.Length > 0) break; // End on non-printable if we have data
            }

            return sb.Length > 0 ? sb.ToString() : null;
        }
    }
}