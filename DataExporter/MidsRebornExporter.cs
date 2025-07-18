using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;

#if MIDSREBORN
using Mids_Reborn.Core;
using Mids_Reborn.Core.Base.Data_Classes;
using Mids_Reborn.Core.Base.Master_Classes;
using Mids_Reborn.Core.Utils;
#endif

namespace DataExporter
{
    public class MidsRebornExporter
    {
        private readonly string _inputPath;
        private readonly string _outputPath;

        public MidsRebornExporter(string inputPath, string outputPath)
        {
            _inputPath = inputPath;
            _outputPath = outputPath;
        }

        public void Export()
        {
#if MIDSREBORN
            try
            {
                Console.WriteLine("=== MidsReborn MHD to JSON Export ===");
                Console.WriteLine($"Input path: {_inputPath}");
                Console.WriteLine($"Output path: {_outputPath}");
                Console.WriteLine();

                // Step 1: Initialize Configuration
                Console.WriteLine("Initializing MidsReborn configuration...");
                InitializeConfiguration();

                // Step 2: Load MHD Data Files
                Console.WriteLine("\nLoading MHD data files...");
                if (!LoadAllData(_inputPath))
                {
                    Console.WriteLine("ERROR: Failed to load MHD data files");
                    return;
                }

                // Step 3: Export to JSON
                Console.WriteLine("\nExporting to JSON...");
                ExportToJson();

                Console.WriteLine("\n=== Export Complete! ===");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"ERROR during MidsReborn export: {ex.Message}");
                Console.WriteLine($"Stack trace: {ex.StackTrace}");
            }
#else
            Console.WriteLine("MidsReborn is not enabled. To enable:");
            Console.WriteLine("1. Uncomment the MidsReborn reference in DataExporter.csproj");
            Console.WriteLine("2. Add <DefineConstants>MIDSREBORN</DefineConstants> to the PropertyGroup");
            Console.WriteLine("3. Rebuild the project");
#endif
        }

#if MIDSREBORN
        private void InitializeConfiguration()
        {
            try
            {
                // Initialize ConfigData without UI
                ConfigData.Initialize();
                
                // Set the data path if needed
                if (ConfigData.Current != null)
                {
                    ConfigData.Current.DataPath = _inputPath;
                    Console.WriteLine($"Configuration initialized with data path: {_inputPath}");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Warning: Could not fully initialize configuration: {ex.Message}");
                Console.WriteLine("Proceeding with default configuration...");
            }
        }

        private bool LoadAllData(string dataPath)
        {
            try
            {
                // Initialize the database
                DatabaseAPI.Database = new Database();
                
                // Load server data (if available)
                Console.Write("Loading server data... ");
                try
                {
                    DatabaseAPI.LoadServerData(dataPath);
                    Console.WriteLine("OK");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Skipped (not critical): {ex.Message}");
                }

                // Load attribute modifiers
                Console.Write("Loading attribute modifiers... ");
                DatabaseAPI.Database.AttribMods = new Modifiers();
                DatabaseAPI.Database.AttribMods.Load(dataPath);
                Console.WriteLine("OK");

                // Load type grades
                Console.Write("Loading type grades... ");
                DatabaseAPI.LoadTypeGrades(dataPath);
                Console.WriteLine("OK");

                // Load level tables
                Console.Write("Loading level tables... ");
                DatabaseAPI.LoadLevelsDatabase(dataPath);
                Console.WriteLine("OK");

                // Load main database (I12.mhd)
                Console.Write("Loading main database (I12.mhd)... ");
                DatabaseAPI.LoadMainDatabase(dataPath);
                Console.WriteLine($"OK - Loaded {DatabaseAPI.Database.Power.Length} powers");

                // Load math tables
                Console.Write("Loading math tables... ");
                DatabaseAPI.LoadMaths(dataPath);
                Console.WriteLine("OK");

                // Load effect IDs
                Console.Write("Loading effect IDs... ");
                DatabaseAPI.LoadEffectIdsDatabase(dataPath);
                Console.WriteLine("OK");

                // Load enhancement classes
                Console.Write("Loading enhancement classes... ");
                DatabaseAPI.LoadEnhancementClasses(dataPath);
                Console.WriteLine("OK");

                // Load enhancement database
                Console.Write("Loading enhancement database... ");
                DatabaseAPI.LoadEnhancementDb(dataPath);
                Console.WriteLine($"OK - Loaded {DatabaseAPI.Database.Enhancements.Length} enhancements");

                // Load origins
                Console.Write("Loading origins... ");
                DatabaseAPI.LoadOrigins(dataPath);
                Console.WriteLine("OK");

                // Load salvage
                Console.Write("Loading salvage... ");
                DatabaseAPI.LoadSalvage(dataPath);
                Console.WriteLine($"OK - Loaded {DatabaseAPI.Database.Salvage.Length} salvage items");

                // Load recipes
                Console.Write("Loading recipes... ");
                DatabaseAPI.LoadRecipes(dataPath);
                Console.WriteLine($"OK - Loaded {DatabaseAPI.Database.Recipes.Length} recipes");

                // Post-loading setup
                Console.Write("Performing post-load setup... ");
                DatabaseAPI.FillGroupArray();
                DatabaseAPI.AssignSetBonusIndexes();
                DatabaseAPI.AssignRecipeIDs();
                Console.WriteLine("OK");

                // Display summary
                Console.WriteLine("\n=== Data Loading Summary ===");
                Console.WriteLine($"Archetypes: {DatabaseAPI.Database.Classes?.Length ?? 0}");
                Console.WriteLine($"Powersets: {DatabaseAPI.Database.Powersets?.Length ?? 0}");
                Console.WriteLine($"Powers: {DatabaseAPI.Database.Power?.Length ?? 0}");
                Console.WriteLine($"Enhancements: {DatabaseAPI.Database.Enhancements?.Length ?? 0}");
                Console.WriteLine($"Enhancement Sets: {DatabaseAPI.Database.EnhancementSets?.Length ?? 0}");
                Console.WriteLine($"Recipes: {DatabaseAPI.Database.Recipes?.Length ?? 0}");
                Console.WriteLine($"Salvage: {DatabaseAPI.Database.Salvage?.Length ?? 0}");

                return true;
            }
            catch (Exception ex)
            {
                Console.WriteLine($"FAILED: {ex.Message}");
                return false;
            }
        }

        private void ExportToJson()
        {
            try
            {
                // Create output directory if it doesn't exist
                Directory.CreateDirectory(_outputPath);

                // Option 1: Use MidsReborn's built-in JSON export
                Console.WriteLine("\nAttempting to use MidsReborn's built-in JSON export...");
                var serializer = Serializer.GetSerializer();
                
                // Try to save using the built-in method
                string exportPath = Path.Combine(_outputPath, "midsreborn_export.json");
                if (DatabaseAPI.SaveJsonDatabase(serializer))
                {
                    Console.WriteLine("Built-in export successful!");
                    // The built-in export creates a compressed archive
                    // You may need to extract it
                }
                else
                {
                    Console.WriteLine("Built-in export failed, using custom export...");
                    CustomExportToJson();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Built-in export error: {ex.Message}");
                Console.WriteLine("Falling back to custom export...");
                CustomExportToJson();
            }
        }

        private void CustomExportToJson()
        {
            // Export individual data types
            var jsonSettings = new JsonSerializerSettings
            {
                Formatting = Formatting.Indented,
                ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
                TypeNameHandling = TypeNameHandling.Auto
            };

            // Export archetypes
            Console.Write("Exporting archetypes... ");
            File.WriteAllText(
                Path.Combine(_outputPath, "archetypes.json"),
                JsonConvert.SerializeObject(DatabaseAPI.Database.Classes, jsonSettings)
            );
            Console.WriteLine("OK");

            // Export powersets
            Console.Write("Exporting powersets... ");
            File.WriteAllText(
                Path.Combine(_outputPath, "powersets.json"),
                JsonConvert.SerializeObject(DatabaseAPI.Database.Powersets, jsonSettings)
            );
            Console.WriteLine("OK");

            // Export powers
            Console.Write("Exporting powers... ");
            File.WriteAllText(
                Path.Combine(_outputPath, "powers.json"),
                JsonConvert.SerializeObject(DatabaseAPI.Database.Power, jsonSettings)
            );
            Console.WriteLine("OK");

            // Export enhancements
            Console.Write("Exporting enhancements... ");
            File.WriteAllText(
                Path.Combine(_outputPath, "enhancements.json"),
                JsonConvert.SerializeObject(DatabaseAPI.Database.Enhancements, jsonSettings)
            );
            Console.WriteLine("OK");

            // Export enhancement sets
            Console.Write("Exporting enhancement sets... ");
            File.WriteAllText(
                Path.Combine(_outputPath, "enhancement_sets.json"),
                JsonConvert.SerializeObject(DatabaseAPI.Database.EnhancementSets, jsonSettings)
            );
            Console.WriteLine("OK");

            // Export recipes
            Console.Write("Exporting recipes... ");
            File.WriteAllText(
                Path.Combine(_outputPath, "recipes.json"),
                JsonConvert.SerializeObject(DatabaseAPI.Database.Recipes, jsonSettings)
            );
            Console.WriteLine("OK");

            // Export salvage
            Console.Write("Exporting salvage... ");
            File.WriteAllText(
                Path.Combine(_outputPath, "salvage.json"),
                JsonConvert.SerializeObject(DatabaseAPI.Database.Salvage, jsonSettings)
            );
            Console.WriteLine("OK");

            Console.WriteLine($"\nAll data exported to: {_outputPath}");
        }
#endif
    }
}