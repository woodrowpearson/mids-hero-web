using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using Newtonsoft.Json;

namespace DataExporter
{
    /// <summary>
    /// Converts MHD (Mids Hero Designer) binary files to JSON format.
    /// Based on the Mids Reborn file format.
    /// </summary>
    public class MhdToJsonConverter
    {
        private readonly string _inputPath;
        private readonly string _outputPath;

        // File headers from Mids Reborn
        private const string DbHeader = "Mids Reborn Powers Database";
        private const string EnhDbHeader = "Mids Reborn Enhancement Database";
        private const string SalvageHeader = "Mids Reborn Salvage Database";
        private const string RecipeHeader = "Mids Reborn Recipe Database";

        // Section markers
        private const string ArchetypesSection = "BEGIN:ARCHETYPES";
        private const string PowersetsSection = "BEGIN:POWERSETS";
        private const string PowersSection = "BEGIN:POWERS";
        private const string SummonsSection = "BEGIN:SUMMONS";

        public MhdToJsonConverter(string inputPath, string outputPath)
        {
            _inputPath = inputPath;
            _outputPath = outputPath;
        }

        public void ConvertDatabase()
        {
            var dbFile = Path.Combine(_inputPath, "I12.mhd");
            if (!File.Exists(dbFile))
            {
                Console.WriteLine($"Database file not found: {dbFile}");
                return;
            }

            try
            {
                using var fileStream = new FileStream(dbFile, FileMode.Open, FileAccess.Read);
                using var reader = new BinaryReader(fileStream);

                // Read header
                var header = reader.ReadString();
                if (header != DbHeader)
                {
                    Console.WriteLine($"Invalid header: expected '{DbHeader}', got '{header}'");
                    return;
                }

                var database = new GameDatabase
                {
                    Version = reader.ReadString(),
                    Date = ReadDate(reader),
                    Issue = reader.ReadInt32(),
                    PageVol = reader.ReadInt32(),
                    PageVolText = reader.ReadString()
                };

                Console.WriteLine($"Database Version: {database.Version}");
                Console.WriteLine($"Database Date: {database.Date}");

                // Read sections
                while (reader.BaseStream.Position < reader.BaseStream.Length)
                {
                    try
                    {
                        var section = reader.ReadString();
                        switch (section)
                        {
                            case ArchetypesSection:
                                database.Archetypes = ReadArchetypes(reader);
                                Console.WriteLine($"Read {database.Archetypes.Count} archetypes");
                                break;
                            case PowersetsSection:
                                database.Powersets = ReadPowersets(reader);
                                Console.WriteLine($"Read {database.Powersets.Count} powersets");
                                break;
                            case PowersSection:
                                database.Powers = ReadPowers(reader);
                                Console.WriteLine($"Read {database.Powers.Count} powers");
                                break;
                            case SummonsSection:
                                database.Summons = ReadSummons(reader);
                                Console.WriteLine($"Read {database.Summons.Count} summons");
                                break;
                            default:
                                // Skip unknown sections
                                Console.WriteLine($"Unknown section: {section}");
                                break;
                        }
                    }
                    catch (EndOfStreamException)
                    {
                        break;
                    }
                }

                // Save to JSON
                SaveToJson(database);
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error converting database: {ex.Message}");
                Console.WriteLine(ex.StackTrace);
            }
        }

        private DateTime ReadDate(BinaryReader reader)
        {
            var year = reader.ReadInt32();
            if (year > 0)
            {
                var month = reader.ReadInt32();
                var day = reader.ReadInt32();
                return new DateTime(year, month, day);
            }
            else
            {
                return DateTime.FromBinary(reader.ReadInt64());
            }
        }

        private List<Archetype> ReadArchetypes(BinaryReader reader)
        {
            var archetypes = new List<Archetype>();
            var count = reader.ReadInt32();

            for (int i = 0; i < count; i++)
            {
                var archetype = new Archetype
                {
                    DisplayName = reader.ReadString(),
                    HitPoints = reader.ReadInt32(),
                    HitPointsMax = reader.ReadSingle(),
                    DescLong = reader.ReadString(),
                    ResCap = reader.ReadSingle(),
                    ClassName = reader.ReadString(),
                    ClassType = reader.ReadInt32(),
                    Column = reader.ReadInt32(),
                    DescShort = reader.ReadString(),
                    PrimaryGroup = reader.ReadString(),
                    SecondaryGroup = reader.ReadString(),
                    Playable = reader.ReadBoolean(),
                    BaseRecovery = reader.ReadSingle(),
                    BaseRegen = reader.ReadSingle(),
                    BaseThreat = reader.ReadSingle(),
                    PerceptionCap = reader.ReadSingle()
                };

                // Read origins
                var originCount = reader.ReadInt32();
                archetype.Origins = new List<string>();
                for (int j = 0; j < originCount; j++)
                {
                    archetype.Origins.Add(reader.ReadString());
                }

                // Read various caps
                archetype.RechargeCap = reader.ReadSingle();
                archetype.RecoveryCap = reader.ReadSingle();
                archetype.RegenCap = reader.ReadSingle();
                archetype.DamageCap = reader.ReadSingle();
                archetype.HitCap = reader.ReadSingle();
                archetype.DefenseCap = reader.ReadSingle();
                archetype.ResistanceCap = reader.ReadSingle();

                archetypes.Add(archetype);
            }

            return archetypes;
        }

        private List<Powerset> ReadPowersets(BinaryReader reader)
        {
            var powersets = new List<Powerset>();
            var count = reader.ReadInt32();

            for (int i = 0; i < count; i++)
            {
                var powerset = new Powerset
                {
                    DisplayName = reader.ReadString(),
                    SetType = reader.ReadInt32(),
                    ImageName = reader.ReadString(),
                    FullName = reader.ReadString(),
                    SetName = reader.ReadString(),
                    Description = reader.ReadString(),
                    SubName = reader.ReadString(),
                    ATClass = reader.ReadString(),
                    // Note: Actual format may vary - this is simplified
                };

                powersets.Add(powerset);
            }

            return powersets;
        }

        private List<Power> ReadPowers(BinaryReader reader)
        {
            var powers = new List<Power>();
            var count = reader.ReadInt32();

            for (int i = 0; i < count; i++)
            {
                var power = new Power
                {
                    FullName = reader.ReadString(),
                    DisplayName = reader.ReadString(),
                    PowerName = reader.ReadString(),
                    // Note: Actual format has many more fields
                };

                powers.Add(power);
            }

            return powers;
        }

        private List<Summon> ReadSummons(BinaryReader reader)
        {
            var summons = new List<Summon>();
            // Implementation would go here
            return summons;
        }

        private void SaveToJson(GameDatabase database)
        {
            var settings = new JsonSerializerSettings
            {
                Formatting = Formatting.Indented,
                NullValueHandling = NullValueHandling.Ignore
            };

            // Save complete database
            var fullPath = Path.Combine(_outputPath, "database.json");
            File.WriteAllText(fullPath, JsonConvert.SerializeObject(database, settings));
            Console.WriteLine($"Saved complete database to {fullPath}");

            // Save individual collections for easier processing
            SaveJsonFile("archetypes.json", database.Archetypes, settings);
            SaveJsonFile("powersets.json", database.Powersets, settings);
            SaveJsonFile("powers.json", database.Powers, settings);
            SaveJsonFile("summons.json", database.Summons, settings);
        }

        private void SaveJsonFile<T>(string filename, T data, JsonSerializerSettings settings)
        {
            var path = Path.Combine(_outputPath, filename);
            File.WriteAllText(path, JsonConvert.SerializeObject(data, settings));
            Console.WriteLine($"Saved {filename}");
        }
    }

    // Data classes
    public class GameDatabase
    {
        public string Version { get; set; }
        public DateTime Date { get; set; }
        public int Issue { get; set; }
        public int PageVol { get; set; }
        public string PageVolText { get; set; }
        public List<Archetype> Archetypes { get; set; } = new();
        public List<Powerset> Powersets { get; set; } = new();
        public List<Power> Powers { get; set; } = new();
        public List<Summon> Summons { get; set; } = new();
    }

    public class Archetype
    {
        public string DisplayName { get; set; }
        public string ClassName { get; set; }
        public string DescShort { get; set; }
        public string DescLong { get; set; }
        public int HitPoints { get; set; }
        public float HitPointsMax { get; set; }
        public string PrimaryGroup { get; set; }
        public string SecondaryGroup { get; set; }
        public bool Playable { get; set; }
        public int ClassType { get; set; }
        public int Column { get; set; }
        public List<string> Origins { get; set; }
        
        // Caps
        public float ResCap { get; set; }
        public float RechargeCap { get; set; }
        public float RecoveryCap { get; set; }
        public float RegenCap { get; set; }
        public float DamageCap { get; set; }
        public float HitCap { get; set; }
        public float DefenseCap { get; set; }
        public float ResistanceCap { get; set; }
        public float BaseRecovery { get; set; }
        public float BaseRegen { get; set; }
        public float BaseThreat { get; set; }
        public float PerceptionCap { get; set; }
    }

    public class Powerset
    {
        public string DisplayName { get; set; }
        public string FullName { get; set; }
        public string SetName { get; set; }
        public string Description { get; set; }
        public string SubName { get; set; }
        public string ATClass { get; set; }
        public string ImageName { get; set; }
        public int SetType { get; set; }
    }

    public class Power
    {
        public string FullName { get; set; }
        public string DisplayName { get; set; }
        public string PowerName { get; set; }
    }

    public class Summon
    {
        // Implementation would go here
    }
}