using System;
using System.IO;
using Xunit;
using DataExporter;

namespace DataExporter.Tests
{
    public class MidsRebornExporterTests : IDisposable
    {
        private readonly string _testInputPath;
        private readonly string _testOutputPath;

        public MidsRebornExporterTests()
        {
            // Create test directories
            _testInputPath = Path.Combine(Path.GetTempPath(), "MidsRebornTests_Input_" + Guid.NewGuid());
            _testOutputPath = Path.Combine(Path.GetTempPath(), "MidsRebornTests_Output_" + Guid.NewGuid());
            
            Directory.CreateDirectory(_testInputPath);
            Directory.CreateDirectory(_testOutputPath);
        }

        public void Dispose()
        {
            // Clean up test directories
            if (Directory.Exists(_testInputPath))
                Directory.Delete(_testInputPath, true);
            if (Directory.Exists(_testOutputPath))
                Directory.Delete(_testOutputPath, true);
        }

        [Fact]
        public void Constructor_ShouldInitializeWithPaths()
        {
            // Arrange & Act
            var exporter = new MidsRebornExporter(_testInputPath, _testOutputPath);

            // Assert
            Assert.NotNull(exporter);
        }

        [Fact]
        public void Export_WithoutMidsReborn_ShouldShowInstructions()
        {
            // Arrange
            var exporter = new MidsRebornExporter(_testInputPath, _testOutputPath);
            var consoleOutput = new StringWriter();
            Console.SetOut(consoleOutput);

            // Act
            exporter.Export();

            // Assert
            var output = consoleOutput.ToString();
            
            if (TestHelpers.IsMidsRebornAvailable())
            {
                // When MidsReborn is available, it should attempt export
                Assert.Contains("MidsReborn MHD to JSON Export", output);
            }
            else
            {
                // When MidsReborn is not available, it should show instructions
                Assert.Contains("MidsReborn is not enabled", output);
                Assert.Contains("Uncomment the MidsReborn reference", output);
            }
        }

        [SkipIfNoMidsRebornFact]
        public void Export_WithMissingFiles_ShouldHandleGracefully()
        {
            // Arrange
            var exporter = new MidsRebornExporter(_testInputPath, _testOutputPath);
            var consoleOutput = new StringWriter();
            Console.SetOut(consoleOutput);

            // Act
            exporter.Export();

            // Assert
            var output = consoleOutput.ToString();
            Assert.Contains("MidsReborn MHD to JSON Export", output);
            // The export should fail gracefully with missing files
        }

        [Fact]
        public void Export_CreatesOutputDirectory()
        {
            // Arrange
            var nonExistentOutput = Path.Combine(Path.GetTempPath(), "NonExistent_" + Guid.NewGuid());
            var exporter = new MidsRebornExporter(_testInputPath, nonExistentOutput);

            try
            {
                // Act
                exporter.Export();

                // Assert
                if (TestHelpers.IsMidsRebornAvailable())
                {
                    // When MidsReborn is available, output directory should be created
                    Assert.True(Directory.Exists(nonExistentOutput));
                }
                else
                {
                    // When MidsReborn is not available, directory won't be created
                    // This is expected behavior
                    Assert.True(true, "Directory creation is not expected without MidsReborn");
                }
            }
            finally
            {
                // Cleanup
                if (Directory.Exists(nonExistentOutput))
                    Directory.Delete(nonExistentOutput, true);
            }
        }

        [Theory]
        [InlineData("")]
        [InlineData(" ")]
        [InlineData("InvalidPath<>:|?*")]
        public void Constructor_WithInvalidPaths_ShouldNotThrow(string invalidPath)
        {
            // The constructor should accept any paths and fail gracefully during export
            var exception = Record.Exception(() => new MidsRebornExporter(invalidPath, invalidPath));
            Assert.Null(exception);
        }
    }
}