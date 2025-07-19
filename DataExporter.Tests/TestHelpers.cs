using System;
using Xunit;

namespace DataExporter.Tests
{
    /// <summary>
    /// Helper class for test conditions
    /// </summary>
    public static class TestHelpers
    {
        /// <summary>
        /// Checks if MidsReborn is available for testing
        /// </summary>
        public static bool IsMidsRebornAvailable()
        {
#if MIDSREBORN
            return true;
#else
            return false;
#endif
        }
    }

    /// <summary>
    /// Skip test if MidsReborn is not available
    /// </summary>
    public class SkipIfNoMidsRebornFactAttribute : FactAttribute
    {
        public SkipIfNoMidsRebornFactAttribute()
        {
            if (!TestHelpers.IsMidsRebornAvailable())
            {
                Skip = "MidsReborn is not available in this environment";
            }
        }
    }

    /// <summary>
    /// Skip theory test if MidsReborn is not available
    /// </summary>
    public class SkipIfNoMidsRebornTheoryAttribute : TheoryAttribute
    {
        public SkipIfNoMidsRebornTheoryAttribute()
        {
            if (!TestHelpers.IsMidsRebornAvailable())
            {
                Skip = "MidsReborn is not available in this environment";
            }
        }
    }
}