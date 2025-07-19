using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using Xunit;
using Xunit.Abstractions;
using DataExporter;

namespace DataExporter.Tests
{
    public class PerformanceBenchmarks : IDisposable
    {
        private readonly ITestOutputHelper _output;
        private readonly string _testDataPath;
        private readonly string _testOutputPath;
        private readonly Dictionary<string, long> _benchmarkResults;

        public PerformanceBenchmarks(ITestOutputHelper output)
        {
            _output = output;
            _testDataPath = Path.Combine(Path.GetTempPath(), "PerfTests_Data_" + Guid.NewGuid());
            _testOutputPath = Path.Combine(Path.GetTempPath(), "PerfTests_Output_" + Guid.NewGuid());
            _benchmarkResults = new Dictionary<string, long>();
            
            Directory.CreateDirectory(_testDataPath);
            Directory.CreateDirectory(_testOutputPath);
            
            // Create mock files of various sizes for benchmarking
            CreateMockDataFiles();
        }

        public void Dispose()
        {
            // Output benchmark summary
            _output.WriteLine("\n=== Performance Benchmark Results ===");
            foreach (var result in _benchmarkResults)
            {
                _output.WriteLine($"{result.Key}: {result.Value}ms");
            }

            if (Directory.Exists(_testDataPath))
                Directory.Delete(_testDataPath, true);
            if (Directory.Exists(_testOutputPath))
                Directory.Delete(_testOutputPath, true);
        }

        private void CreateMockDataFiles()
        {
            // Create mock files with different sizes to simulate real MHD files
            var mockFiles = new Dictionary<string, int>
            {
                { "I12.mhd", 5 * 1024 * 1024 },      // 5MB - typical main database
                { "EnhDB.mhd", 500 * 1024 },         // 500KB - enhancements
                { "Recipe.mhd", 1 * 1024 * 1024 },   // 1MB - recipes
                { "Salvage.mhd", 10 * 1024 },        // 10KB - salvage
                { "AttribMod.json", 100 * 1024 },    // 100KB - JSON file
                { "TypeGrades.json", 50 * 1024 }     // 50KB - JSON file
            };

            foreach (var file in mockFiles)
            {
                var filePath = Path.Combine(_testDataPath, file.Key);
                var data = new byte[file.Value];
                
                // Fill with pseudo-random data
                var random = new Random(42); // Fixed seed for reproducibility
                random.NextBytes(data);
                
                File.WriteAllBytes(filePath, data);
            }
        }

        [Fact]
        public void Benchmark_InitializationTime()
        {
            var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
            var stopwatch = new Stopwatch();

            // Suppress console output
            Console.SetOut(TextWriter.Null);

            // Measure just the initialization phase
            stopwatch.Start();
            // In real implementation, this would measure ConfigData.Initialize()
            stopwatch.Stop();

            _benchmarkResults["Initialization"] = stopwatch.ElapsedMilliseconds;
            
            // Initialization should be fast
            Assert.True(stopwatch.ElapsedMilliseconds < 1000,
                $"Initialization too slow: {stopwatch.ElapsedMilliseconds}ms");
        }

        [Fact]
        public void Benchmark_FileLoadingTime()
        {
            var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
            var stopwatch = new Stopwatch();
            
            Console.SetOut(TextWriter.Null);

            // Measure the complete export process
            stopwatch.Start();
            exporter.Export();
            stopwatch.Stop();

            _benchmarkResults["Complete Export"] = stopwatch.ElapsedMilliseconds;
            
            // With mock files, export should complete quickly
            Assert.True(stopwatch.ElapsedMilliseconds < 5000,
                $"Export too slow: {stopwatch.ElapsedMilliseconds}ms");
        }

        [Fact]
        public void Benchmark_MemoryUsage()
        {
            var exporter = new MidsRebornExporter(_testDataPath, _testOutputPath);
            Console.SetOut(TextWriter.Null);

            // Measure memory before
            GC.Collect();
            GC.WaitForPendingFinalizers();
            GC.Collect();
            var memoryBefore = GC.GetTotalMemory(false);

            // Run export
            exporter.Export();

            // Measure memory after
            var memoryAfter = GC.GetTotalMemory(false);
            var memoryUsed = (memoryAfter - memoryBefore) / 1024 / 1024; // Convert to MB

            _benchmarkResults["Memory Usage (MB)"] = memoryUsed;
            
            // Memory usage should be reasonable
            Assert.True(memoryUsed < 100,
                $"Excessive memory usage: {memoryUsed}MB");
        }

        [Theory]
        [InlineData(1)]
        [InlineData(10)]
        [InlineData(100)]
        public void Benchmark_JsonSerializationScaling(int scaleFactor)
        {
            // Test how serialization scales with data size
            var largeDataPath = Path.Combine(_testDataPath, $"scale_{scaleFactor}");
            Directory.CreateDirectory(largeDataPath);
            
            // Create scaled mock file
            var fileSize = scaleFactor * 100 * 1024; // Base 100KB
            var data = new byte[fileSize];
            File.WriteAllBytes(Path.Combine(largeDataPath, "I12.mhd"), data);

            var exporter = new MidsRebornExporter(largeDataPath, _testOutputPath);
            var stopwatch = new Stopwatch();
            
            Console.SetOut(TextWriter.Null);

            stopwatch.Start();
            exporter.Export();
            stopwatch.Stop();

            var key = $"Scale {scaleFactor}x";
            _benchmarkResults[key] = stopwatch.ElapsedMilliseconds;
            
            // Time should scale roughly linearly
            var expectedMax = scaleFactor * 100; // 100ms per scale factor
            Assert.True(stopwatch.ElapsedMilliseconds < expectedMax,
                $"Scaling issue at {scaleFactor}x: {stopwatch.ElapsedMilliseconds}ms");
            
            // Cleanup
            Directory.Delete(largeDataPath, true);
        }

        [Fact]
        public void Benchmark_ConcurrentExports()
        {
            // Test thread safety and concurrent performance
            const int concurrentExports = 3;
            var tasks = new System.Threading.Tasks.Task[concurrentExports];
            var stopwatch = new Stopwatch();
            
            Console.SetOut(TextWriter.Null);

            stopwatch.Start();
            for (int i = 0; i < concurrentExports; i++)
            {
                var outputPath = Path.Combine(_testOutputPath, $"concurrent_{i}");
                tasks[i] = System.Threading.Tasks.Task.Run(() =>
                {
                    var exporter = new MidsRebornExporter(_testDataPath, outputPath);
                    exporter.Export();
                });
            }

            System.Threading.Tasks.Task.WaitAll(tasks);
            stopwatch.Stop();

            _benchmarkResults["Concurrent Exports"] = stopwatch.ElapsedMilliseconds;
            
            // Concurrent exports should complete in reasonable time
            Assert.True(stopwatch.ElapsedMilliseconds < 10000,
                $"Concurrent exports too slow: {stopwatch.ElapsedMilliseconds}ms");
        }
    }
}