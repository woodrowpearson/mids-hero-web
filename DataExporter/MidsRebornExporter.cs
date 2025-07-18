using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using Newtonsoft.Json;

#if MIDSREBORN
using MidsReborn.Core;
using MidsReborn.Core.Base.Master_Classes;
using MidsReborn.Core.Import;
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
                Console.WriteLine("Loading MidsReborn database...");
                
                // Initialize MidsReborn database
                DatabaseAPI.LoadMainDatabase(Path.Combine(_inputPath, "I12.mhd"));
                DatabaseAPI.LoadEnhancementDb(Path.Combine(_inputPath, "EnhDB.mhd"));
                DatabaseAPI.LoadRecipeDb(Path.Combine(_inputPath, "Recipe.mhd"));
                DatabaseAPI.LoadSalvageDb(Path.Combine(_inputPath, "Salvage.mhd"));

                // Export Archetypes
                ExportArchetypes();
                
                // Export Powersets
                ExportPowersets();
                
                // Export Powers
                ExportPowers();
                
                // Export Enhancements
                ExportEnhancements();
                
                // Export Enhancement Sets
                ExportEnhancementSets();
                
                // Export Recipes
                ExportRecipes();
                
                // Export Salvage
                ExportSalvage();
                
                Console.WriteLine("\nExport complete!");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error during MidsReborn export: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }
#else
            Console.WriteLine("MidsReborn is not enabled. To enable:");
            Console.WriteLine("1. Uncomment the MidsReborn reference in DataExporter.csproj");
            Console.WriteLine("2. Add <DefineConstants>MIDSREBORN</DefineConstants> to the PropertyGroup");
            Console.WriteLine("3. Rebuild the project");
#endif
        }

#if MIDSREBORN
        private void ExportArchetypes()
        {
            Console.Write("Exporting archetypes... ");
            var archetypes = DatabaseAPI.Database.Classes
                .Select((arch, idx) => new
                {
                    id = idx + 1,
                    name = arch.ClassName,
                    display_name = arch.DisplayName,
                    description = arch.DescLong,
                    primary_group = arch.PrimaryGroup,
                    secondary_group = arch.SecondaryGroup,
                    hit_points_base = arch.Hitpoints,
                    hit_points_max = arch.HPCap
                })
                .ToList();
            
            var json = JsonConvert.SerializeObject(archetypes, Formatting.Indented);
            File.WriteAllText(Path.Combine(_outputPath, "archetypes.json"), json);
            Console.WriteLine($"Done! ({archetypes.Count} exported)");
        }

        private void ExportPowersets()
        {
            Console.Write("Exporting powersets... ");
            var powersets = DatabaseAPI.Database.Powersets
                .Select((ps, idx) => new
                {
                    id = idx + 1,
                    name = ps.SetName,
                    display_name = ps.DisplayName,
                    description = ps.Description,
                    archetype_id = ps.ATClass?.Length > 0 ? ps.ATClass[0] + 1 : (int?)null,
                    powerset_type = ps.SetType.ToString().ToLower()
                })
                .ToList();
            
            var json = JsonConvert.SerializeObject(powersets, Formatting.Indented);
            File.WriteAllText(Path.Combine(_outputPath, "powersets.json"), json);
            Console.WriteLine($"Done! ({powersets.Count} exported)");
        }

        private void ExportPowers()
        {
            Console.Write("Exporting powers... ");
            var powers = DatabaseAPI.Database.Power
                .Select((power, idx) => new
                {
                    id = idx + 1,
                    name = power.PowerName,
                    display_name = power.DisplayName,
                    description = power.DescLong,
                    powerset_id = power.PowerSetID >= 0 ? power.PowerSetID + 1 : (int?)null,
                    level_available = power.Level,
                    power_type = power.PowerType.ToString().ToLower(),
                    accuracy = power.Accuracy,
                    endurance_cost = power.EndCost,
                    recharge_time = power.RechargeTime,
                    activation_time = power.CastTime,
                    range_feet = power.Range
                })
                .ToList();
            
            var json = JsonConvert.SerializeObject(powers, Formatting.Indented);
            File.WriteAllText(Path.Combine(_outputPath, "powers.json"), json);
            Console.WriteLine($"Done! ({powers.Count} exported)");
        }

        private void ExportEnhancements()
        {
            Console.Write("Exporting enhancements... ");
            var enhancements = DatabaseAPI.Database.Enhancements
                .Select((enh, idx) => new
                {
                    id = idx + 1,
                    name = enh.Name,
                    display_name = enh.ShortName,
                    description = enh.Desc,
                    enhancement_type = enh.TypeID.ToString(),
                    set_id = enh.nIDSet >= 0 ? enh.nIDSet + 1 : (int?)null,
                    level_min = enh.LevelMin,
                    level_max = enh.LevelMax
                })
                .ToList();
            
            var json = JsonConvert.SerializeObject(enhancements, Formatting.Indented);
            File.WriteAllText(Path.Combine(_outputPath, "enhancements.json"), json);
            Console.WriteLine($"Done! ({enhancements.Count} exported)");
        }

        private void ExportEnhancementSets()
        {
            Console.Write("Exporting enhancement sets... ");
            var enhancementSets = DatabaseAPI.Database.EnhancementSets
                .Select((set, idx) => new
                {
                    id = idx + 1,
                    name = set.Uid,
                    display_name = set.DisplayName,
                    description = set.Desc,
                    min_level = set.LevelMin,
                    max_level = set.LevelMax
                })
                .ToList();
            
            var json = JsonConvert.SerializeObject(enhancementSets, Formatting.Indented);
            File.WriteAllText(Path.Combine(_outputPath, "enhancement_sets.json"), json);
            Console.WriteLine($"Done! ({enhancementSets.Count} exported)");
        }

        private void ExportRecipes()
        {
            Console.Write("Exporting recipes... ");
            var recipes = DatabaseAPI.Database.Recipes
                .Select((recipe, idx) => new
                {
                    id = idx + 1,
                    name = recipe.InternalName,
                    display_name = recipe.ExternalName,
                    enhancement_id = recipe.EnhIdx >= 0 ? recipe.EnhIdx + 1 : (int?)null,
                    rarity = recipe.Rarity.ToString()
                })
                .ToList();
            
            var json = JsonConvert.SerializeObject(recipes, Formatting.Indented);
            File.WriteAllText(Path.Combine(_outputPath, "recipes.json"), json);
            Console.WriteLine($"Done! ({recipes.Count} exported)");
        }

        private void ExportSalvage()
        {
            Console.Write("Exporting salvage... ");
            var salvage = DatabaseAPI.Database.Salvage
                .Select((salv, idx) => new
                {
                    id = idx + 1,
                    name = salv.InternalName,
                    display_name = salv.ExternalName,
                    description = salv.Description,
                    rarity = salv.Rarity.ToString(),
                    origin = salv.Origin.ToString(),
                    level_min = salv.LevelMin,
                    level_max = salv.LevelMax
                })
                .ToList();
            
            var json = JsonConvert.SerializeObject(salvage, Formatting.Indented);
            File.WriteAllText(Path.Combine(_outputPath, "salvage.json"), json);
            Console.WriteLine($"Done! ({salvage.Count} exported)");
        }
#endif
    }
}