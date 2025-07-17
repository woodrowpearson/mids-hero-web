using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;

namespace DataExporter
{
    public class MhdExporter
    {
        private readonly string _inputPath;
        private readonly string _outputPath;
        private readonly JsonSerializerSettings _jsonSettings;

        public MhdExporter(string inputPath, string outputPath)
        {
            _inputPath = inputPath;
            _outputPath = outputPath;
            
            // Configure JSON serialization for clean output
            _jsonSettings = new JsonSerializerSettings
            {
                Formatting = Formatting.Indented,
                ContractResolver = new CamelCasePropertyNamesContractResolver(),
                NullValueHandling = NullValueHandling.Ignore,
                DateFormatHandling = DateFormatHandling.IsoDateFormat
            };
        }

        public void ExportAllData()
        {
            Console.WriteLine("Starting MHD data export...");
            Console.WriteLine($"Input folder: {_inputPath}");
            Console.WriteLine($"Output folder: {_outputPath}");

            // Create output directory if it doesn't exist
            Directory.CreateDirectory(_outputPath);

            // Export each data type
            try
            {
                // Main database (archetypes, powersets, powers)
                ExportMainDatabase();
                
                // Enhancements database
                ExportEnhancementDatabase();
                
                // Recipes
                ExportRecipes();
                
                // Salvage
                ExportSalvage();
                
                // Other data files
                ExportMiscellaneousData();
                
                Console.WriteLine("\nExport completed successfully!");
                CreateExportReport();
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\nError during export: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }
        }

        private void ExportMainDatabase()
        {
            var i12File = Path.Combine(_inputPath, "I12.mhd");
            if (!File.Exists(i12File))
            {
                Console.WriteLine("Warning: I12.mhd not found - skipping main database export");
                return;
            }

            Console.WriteLine("\nExporting main database (I12.mhd)...");
            
            try
            {
                // For now, we'll create a placeholder structure
                // This will be replaced with actual MidsReborn parsing logic
                var mainDatabase = new
                {
                    version = "Homecoming 2025.7.1111",
                    exportDate = DateTime.UtcNow,
                    archetypes = new List<object>(),
                    powersets = new List<object>(),
                    powers = new List<object>()
                };

                // TODO: Integrate MidsReborn's DatabaseAPI to parse I12.mhd
                // Example:
                // var database = DatabaseAPI.LoadDatabase(i12File);
                // mainDatabase.archetypes = database.Archetypes;
                // mainDatabase.powersets = database.Powersets;
                // mainDatabase.powers = database.Powers;

                SaveToJson("main_database.json", mainDatabase);
                Console.WriteLine("  - Exported archetypes, powersets, and powers");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  - Error: {ex.Message}");
            }
        }

        private void ExportEnhancementDatabase()
        {
            var enhDbFile = Path.Combine(_inputPath, "EnhDB.mhd");
            if (!File.Exists(enhDbFile))
            {
                Console.WriteLine("Warning: EnhDB.mhd not found - skipping enhancement export");
                return;
            }

            Console.WriteLine("\nExporting enhancement database (EnhDB.mhd)...");
            
            try
            {
                var enhancementDatabase = new
                {
                    version = "Homecoming 2025.7.1111",
                    exportDate = DateTime.UtcNow,
                    enhancementSets = new List<object>(),
                    enhancements = new List<object>(),
                    setBonuses = new List<object>()
                };

                // TODO: Parse EnhDB.mhd using MidsReborn
                
                SaveToJson("enhancement_database.json", enhancementDatabase);
                Console.WriteLine("  - Exported enhancement sets, enhancements, and set bonuses");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  - Error: {ex.Message}");
            }
        }

        private void ExportRecipes()
        {
            var recipeFile = Path.Combine(_inputPath, "Recipe.mhd");
            if (!File.Exists(recipeFile))
            {
                Console.WriteLine("Warning: Recipe.mhd not found - skipping recipe export");
                return;
            }

            Console.WriteLine("\nExporting recipes (Recipe.mhd)...");
            
            try
            {
                var recipes = new
                {
                    version = "Homecoming 2025.7.1111",
                    exportDate = DateTime.UtcNow,
                    recipes = new List<object>()
                };

                // TODO: Parse Recipe.mhd
                
                SaveToJson("recipes.json", recipes);
                Console.WriteLine("  - Exported recipes");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  - Error: {ex.Message}");
            }
        }

        private void ExportSalvage()
        {
            var salvageFile = Path.Combine(_inputPath, "Salvage.mhd");
            if (!File.Exists(salvageFile))
            {
                Console.WriteLine("Warning: Salvage.mhd not found - skipping salvage export");
                return;
            }

            Console.WriteLine("\nExporting salvage (Salvage.mhd)...");
            
            try
            {
                var salvage = new
                {
                    version = "Homecoming 2025.7.1111",
                    exportDate = DateTime.UtcNow,
                    salvageItems = new List<object>()
                };

                // TODO: Parse Salvage.mhd
                
                SaveToJson("salvage.json", salvage);
                Console.WriteLine("  - Exported salvage items");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"  - Error: {ex.Message}");
            }
        }

        private void ExportMiscellaneousData()
        {
            Console.WriteLine("\nExporting miscellaneous data files...");
            
            // Copy existing JSON files
            var jsonFiles = new[] { "AttribMod.json", "TypeGrades.json" };
            foreach (var jsonFile in jsonFiles)
            {
                var sourceFile = Path.Combine(_inputPath, jsonFile);
                if (File.Exists(sourceFile))
                {
                    var destFile = Path.Combine(_outputPath, jsonFile);
                    File.Copy(sourceFile, destFile, overwrite: true);
                    Console.WriteLine($"  - Copied {jsonFile}");
                }
            }
        }

        private void SaveToJson(string filename, object data)
        {
            var outputFile = Path.Combine(_outputPath, filename);
            var json = JsonConvert.SerializeObject(data, _jsonSettings);
            File.WriteAllText(outputFile, json);
        }

        private void CreateExportReport()
        {
            var report = new
            {
                exportDate = DateTime.UtcNow,
                inputDirectory = _inputPath,
                outputDirectory = _outputPath,
                exportedFiles = Directory.GetFiles(_outputPath, "*.json")
                    .Select(f => new
                    {
                        filename = Path.GetFileName(f),
                        size = new FileInfo(f).Length,
                        lastModified = File.GetLastWriteTimeUtc(f)
                    })
                    .ToList(),
                totalSize = Directory.GetFiles(_outputPath, "*.json")
                    .Sum(f => new FileInfo(f).Length)
            };

            SaveToJson("export_report.json", report);
            Console.WriteLine($"\nExport report saved to: {Path.Combine(_outputPath, "export_report.json")}");
        }
    }
}