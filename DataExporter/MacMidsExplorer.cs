using System;
using System.IO;
using System.Reflection;
using System.Linq;
using Newtonsoft.Json;

namespace DataExporter
{
    /// <summary>
    /// Explores the Mac MidsReborn installation to understand available APIs
    /// </summary>
    public class MacMidsExplorer
    {
        private readonly string _midsPath = "/Applications/Mids";
        private readonly string _outputPath;
        private readonly string _dataPath;

        public MacMidsExplorer(string dataPath, string outputPath)
        {
            _dataPath = dataPath;
            _outputPath = outputPath;
        }

        public void ExploreAndExport()
        {
            Console.WriteLine("=== Mac MidsReborn Explorer ===\n");

            // Use provided data path
            if (Directory.Exists(_dataPath))
            {
                Console.WriteLine($"Found data directory: {_dataPath}");
                ProcessDataFiles(_dataPath);
                
                // Use the text parser for structured extraction
                var textParser = new TextToJsonParser(_outputPath);
                textParser.ParseExtractedFiles();
            }

#if MIDSREBORN
            // Try to explore the DLL structure
            try
            {
                var midsRebornDll = Path.Combine(_midsPath, "MidsReborn.dll");
                if (File.Exists(midsRebornDll))
                {
                    Console.WriteLine($"\nExploring MidsReborn.dll...");
                    var assembly = Assembly.LoadFrom(midsRebornDll);
                    
                    // Find database-related types
                    var databaseTypes = assembly.GetTypes()
                        .Where(t => t.Name.Contains("Database") || t.Name.Contains("Data"))
                        .OrderBy(t => t.FullName)
                        .Take(20);

                    Console.WriteLine("\nDatabase-related types found:");
                    foreach (var type in databaseTypes)
                    {
                        Console.WriteLine($"  {type.FullName}");
                        
                        // Look for static methods that might load data
                        var staticMethods = type.GetMethods(BindingFlags.Public | BindingFlags.Static)
                            .Where(m => m.Name.Contains("Load") || m.Name.Contains("Read"))
                            .Take(5);
                        
                        foreach (var method in staticMethods)
                        {
                            Console.WriteLine($"    -> {method.Name}({string.Join(", ", method.GetParameters().Select(p => p.ParameterType.Name))})");
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error exploring DLL: {ex.Message}");
            }
#endif
        }

        private void ProcessDataFiles(string dataPath)
        {
            Directory.CreateDirectory(_outputPath);

            // Copy JSON files as-is
            var jsonFiles = Directory.GetFiles(dataPath, "*.json");
            foreach (var jsonFile in jsonFiles)
            {
                var fileName = Path.GetFileName(jsonFile);
                var outputFile = Path.Combine(_outputPath, fileName);
                File.Copy(jsonFile, outputFile, true);
                Console.WriteLine($"  Copied: {fileName}");
            }

            // Process MHD files to extract readable data
            var mhdFiles = Directory.GetFiles(dataPath, "*.mhd");
            Console.WriteLine($"\nFound {mhdFiles.Length} MHD files:");
            
            foreach (var mhdFile in mhdFiles)
            {
                var fileName = Path.GetFileName(mhdFile);
                Console.WriteLine($"\n  Processing: {fileName}");
                ExtractMhdData(mhdFile);
            }
        }

        private void ExtractMhdData(string mhdFile)
        {
            try
            {
                var fileName = Path.GetFileNameWithoutExtension(mhdFile);
                var outputFile = Path.Combine(_outputPath, $"{fileName}_extracted.txt");

                // Extract all readable strings from the MHD file
                using (var reader = new BinaryReader(File.OpenRead(mhdFile)))
                {
                    var fileSize = reader.BaseStream.Length;
                    var strings = new List<string>();
                    var currentString = "";
                    
                    while (reader.BaseStream.Position < fileSize)
                    {
                        try
                        {
                            var b = reader.ReadByte();
                            if (b >= 32 && b <= 126) // Printable ASCII
                            {
                                currentString += (char)b;
                            }
                            else if (currentString.Length > 3) // Save strings longer than 3 chars
                            {
                                strings.Add(currentString);
                                currentString = "";
                            }
                            else
                            {
                                currentString = "";
                            }
                        }
                        catch
                        {
                            break;
                        }
                    }

                    // Save extracted strings
                    File.WriteAllLines(outputFile, strings);
                    Console.WriteLine($"    Extracted {strings.Count} strings -> {Path.GetFileName(outputFile)}");

                    // Try to identify structured sections
                    var sections = strings.Where(s => s.StartsWith("BEGIN:")).ToList();
                    if (sections.Any())
                    {
                        Console.WriteLine($"    Found sections: {string.Join(", ", sections)}");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"    Error: {ex.Message}");
            }
        }
    }
}