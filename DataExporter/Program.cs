using System;
using System.IO;

namespace DataExporter
{
    internal class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: DataExporter <mhd-data-folder> <output-folder>");
                Console.WriteLine("Example: DataExporter ~/code/mids-hero-web/data/Homecoming_2025-7-1111 ~/code/mids-hero-web/data/exported-json");
                Console.WriteLine("\nThis tool uses MidsReborn to export City of Heroes MHD data files to JSON format.");
                return;
            }

            var inputPath = args[0];
            var outputPath = args[1];
            
            // Expand tilde paths
            if (inputPath.StartsWith("~/"))
            {
                inputPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), inputPath[2..]);
            }
            if (outputPath.StartsWith("~/"))
            {
                outputPath = Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), outputPath[2..]);
            }

            // Validate input directory exists
            if (!Directory.Exists(inputPath))
            {
                Console.WriteLine($"Error: Input directory does not exist: {inputPath}");
                return;
            }

            // Validate required MHD files exist
            var requiredFiles = new[] { "I12.mhd", "EnhDB.mhd", "Recipe.mhd", "Salvage.mhd" };
            foreach (var file in requiredFiles)
            {
                var filePath = Path.Combine(inputPath, file);
                if (!File.Exists(filePath))
                {
                    Console.WriteLine($"Warning: Required file not found: {filePath}");
                }
            }

            // Create output directory if needed
            Directory.CreateDirectory(outputPath);
            
            // Use the MidsReborn exporter
            var exporter = new MidsRebornExporter(inputPath, outputPath);
            exporter.ExportAllData();
        }
    }
}
