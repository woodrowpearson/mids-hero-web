using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace DataExporter
{
    /// <summary>
    /// Parses the extracted text files into structured JSON
    /// </summary>
    public class TextToJsonParser
    {
        private readonly string _outputPath;

        public TextToJsonParser(string outputPath)
        {
            _outputPath = outputPath;
        }

        public void ParseExtractedFiles()
        {
            Console.WriteLine("\n=== Text to JSON Parser ===\n");

            // Parse I9 extracted file
            var i9File = Path.Combine(_outputPath, "I9_extracted.txt");
            if (File.Exists(i9File))
            {
                Console.WriteLine("Parsing I9_extracted.txt...");
                ParseI9File(i9File);
            }

            // Parse I12 extracted file
            var i12File = Path.Combine(_outputPath, "I12_extracted.txt");
            if (File.Exists(i12File))
            {
                Console.WriteLine("Parsing I12_extracted.txt...");
                ParseI12File(i12File);
            }

            // Parse other files
            ParseEnhancementsFile();
            ParseSalvageFile();
            ParseRecipeFile();
        }

        private void ParseI9File(string filePath)
        {
            var lines = File.ReadAllLines(filePath);
            var result = new JObject();
            var archetypes = new JArray();
            var powersets = new JArray();
            var powers = new JArray();

            var currentSection = "";
            var currentArchetype = new JObject();
            var currentOrigins = new JArray();
            var currentPowerset = new JObject();

            for (int i = 0; i < lines.Length; i++)
            {
                var line = lines[i].Trim();

                if (line == "BEGIN:ARCHETYPES")
                {
                    currentSection = "ARCHETYPES";
                    continue;
                }
                else if (line == "BEGIN:POWERSETS")
                {
                    // Save last archetype if any
                    if (currentArchetype.Count > 0)
                    {
                        currentArchetype["origins"] = currentOrigins;
                        archetypes.Add(currentArchetype);
                    }
                    currentSection = "POWERSETS";
                    continue;
                }
                else if (line == "BEGIN:POWERS")
                {
                    // Save last powerset if any
                    if (currentPowerset.Count > 0)
                    {
                        powersets.Add(currentPowerset);
                    }
                    currentSection = "POWERS";
                    continue;
                }

                // Process based on current section
                switch (currentSection)
                {
                    case "ARCHETYPES":
                        if (IsOrigin(line))
                        {
                            currentOrigins.Add(line);
                        }
                        else if (!string.IsNullOrWhiteSpace(line) && IsArchetypeName(line))
                        {
                            // Save previous archetype
                            if (currentArchetype.Count > 0)
                            {
                                currentArchetype["origins"] = currentOrigins;
                                archetypes.Add(currentArchetype);
                            }
                            // Start new archetype
                            currentArchetype = new JObject { ["name"] = line };
                            currentOrigins = new JArray();
                        }
                        break;

                    case "POWERSETS":
                        if (line.EndsWith(".png"))
                        {
                            currentPowerset["icon"] = line;
                            powersets.Add(currentPowerset);
                            currentPowerset = new JObject();
                        }
                        else if (!string.IsNullOrWhiteSpace(line) && !line.Contains("BEGIN:"))
                        {
                            currentPowerset["name"] = line;
                        }
                        break;

                    case "POWERS":
                        if (!string.IsNullOrWhiteSpace(line) && !line.Contains(".png"))
                        {
                            powers.Add(line);
                        }
                        break;
                }
            }

            // Save last items
            if (currentArchetype.Count > 0)
            {
                currentArchetype["origins"] = currentOrigins;
                archetypes.Add(currentArchetype);
            }
            if (currentPowerset.Count > 0)
            {
                powersets.Add(currentPowerset);
            }

            result["archetypes"] = archetypes;
            result["powersets"] = powersets;
            result["powers"] = powers;

            var outputFile = Path.Combine(_outputPath, "I9_structured.json");
            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
            Console.WriteLine($"  Created: I9_structured.json");
            Console.WriteLine($"  - {archetypes.Count} archetypes");
            Console.WriteLine($"  - {powersets.Count} powersets");
            Console.WriteLine($"  - {powers.Count} powers");
        }

        private void ParseI12File(string filePath)
        {
            // I12 is much larger and contains more detailed power data
            // For now, we'll create a similar structure
            var outputFile = Path.Combine(_outputPath, "I12_structured.json");
            Console.WriteLine("  I12 file is very large - simplified parsing for now");
            
            // Create a summary
            var lines = File.ReadAllLines(filePath);
            var summary = new JObject
            {
                ["totalLines"] = lines.Length,
                ["fileSize"] = new FileInfo(filePath).Length,
                ["description"] = "Full power database - requires deeper parsing"
            };
            
            File.WriteAllText(outputFile, summary.ToString(Formatting.Indented));
        }

        private void ParseEnhancementsFile()
        {
            var enhFile = Path.Combine(_outputPath, "EnhDB_extracted.txt");
            if (!File.Exists(enhFile)) return;

            Console.WriteLine("Parsing EnhDB_extracted.txt...");
            var lines = File.ReadAllLines(enhFile);
            var enhancements = new JArray();

            foreach (var line in lines)
            {
                if (!string.IsNullOrWhiteSpace(line) && 
                    !line.Contains("Mids") && 
                    line.Length > 2)
                {
                    enhancements.Add(line);
                }
            }

            var result = new JObject { ["enhancements"] = enhancements };
            var outputFile = Path.Combine(_outputPath, "enhancements.json");
            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
            Console.WriteLine($"  Created: enhancements.json ({enhancements.Count} items)");
        }

        private void ParseSalvageFile()
        {
            var salvageFile = Path.Combine(_outputPath, "Salvage_extracted.txt");
            if (!File.Exists(salvageFile)) return;

            Console.WriteLine("Parsing Salvage_extracted.txt...");
            var lines = File.ReadAllLines(salvageFile);
            var salvage = new JArray();

            foreach (var line in lines)
            {
                if (!string.IsNullOrWhiteSpace(line) && 
                    !line.Contains("Database") && 
                    line.Length > 2)
                {
                    salvage.Add(line);
                }
            }

            var result = new JObject { ["salvage"] = salvage };
            var outputFile = Path.Combine(_outputPath, "salvage.json");
            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
            Console.WriteLine($"  Created: salvage.json ({salvage.Count} items)");
        }

        private void ParseRecipeFile()
        {
            var recipeFile = Path.Combine(_outputPath, "Recipe_extracted.txt");
            if (!File.Exists(recipeFile)) return;

            Console.WriteLine("Parsing Recipe_extracted.txt...");
            var lines = File.ReadAllLines(recipeFile);
            
            // Recipes are complex - for now just count them
            var recipeCount = lines.Count(l => !string.IsNullOrWhiteSpace(l) && l.Length > 5);
            
            var result = new JObject 
            { 
                ["totalRecipes"] = recipeCount,
                ["description"] = "Recipe data - requires structured parsing"
            };
            
            var outputFile = Path.Combine(_outputPath, "recipes.json");
            File.WriteAllText(outputFile, result.ToString(Formatting.Indented));
            Console.WriteLine($"  Created: recipes.json ({recipeCount} potential recipes)");
        }

        private bool IsOrigin(string text)
        {
            var origins = new[] { "Magic", "Mutation", "Natural", "Science", "Technology" };
            return origins.Contains(text);
        }

        private bool IsArchetypeName(string text)
        {
            var archetypes = new[] 
            { 
                "Blaster", "Controller", "Defender", "Scrapper", "Tanker",
                "Peacebringer", "Warshade", "Brute", "Corruptor", "Dominator",
                "Mastermind", "Stalker", "Sentinel", "Arachnos Soldier", "Arachnos Widow"
            };
            return archetypes.Contains(text);
        }
    }
}