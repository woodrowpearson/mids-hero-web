using System;
using System.IO;
using Newtonsoft.Json;

namespace DataExporter
{
    internal class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 2)
            {
                Console.WriteLine("Usage: DataExporter <input-folder> <output-folder>");
                Console.WriteLine("Example: DataExporter ~/code/Homecoming_2025.7.1111 ~/code/mids-hero-web/data/exported-json");
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

            Directory.CreateDirectory(outputPath);
            
            Console.WriteLine($"Input folder: {inputPath}");
            Console.WriteLine($"Output folder: {outputPath}");
            
            // Check for flags
            bool useDirect = args.Length > 2 && args[2] == "--direct";
            bool useMac = args.Length > 2 && args[2] == "--mac";
            
            if (useMac)
            {
                Console.WriteLine("Using Mac MidsReborn explorer...");
                var macExplorer = new MacMidsExplorer(inputPath, outputPath);
                macExplorer.ExploreAndExport();
            }
            else if (useDirect)
            {
                Console.WriteLine("Using direct data loader (no configuration)...");
                var directLoader = new DirectDataLoader(inputPath, outputPath);
                directLoader.Export();
            }
            else
            {
                // Try to use MidsReborn exporter if available
                var exporter = new MidsRebornExporter(inputPath, outputPath);
                exporter.Export();
            }
            
            // If MidsReborn is not available, fall back to JSON processing
            #if !MIDSREBORN
            Console.WriteLine("\nFalling back to JSON file processing...");
            ProcessJsonFiles(inputPath, outputPath);
            #endif
        }

        static void ProcessJsonFiles(string inputPath, string outputPath)
        {
            try
            {
                // Process AttribMod.json
                var attribModFile = Path.Combine(inputPath, "AttribMod.json");
                if (File.Exists(attribModFile))
                {
                    var attribModData = File.ReadAllText(attribModFile);
                    var attribModJson = JsonConvert.DeserializeObject(attribModData);
                    var outputFile = Path.Combine(outputPath, "AttribMod.json");
                    File.WriteAllText(outputFile, JsonConvert.SerializeObject(attribModJson, Formatting.Indented));
                    Console.WriteLine($"Processed AttribMod.json -> {outputFile}");
                }

                // Process TypeGrades.json
                var typeGradesFile = Path.Combine(inputPath, "TypeGrades.json");
                if (File.Exists(typeGradesFile))
                {
                    var typeGradesData = File.ReadAllText(typeGradesFile);
                    var typeGradesJson = JsonConvert.DeserializeObject(typeGradesData);
                    var outputFile = Path.Combine(outputPath, "TypeGrades.json");
                    File.WriteAllText(outputFile, JsonConvert.SerializeObject(typeGradesJson, Formatting.Indented));
                    Console.WriteLine($"Processed TypeGrades.json -> {outputFile}");
                }

                // List available .mhd files for future processing
                Console.WriteLine("\nAvailable .mhd files for future processing:");
                var mhdFiles = Directory.GetFiles(inputPath, "*.mhd");
                foreach (var mhdFile in mhdFiles)
                {
                    var fileInfo = new FileInfo(mhdFile);
                    Console.WriteLine($"  {Path.GetFileName(mhdFile)} ({fileInfo.Length:N0} bytes)");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error processing files: {ex.Message}");
            }
        }
    }
}
