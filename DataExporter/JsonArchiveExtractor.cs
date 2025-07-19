using System;
using System.IO;
using System.IO.Compression;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace DataExporter
{
    /// <summary>
    /// Handles extraction and organization of JSON archives created by MidsReborn
    /// </summary>
    public static class JsonArchiveExtractor
    {
        /// <summary>
        /// Extracts a compressed JSON archive if it exists
        /// </summary>
        public static bool ExtractArchive(string archivePath, string outputPath)
        {
            try
            {
                if (!File.Exists(archivePath))
                {
                    Console.WriteLine($"Archive not found: {archivePath}");
                    return false;
                }

                // Check if it's a ZIP archive
                if (IsZipFile(archivePath))
                {
                    Console.WriteLine("Extracting ZIP archive...");
                    ExtractZipArchive(archivePath, outputPath);
                    return true;
                }

                // Check if it's a JSON file that might contain embedded data
                if (archivePath.EndsWith(".json", StringComparison.OrdinalIgnoreCase))
                {
                    Console.WriteLine("Processing JSON file...");
                    return ProcessJsonFile(archivePath, outputPath);
                }

                Console.WriteLine("Unknown archive format");
                return false;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error extracting archive: {ex.Message}");
                return false;
            }
        }

        private static bool IsZipFile(string filePath)
        {
            try
            {
                using (var file = File.OpenRead(filePath))
                {
                    // ZIP files start with PK (0x504B)
                    return file.ReadByte() == 0x50 && file.ReadByte() == 0x4B;
                }
            }
            catch
            {
                return false;
            }
        }

        private static void ExtractZipArchive(string archivePath, string outputPath)
        {
            Directory.CreateDirectory(outputPath);
            ZipFile.ExtractToDirectory(archivePath, outputPath, true);
            Console.WriteLine($"Extracted to: {outputPath}");

            // Organize extracted files
            OrganizeExtractedFiles(outputPath);
        }

        private static bool ProcessJsonFile(string jsonPath, string outputPath)
        {
            try
            {
                var content = File.ReadAllText(jsonPath);
                var json = JToken.Parse(content);

                Directory.CreateDirectory(outputPath);

                // Check if it's a single object with multiple data types
                if (json is JObject obj)
                {
                    foreach (var property in obj.Properties())
                    {
                        var fileName = $"{property.Name.ToLowerInvariant()}.json";
                        var filePath = Path.Combine(outputPath, fileName);
                        
                        File.WriteAllText(filePath, property.Value.ToString(Formatting.Indented));
                        Console.WriteLine($"Extracted: {fileName}");
                    }
                    return true;
                }

                // If it's not in expected format, copy as-is
                File.Copy(jsonPath, Path.Combine(outputPath, Path.GetFileName(jsonPath)), true);
                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing JSON: {ex.Message}");
                return false;
            }
        }

        private static void OrganizeExtractedFiles(string outputPath)
        {
            // Map common file patterns to standard names
            var fileMapping = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
            {
                { "Archetype", "archetypes.json" },
                { "Classes", "archetypes.json" },
                { "Powerset", "powersets.json" },
                { "Power", "powers.json" },
                { "Enhancement", "enhancements.json" },
                { "EnhancementSet", "enhancement_sets.json" },
                { "Recipe", "recipes.json" },
                { "Salvage", "salvage.json" }
            };

            var files = Directory.GetFiles(outputPath, "*.json");
            foreach (var file in files)
            {
                var fileName = Path.GetFileNameWithoutExtension(file);
                
                // Find matching pattern
                foreach (var mapping in fileMapping)
                {
                    if (fileName.Contains(mapping.Key, StringComparison.OrdinalIgnoreCase))
                    {
                        var newPath = Path.Combine(outputPath, mapping.Value);
                        if (!File.Exists(newPath))
                        {
                            File.Move(file, newPath);
                            Console.WriteLine($"Renamed: {Path.GetFileName(file)} -> {mapping.Value}");
                        }
                        break;
                    }
                }
            }
        }
    }
}