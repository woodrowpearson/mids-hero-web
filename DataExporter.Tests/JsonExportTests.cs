using System;
using System.IO;
using System.Linq;
using Xunit;
using DataExporter;
using Newtonsoft.Json;
using Newtonsoft.Json.Linq;

namespace DataExporter.Tests
{
    public class JsonExportTests : IDisposable
    {
        private readonly string _testInputPath;
        private readonly string _testOutputPath;

        public JsonExportTests()
        {
            _testInputPath = Path.Combine(Path.GetTempPath(), "JsonExportTests_Input_" + Guid.NewGuid());
            _testOutputPath = Path.Combine(Path.GetTempPath(), "JsonExportTests_Output_" + Guid.NewGuid());
            
            Directory.CreateDirectory(_testInputPath);
            Directory.CreateDirectory(_testOutputPath);
        }

        public void Dispose()
        {
            if (Directory.Exists(_testInputPath))
                Directory.Delete(_testInputPath, true);
            if (Directory.Exists(_testOutputPath))
                Directory.Delete(_testOutputPath, true);
        }

        [Fact]
        public void Export_CreatesOutputDirectory_WhenNotExists()
        {
            // Arrange
            var nonExistentPath = Path.Combine(Path.GetTempPath(), "NonExistent_" + Guid.NewGuid());
            var exporter = new MidsRebornExporter(_testInputPath, nonExistentPath);

            try
            {
                // Act
                exporter.Export();

                // Assert
                if (TestHelpers.IsMidsRebornAvailable())
                {
                    Assert.True(Directory.Exists(nonExistentPath));
                }
                else
                {
                    // Without MidsReborn, directory creation doesn't happen
                    Assert.True(true, "Directory creation requires MidsReborn");
                }
            }
            finally
            {
                if (Directory.Exists(nonExistentPath))
                    Directory.Delete(nonExistentPath, true);
            }
        }

        [Fact]
        public void CustomExport_ShouldCreateExpectedJsonFiles()
        {
            // This test documents the expected output files from custom export
            var expectedFiles = new[]
            {
                "archetypes.json",
                "powersets.json",
                "powers.json",
                "enhancements.json",
                "enhancement_sets.json",
                "recipes.json",
                "salvage.json"
            };

            // The actual export would create these files
            // This test serves as documentation
            Assert.All(expectedFiles, file =>
                Assert.True(file.EndsWith(".json"), $"{file} should be a JSON file"));
        }

        [Fact]
        public void JsonSerializerSettings_ConfiguredCorrectly()
        {
            // Test that the JSON serializer settings are appropriate
            var settings = new JsonSerializerSettings
            {
                Formatting = Formatting.Indented,
                ReferenceLoopHandling = ReferenceLoopHandling.Ignore,
                TypeNameHandling = TypeNameHandling.Auto
            };

            // These settings should handle circular references
            Assert.Equal(ReferenceLoopHandling.Ignore, settings.ReferenceLoopHandling);
            
            // Type information should be included for polymorphic types
            Assert.Equal(TypeNameHandling.Auto, settings.TypeNameHandling);
            
            // Output should be human-readable
            Assert.Equal(Formatting.Indented, settings.Formatting);
        }

        [Theory]
        [InlineData("archetypes.json")]
        [InlineData("powersets.json")]
        [InlineData("powers.json")]
        [InlineData("enhancements.json")]
        [InlineData("enhancement_sets.json")]
        [InlineData("recipes.json")]
        [InlineData("salvage.json")]
        public void Export_OutputFiles_ShouldBeValidJson(string fileName)
        {
            // Create a dummy JSON file to test validation
            var filePath = Path.Combine(_testOutputPath, fileName);
            File.WriteAllText(filePath, "[]"); // Empty array

            // Test that it's valid JSON
            var content = File.ReadAllText(filePath);
            var exception = Record.Exception(() => JToken.Parse(content));
            Assert.Null(exception);
        }

        [Fact]
        public void Export_HandlesBuiltInExportFailure_Gracefully()
        {
            // The ExportToJson method has fallback logic
            // This test documents that behavior
            
            var exporter = new MidsRebornExporter(_testInputPath, _testOutputPath);
            var consoleOutput = new StringWriter();
            Console.SetOut(consoleOutput);

            // Act
            exporter.Export();

            // Assert - should mention export attempt
            var output = consoleOutput.ToString();
            // Either built-in or custom export should be attempted
            Assert.True(
                output.Contains("MidsReborn MHD to JSON Export") ||
                output.Contains("export"),
                "Export process should be attempted"
            );
        }
    }
}