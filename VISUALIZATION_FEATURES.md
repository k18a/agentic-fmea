# Enhanced Visualization Features

This document describes the new automated visualization features implemented for the agentic-fmea library.

## Overview

The enhanced visualization system provides professional, automatically-generated charts that are seamlessly integrated into both Markdown and HTML reports. The system includes multiple chart types, professional styling themes, and automated report generation with visual risk assessment sections.

## Key Features Implemented

### 1. Professional Chart Themes

**Location**: `agentic_fmea/risk.py` - `ChartTheme` and `ChartThemes` classes

- **Professional Theme**: Corporate-style charts with consistent branding
- **Academic Theme**: Presentation-ready charts for research contexts  
- **Colorblind-Friendly Theme**: Accessible color palettes for inclusive design
- **Consistent Styling**: Risk-level color coding across all visualizations
- **High-DPI Output**: 150 DPI resolution for crisp presentations

### 2. Expanded Visualization Types

**Location**: `agentic_fmea/risk.py` - New `RiskCalculator` methods

#### Core Charts
- **Risk Distribution**: Bar chart of risk levels + RPN histogram with statistics
- **Risk Matrix**: Traditional FMEA matrix with severity vs occurrence plotting
- **Subsystem Comparison**: Average RPN and entry counts by system component
- **Taxonomy Breakdown**: Pie chart and bar analysis of failure mode categories
- **Mitigation Analysis**: Scatter plot and histogram of mitigation effectiveness

#### Advanced Features
- **Risk Region Overlays**: Color-coded background regions on risk matrices
- **Threshold Lines**: Visual risk level boundaries on all relevant charts
- **Trend Analysis**: Polynomial trend lines for mitigation effectiveness
- **Statistical Annotations**: Mean, median, max values displayed on charts
- **Professional Styling**: Consistent fonts, colors, and layout

### 3. Automated Chart Generation

**Location**: `agentic_fmea/risk.py` - `generate_comprehensive_charts()` method

- **Batch Generation**: All charts created in one call
- **Multiple Formats**: PNG, SVG, PDF output support
- **Error Handling**: Graceful failure with warnings, continues processing
- **Configurable Output**: Custom directories and file naming
- **Memory Management**: Automatic cleanup of matplotlib figures

### 4. Enhanced Markdown Reports

**Location**: `agentic_fmea/report.py` - Enhanced `FMEAReportGenerator`

#### New Visual Risk Assessment Section
- **Automatic Chart Inclusion**: Charts generated and referenced automatically
- **Professional Descriptions**: Detailed explanations for each chart type
- **Key Insights Generation**: AI-generated interpretation of visual patterns
- **Relative Path Handling**: Proper linking between markdown and chart files

#### Chart Descriptions Included
- Risk Level Distribution analysis
- Risk Matrix methodology explanation  
- Subsystem risk comparison insights
- Taxonomy category breakdown
- Mitigation strategy effectiveness analysis

#### Automated Insights
- Critical risk alerts with percentages
- High-risk concentration analysis
- Elevated average risk warnings
- Highest-risk subsystem identification
- Mitigation gap analysis

### 5. Enhanced HTML Reports

**Location**: `agentic_fmea/report.py` - Updated chart embedding

- **All Chart Types**: Now includes all 5 visualization types
- **Base64 Embedding**: Charts embedded directly in HTML for portability
- **Error Resilience**: Continues generation even if some charts fail
- **Professional Integration**: Charts styled to match existing HTML theme

### 6. Chart Customization Options

#### Theme Selection
```python
from agentic_fmea.risk import RiskCalculator, ChartThemes

# Professional corporate theme
calculator = RiskCalculator(chart_theme=ChartThemes.professional())

# Academic presentation theme  
calculator = RiskCalculator(chart_theme=ChartThemes.academic())

# Colorblind-friendly theme
calculator = RiskCalculator(chart_theme=ChartThemes.colorblind_friendly())
```

#### Comprehensive Chart Generation
```python
# Generate all charts with multiple formats
chart_paths = calculator.generate_comprehensive_charts(
    report, 
    output_dir="risk_charts",
    formats=['png', 'svg', 'pdf']
)
```

#### Enhanced Report Generation
```python
from agentic_fmea.report import FMEAReportGenerator

generator = FMEAReportGenerator()

# Markdown with automated charts
generator.save_markdown_report(
    report, 
    "output/report.md",
    include_charts=True,
    chart_dir="charts"
)

# HTML with embedded charts
generator.save_html_report(
    report,
    "output/report.html", 
    include_charts=True
)
```

## Testing and Validation

**Test File**: `test_enhanced_visualizations.py`

Comprehensive test suite covering:
- ✅ Chart theme functionality
- ✅ Comprehensive chart generation
- ✅ Markdown report with charts
- ✅ HTML report with embedded charts
- ✅ Memory poisoning case study validation

## Files Generated

### Test Outputs
- `test_charts/` - Individual chart files in PNG and SVG formats
- `docs/enhanced_memory_poisoning_report.md` - Enhanced markdown report
- `docs/enhanced_memory_poisoning_report.html` - Enhanced HTML report
- `charts/` - Chart files for markdown report

### Chart Types Generated
1. `risk_distribution.png` - Risk levels and RPN distribution
2. `risk_matrix.png` - Traditional FMEA risk matrix
3. `subsystem_comparison.png` - Risk analysis by subsystem
4. `taxonomy_breakdown.png` - Failure mode taxonomy analysis
5. `mitigation_analysis.png` - Mitigation strategy effectiveness

## Key Benefits

### For Users
- **Automatic Visualization**: No manual chart creation required
- **Professional Quality**: Publication-ready charts with consistent styling
- **Comprehensive Analysis**: Multiple perspectives on risk data
- **Accessible Design**: Colorblind-friendly options available
- **Actionable Insights**: AI-generated interpretation of visual patterns

### For Reports
- **Enhanced Readability**: Visual elements improve comprehension
- **Professional Appearance**: Consistent branding and styling
- **Comprehensive Coverage**: All key risk metrics visualized
- **Flexible Output**: Multiple formats for different use cases
- **Self-Contained**: Charts embedded or properly linked

### For Development
- **Modular Design**: Easy to extend with new chart types
- **Error Resilient**: Graceful handling of visualization failures
- **Memory Efficient**: Proper cleanup of matplotlib resources
- **Configurable**: Themes and output options easily customized

## Integration with Existing Features

The new visualization features are fully integrated with existing agentic-fmea functionality:

- **Risk Calculator**: Enhanced with new visualization methods
- **Report Generator**: Updated to include visual sections
- **HTML Templates**: Compatible with existing styling
- **Taxonomy System**: Visualizations leverage taxonomy data
- **FMEA Methodology**: Charts follow traditional FMEA principles

## Future Enhancements

Potential areas for future development:
- Interactive charts for web interfaces
- Real-time risk monitoring dashboards  
- Comparative analysis across multiple reports
- Time-series risk trend analysis
- Custom chart templates for specific industries
- Integration with external visualization libraries

## Performance Notes

- Chart generation adds ~2-3 seconds to report generation
- Memory usage peaks during matplotlib operations
- SVG format recommended for scalable output
- PNG format optimal for web embedding
- PDF format best for print documentation

The enhanced visualization system transforms agentic-fmea from a data analysis tool into a comprehensive visual risk assessment platform, making complex risk patterns immediately apparent and actionable for stakeholders at all technical levels.