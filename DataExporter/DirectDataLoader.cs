using System;
using System.IO;
using Newtonsoft.Json;

#if MIDSREBORN
using Mids_Reborn.Core;
using Mids_Reborn.Core.Base.Master_Classes;
using Mids_Reborn.Core.Base.Data_Classes;
#endif

namespace DataExporter
{
    /// <summary>
    /// Alternative approach that loads MHD data directly without configuration
    /// </summary>
    public class DirectDataLoader
    {
        private readonly string _inputPath;
        private readonly string _outputPath;

        public DirectDataLoader(string inputPath, string outputPath)
        {
            _inputPath = inputPath;
            _outputPath = outputPath;
        }

        public void Export()
        {
#if MIDSREBORN
            try
            {
                Console.WriteLine("=== Direct MHD Data Loading (No Config) ===");
                Console.WriteLine($"Input: {_inputPath}");
                Console.WriteLine($"Output: {_outputPath}");
                
                // Directly load the main database without configuration
                Console.Write("\nLoading I12.mhd... ");
                var i12Path = Path.Combine(_inputPath, "I12.mhd");
                if (File.Exists(i12Path))
                {
                    DatabaseAPI.LoadMainDatabase(_inputPath);
                    Console.WriteLine($"OK - Loaded {DatabaseAPI.Database?.Power?.Length ?? 0} powers");
                }
                else
                {
                    Console.WriteLine($"ERROR: I12.mhd not found at {i12Path}");
                    return;
                }

                // Try to load other data files
                Console.Write("Loading EnhDB.mhd... ");
                try
                {
                    DatabaseAPI.LoadEnhancementDb(_inputPath);
                    Console.WriteLine($"OK - Loaded {DatabaseAPI.Database?.Enhancements?.Length ?? 0} enhancements");
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Failed: {ex.Message}");
                }

                // Export what we have
                Console.WriteLine("\nExporting to JSON...");
                Directory.CreateDirectory(_outputPath);

                var settings = new JsonSerializerSettings
                {
                    Formatting = Formatting.Indented,
                    ReferenceLoopHandling = ReferenceLoopHandling.Ignore
                };

                // Export powers if we have them
                if (DatabaseAPI.Database?.Power != null)
                {
                    Console.Write("Exporting powers.json... ");
                    File.WriteAllText(
                        Path.Combine(_outputPath, "powers.json"),
                        JsonConvert.SerializeObject(DatabaseAPI.Database.Power, settings)
                    );
                    Console.WriteLine("OK");
                }

                // Export enhancements if we have them
                if (DatabaseAPI.Database?.Enhancements != null)
                {
                    Console.Write("Exporting enhancements.json... ");
                    File.WriteAllText(
                        Path.Combine(_outputPath, "enhancements.json"),
                        JsonConvert.SerializeObject(DatabaseAPI.Database.Enhancements, settings)
                    );
                    Console.WriteLine("OK");
                }

                Console.WriteLine("\n=== Export Complete! ===");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"\nERROR: {ex.Message}");
                Console.WriteLine($"Type: {ex.GetType().Name}");
                if (ex.InnerException != null)
                {
                    Console.WriteLine($"Inner: {ex.InnerException.Message}");
                }
            }
#else
            Console.WriteLine("MidsReborn is not enabled in this build.");
#endif
        }
    }
}