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
            
            // Process JSON files that are already available
            ProcessJsonFiles(inputPath, outputPath);
            
            // Process MHD files
            Console.WriteLine("\nProcessing MHD files...");
            Console.WriteLine("\nTrying simple parser approach:");
            SimpleMhdParser.ParseAndConvert(inputPath, outputPath);
            
            Console.WriteLine("\nNote: Full MHD parsing requires either:");
            Console.WriteLine("1. Reverse engineering the custom binary format");
            Console.WriteLine("2. Using Mids Reborn's actual DLLs");
            Console.WriteLine("3. Obtaining data in JSON/SQL format from the Mids Reborn team");
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
