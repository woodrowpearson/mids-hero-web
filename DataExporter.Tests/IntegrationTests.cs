using System;
using System.Diagnostics;
using System.IO;
using System.Linq;
using Xunit;
using DataExporter;

namespace DataExporter.Tests
{
    public class IntegrationTests : IDisposable
    {
        private readonly string _testDataPath;
        private readonly string _testOutputPath;
        private readonly string _fixturesPath;

        public IntegrationTests()
        {
            _testDataPath = Path.Combine(Path.GetTempPath(), "IntegrationTests_Data_" + Guid.NewGuid());
            _testOutputPath = Path.Combine(Path.GetTempPath(), "IntegrationTests_Output_" + Guid.NewGuid());
            _fixturesPath = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "TestFixtures");
            
            Directory.CreateDirectory(_testDataPath);
            Directory.CreateDirectory(_testOutputPath);
        }

        public void Dispose()
        {
            if (Directory.Exists(_testDataPath))
                Directory.Delete(_testDataPath, true);
            if (Directory.Exists(_testOutputPath))
                Directory.Delete(_testOutputPath, true);
        }

        [Fact]
        public void EndToEnd_CompleteExportPipeline()
        {
            // This test documents the complete pipeline
            // In a real scenario with MHD files, it would:
            // 1. Initialize configuration
            // 2. Load all MHD files
            // 3. Export to JSON
            // 4. Verify output files

            var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
            var consoleOutput = new StringWriter();
            Console.SetOut(consoleOutput);

            // Act
            exporter.Export();

            // Assert
            var output = consoleOutput.ToString();
            Assert.Contains("MidsReborn MHD to JSON Export", output);
            Assert.Contains("Input path:", output);
            Assert.Contains("Output path:", output);
        }

        [Fact]
        public void Performance_ExportCompleteTime()
        {
            // Benchmark the export process
            var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
            var stopwatch = new Stopwatch();

            // Suppress console output for performance test
            Console.SetOut(TextWriter.Null);

            // Act
            stopwatch.Start();
            exporter.Export();
            stopwatch.Stop();

            // Assert - export should complete in reasonable time
            // Even with errors, the process should not hang
            Assert.True(stopwatch.ElapsedMilliseconds < 30000, // 30 seconds max
                $"Export took too long: {stopwatch.ElapsedMilliseconds}ms");
        }

        [Theory]
        [InlineData("Happy Path", true, true, true)]
        [InlineData("Missing Main DB", false, true, true)]
        [InlineData("Missing Enhancements", true, false, true)]
        [InlineData("Missing All", false, false, false)]
        public void Scenarios_DifferentDataAvailability(string scenario, bool hasMainDb, bool hasEnhDb, bool hasRecipes)
        {
            // Test different scenarios of data availability
            // Document expected behavior for each case

            // Create mock files based on scenario
            if (hasMainDb)
                File.WriteAllBytes(Path.Combine(_testDataPath, "I12.mhd"), new byte[] { 0x00 });
            if (hasEnhDb)
                File.WriteAllBytes(Path.Combine(_testDataPath, "EnhDB.mhd"), new byte[] { 0x00 });
            if (hasRecipes)
                File.WriteAllBytes(Path.Combine(_testDataPath, "Recipe.mhd"), new byte[] { 0x00 });

            var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
            var consoleOutput = new StringWriter();
            Console.SetOut(consoleOutput);

            // Act
            exporter.Export();

            // Assert
            var output = consoleOutput.ToString();
            Assert.Contains("MidsReborn", output);
            
            // Export should always attempt to run
            Assert.True(output.Length > 0, $"Scenario '{scenario}' produced no output");
        }

        [Fact]
        public void ErrorHandling_CorruptedFiles()
        {
            // Test handling of corrupted MHD files
            
            // Create a corrupted file (invalid binary data)
            var corruptedFile = Path.Combine(_testDataPath, "I12.mhd");
            File.WriteAllText(corruptedFile, "This is not valid MHD binary data!");

            var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
            var consoleOutput = new StringWriter();
            Console.SetOut(consoleOutput);

            // Act - should not throw
            var exception = Record.Exception(() => exporter.Export());

            // Assert
            Assert.Null(exception);
            var output = consoleOutput.ToString();
            Assert.Contains("ERROR", output, StringComparison.OrdinalIgnoreCase);
        }

        [Fact]
        public void Output_DirectoryStructure()
        {
            // Test that output directory is created and structured correctly
            var nestedOutput = Path.Combine(_testOutputPath, "nested", "path", "output");
            var exporter = new MidsRebornExporter(_testDataPath, nestedOutput);

            // Act
            exporter.Export();

            // Assert
            Assert.True(Directory.Exists(nestedOutput), "Nested output directory should be created");
        }

        [Fact]
        public void ConsoleOutput_ProgressReporting()
        {
            // Test that progress is reported to console
            var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
            var consoleOutput = new StringWriter();
            Console.SetOut(consoleOutput);

            // Act
            exporter.Export();

            // Assert - should show progress messages
            var output = consoleOutput.ToString();
            var lines = output.Split('\n', StringSplitOptions.RemoveEmptyEntries);
            Assert.True(lines.Length > 5, "Should output multiple progress messages");
        }

        [Fact]
        public void Memory_NoLeaksInExportProcess()
        {
            // Test that export process doesn't have obvious memory leaks
            var initialMemory = GC.GetTotalMemory(true);
            
            // Run export multiple times
            for (int i = 0; i < 3; i++)
            {
                var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
                Console.SetOut(TextWriter.Null);
                exporter.Export();
            }

            // Force garbage collection
            GC.Collect();
            GC.WaitForPendingFinalizers();
            GC.Collect();

            var finalMemory = GC.GetTotalMemory(true);
            var memoryGrowth = finalMemory - initialMemory;

            // Memory growth should be reasonable (less than 50MB)
            Assert.True(memoryGrowth < 50 * 1024 * 1024,
                $"Excessive memory growth: {memoryGrowth / 1024 / 1024}MB");
        }
    }
}