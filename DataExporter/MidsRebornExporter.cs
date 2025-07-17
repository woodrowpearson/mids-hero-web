using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using Newtonsoft.Json;
using Newtonsoft.Json.Serialization;
using Mids_Reborn.Core;
using Mids_Reborn.Core.Base.Data_Classes;

namespace DataExporter
{
    public class MidsRebornExporter
    {
        private readonly string _dataPath;
        private readonly string _outputPath;
        private readonly JsonSerializerSettings _jsonSettings;

        public MidsRebornExporter(string dataPath, string outputPath)
        {
            _dataPath = dataPath;
            _outputPath = outputPath;
            
            _jsonSettings = new JsonSerializerSettings
            {
                Formatting = Formatting.Indented,
                ContractResolver = new CamelCasePropertyNamesContractResolver(),
                NullValueHandling = NullValueHandling.Ignore,
                ReferenceLoopHandling = ReferenceLoopHandling.Ignore
            };
        }

        public void ExportAllData()
        {
            Console.WriteLine("Starting MidsReborn data export...");
            Console.WriteLine($"Data path: {_dataPath}");
            Console.WriteLine($"Output path: {_outputPath}");
            
            Directory.CreateDirectory(_outputPath);

            try
            {
                // Load main database (I12.mhd)
                Console.WriteLine("\nLoading main database...");
                if (DatabaseAPI.LoadMainDatabase(_dataPath))
                {
                    Console.WriteLine("Main database loaded successfully!");
                    ExportMainDatabase();
                }
                else
                {
                    Console.WriteLine("Failed to load main database!");
                }

                // Load enhancement database
                Console.WriteLine("\nLoading enhancement database...");
                DatabaseAPI.LoadEnhancementDb(_dataPath);
                ExportEnhancements();

                // Load recipes
                Console.WriteLine("\nLoading recipes...");
                DatabaseAPI.LoadRecipes(_dataPath);
                ExportRecipes();

                // Load salvage
                Console.WriteLine("\nLoading salvage...");
                DatabaseAPI.LoadSalvage(_dataPath);
                ExportSalvage();

                Console.WriteLine("\nExport completed!");
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
            var db = DatabaseAPI.Database;
            
            // Export Archetypes
            Console.WriteLine($"\nExporting {db.Classes.Length} archetypes...");
            var archetypes = db.Classes.Select((arch, idx) => new
            {
                id = idx + 1,
                name = arch.ClassName,
                display_name = arch.DisplayName,
                description = arch.DescLong,
                primary_group = arch.PrimaryGroup,
                secondary_group = arch.SecondaryGroup,
                hit_points_base = arch.Hitpoints,
                hit_points_max = (int)(arch.Hitpoints * arch.HPCap)
            }).ToList();
            
            SaveToJson("archetypes.json", archetypes);
            
            // Export Powersets
            Console.WriteLine($"\nExporting {db.Powersets.Length} powersets...");
            var powersets = db.Powersets.Select((ps, idx) => new
            {
                id = idx + 1,
                name = ps.SetName,
                display_name = ps.DisplayName,
                description = ps.Description,
                archetype_id = ps.ATClass >= 0 && ps.ATClass < db.Classes.Length ? ps.ATClass + 1 : (int?)null,
                powerset_type = ConvertPowersetType(ps.SetType),
                icon_path = ps.ImageName
            }).ToList();
            
            SaveToJson("powersets.json", powersets);
            
            // Export Powers
            Console.WriteLine($"\nExporting {db.Power.Length} powers...");
            var powers = db.Power.Select((power, idx) => new
            {
                id = idx + 1,
                name = power.PowerName,
                display_name = power.DisplayName,
                description = power.DescLong,
                powerset_id = power.PowerSetID >= 0 && power.PowerSetID < db.Powersets.Length ? power.PowerSetID + 1 : (int?)null,
                level_available = power.Level,
                power_type = power.PowerType.ToString().ToLower(),
                target_type = power.EntitiesAutoHit.ToString().ToLower(),
                accuracy = (decimal)power.Accuracy,
                damage_scale = power.Effects?.Any(e => e.EffectType == Enums.eEffectType.Damage) == true 
                    ? (decimal?)power.Effects.Where(e => e.EffectType == Enums.eEffectType.Damage).Sum(e => e.Scale) 
                    : null,
                endurance_cost = (decimal)power.EndCost,
                recharge_time = (decimal)power.RechargeTime,
                activation_time = (decimal)power.CastTime,
                range_feet = power.Range,
                radius_feet = power.Radius,
                max_targets = power.MaxTargets,
                icon_path = power.IconName
            }).ToList();
            
            SaveToJson("powers.json", powers);
        }

        private void ExportEnhancements()
        {
            var db = DatabaseAPI.Database;
            
            // Export Enhancement Sets
            Console.WriteLine($"\nExporting {db.EnhancementSets.Count} enhancement sets...");
            var enhSets = db.EnhancementSets.Select((set, idx) => new
            {
                id = idx + 1,
                name = set.Name,
                display_name = set.DisplayName,
                description = set.Desc,
                min_level = set.LevelMin,
                max_level = set.LevelMax
            }).ToList();
            
            SaveToJson("enhancement_sets.json", enhSets);
            
            // Export Enhancements
            Console.WriteLine($"\nExporting {db.Enhancements.Length} enhancements...");
            var enhancements = db.Enhancements.Select((enh, idx) => new
            {
                id = idx + 1,
                name = enh.Name,
                display_name = enh.ShortName,
                enhancement_type = ConvertEnhancementType(enh.TypeID),
                set_id = enh.nIDSet >= 0 && enh.nIDSet < db.EnhancementSets.Count ? enh.nIDSet + 1 : (int?)null,
                level_min = enh.LevelMin,
                level_max = enh.LevelMax,
                unique_enhancement = enh.Unique
            }).ToList();
            
            SaveToJson("enhancements.json", enhancements);
            
            // Export Set Bonuses
            var setBonuses = new List<object>();
            int bonusId = 1;
            
            for (int setIdx = 0; setIdx < db.EnhancementSets.Count; setIdx++)
            {
                var set = db.EnhancementSets[setIdx];
                for (int bonusIdx = 0; bonusIdx < set.Bonus.Length; bonusIdx++)
                {
                    var bonus = set.Bonus[bonusIdx];
                    if (bonus != null && bonus.Index.Length > 0)
                    {
                        setBonuses.Add(new
                        {
                            id = bonusId++,
                            set_id = setIdx + 1,
                            pieces_required = bonusIdx + 2, // Bonuses start at 2 pieces
                            bonus_type = "multiple",
                            bonus_description = string.Join(", ", bonus.Index.Select(i => GetBonusDescription(i, bonus)))
                        });
                    }
                }
            }
            
            SaveToJson("set_bonuses.json", setBonuses);
        }

        private void ExportRecipes()
        {
            var db = DatabaseAPI.Database;
            
            Console.WriteLine($"\nExporting {db.Recipes.Length} recipes...");
            var recipes = db.Recipes.Select((recipe, idx) => new
            {
                id = idx + 1,
                name = recipe.InternalName,
                external_name = recipe.ExternalName,
                rarity = recipe.Rarity.ToString().ToLower(),
                level_min = recipe.Level.Min(l => l.Level),
                level_max = recipe.Level.Max(l => l.Level),
                enhancement_id = recipe.EnhIdx >= 0 && recipe.EnhIdx < db.Enhancements.Length ? recipe.EnhIdx + 1 : (int?)null,
                salvage_requirements = recipe.Salvage.Select(s => new { salvage_id = s.ID + 1, count = s.Count }).ToList(),
                cost_by_level = recipe.Level.Select(l => l.BuyCost).ToList()
            }).ToList();
            
            SaveToJson("recipes.json", recipes);
        }

        private void ExportSalvage()
        {
            var db = DatabaseAPI.Database;
            
            Console.WriteLine($"\nExporting {db.Salvage.Length} salvage items...");
            var salvage = db.Salvage.Select((item, idx) => new
            {
                id = idx + 1,
                name = item.InternalName,
                display_name = item.ExternalName,
                description = item.InternalName, // MidsReborn doesn't seem to have descriptions
                salvage_type = item.Origin.ToString().ToLower(),
                rarity = item.Rarity.ToString().ToLower(),
                level_min = item.LevelMin,
                level_max = item.LevelMax,
                sell_price = item.Inf,
                buy_price = item.Inf * 10 // Approximate
            }).ToList();
            
            SaveToJson("salvage.json", salvage);
        }

        private string ConvertPowersetType(Enums.ePowerSetType type)
        {
            return type switch
            {
                Enums.ePowerSetType.Primary => "primary",
                Enums.ePowerSetType.Secondary => "secondary",
                Enums.ePowerSetType.Pool => "pool",
                Enums.ePowerSetType.Ancillary => "epic",
                Enums.ePowerSetType.Inherent => "inherent",
                Enums.ePowerSetType.Incarnate => "incarnate",
                _ => "other"
            };
        }

        private string ConvertEnhancementType(Enums.eType type)
        {
            return type switch
            {
                Enums.eType.Normal => "IO",
                Enums.eType.InventO => "IO",
                Enums.eType.SpecialO => "SO",
                Enums.eType.SetO => "set_piece",
                _ => "other"
            };
        }

        private string GetBonusDescription(int index, EnhancementSet.BonusItem bonus)
        {
            // Simplified - in reality this would need to look up the actual bonus effects
            return $"Bonus effect {index + 1}";
        }

        private void SaveToJson(string filename, object data)
        {
            var outputFile = Path.Combine(_outputPath, filename);
            var json = JsonConvert.SerializeObject(data, _jsonSettings);
            File.WriteAllText(outputFile, json);
            Console.WriteLine($"  Saved to {outputFile}");
        }

        private void CreateExportReport()
        {
            var report = new
            {
                exportDate = DateTime.UtcNow,
                dataDirectory = _dataPath,
                outputDirectory = _outputPath,
                exportedFiles = Directory.GetFiles(_outputPath, "*.json")
                    .Select(f => new
                    {
                        filename = Path.GetFileName(f),
                        size = new FileInfo(f).Length,
                        lastModified = File.GetLastWriteTimeUtc(f)
                    })
                    .ToList(),
                statistics = new
                {
                    archetypes = DatabaseAPI.Database.Classes.Length,
                    powersets = DatabaseAPI.Database.Powersets.Length,
                    powers = DatabaseAPI.Database.Power.Length,
                    enhancements = DatabaseAPI.Database.Enhancements.Length,
                    enhancementSets = DatabaseAPI.Database.EnhancementSets.Count,
                    recipes = DatabaseAPI.Database.Recipes.Length,
                    salvage = DatabaseAPI.Database.Salvage.Length
                }
            };

            SaveToJson("export_report.json", report);
            Console.WriteLine($"\nExport report saved!");
        }
    }
}