"""
Report generation utilities for agentic AI FMEA.

This module provides functions for generating Markdown and HTML reports
from FMEA entries and analysis results.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path
import base64
import io

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .entry import FMEAEntry, FMEAReport
from .risk import RiskCalculator
from .taxonomy import TaxonomyLoader


class FMEAReportGenerator:
    """Generates various types of reports from FMEA data."""

    def __init__(
        self, risk_calculator: Optional[RiskCalculator] = None,
        taxonomy_loader: Optional[TaxonomyLoader] = None
    ):
        """
        Initialize the report generator.

        Args:
            risk_calculator: Risk calculator instance. If None, creates default.
            taxonomy_loader: Taxonomy loader instance. If None, creates default.
        """
        self.risk_calculator = risk_calculator or RiskCalculator()
        self.taxonomy_loader = taxonomy_loader or TaxonomyLoader()
        
        # Set up Jinja2 template environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=select_autoescape(['html', 'xml'])
        )

    def generate_markdown_report(self, report: FMEAReport, include_charts: bool = True, 
                                chart_dir: str = "charts") -> str:
        """
        Generate a comprehensive Markdown report with optional visualizations.
        
        Args:
            report: FMEA report to generate
            include_charts: Whether to generate and include charts
            chart_dir: Directory to save charts (relative to markdown file)
        """
        markdown = self._generate_markdown_header(report)
        markdown += self._generate_markdown_summary(report)
        markdown += self._generate_markdown_risk_analysis(report)
        
        # Add visual risk assessment section if charts are enabled
        if include_charts:
            markdown += self._generate_markdown_visual_assessment(report, chart_dir)
        
        markdown += self._generate_markdown_taxonomy_guidance(report)
        markdown += self._generate_markdown_entries_table(report)
        markdown += self._generate_markdown_detailed_entries(report)
        markdown += self._generate_markdown_recommendations(report)

        return markdown

    def _generate_markdown_header(self, report: FMEAReport) -> str:
        """Generate Markdown header section."""
        return f"""# FMEA Report: {report.title}

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Created by:** {report.created_by}
**Version:** {report.version}

## System Description

{report.system_description}

"""

    def _generate_markdown_summary(self, report: FMEAReport) -> str:
        """Generate Markdown summary section."""
        risk_analysis = self.risk_calculator.analyze_report_risk(report)
        
        # Handle empty reports
        if "error" in risk_analysis:
            return f"""## Executive Summary

- **Total Failure Modes Analyzed:** 0
- **Status:** No entries to analyze

"""
        
        stats = risk_analysis["statistics"]
        risk_dist = risk_analysis["risk_distribution"]

        critical_pct = risk_dist['Critical'] / stats['total_entries'] * 100
        high_pct = risk_dist['High'] / stats['total_entries'] * 100
        medium_pct = risk_dist['Medium'] / stats['total_entries'] * 100
        low_pct = risk_dist['Low'] / stats['total_entries'] * 100

        return f"""## Executive Summary

- **Total Failure Modes Analyzed:** {stats['total_entries']}
- **Mean RPN:** {stats['mean_rpn']:.1f}
- **Median RPN:** {stats['median_rpn']:.1f}
- **Maximum RPN:** {stats['max_rpn']}

### Risk Distribution

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical   | {risk_dist['Critical']} | {critical_pct:.1f}% |
| High       | {risk_dist['High']} | {high_pct:.1f}% |
| Medium     | {risk_dist['Medium']} | {medium_pct:.1f}% |
| Low        | {risk_dist['Low']} | {low_pct:.1f}% |

"""

    def _generate_markdown_risk_analysis(self, report: FMEAReport) -> str:
        """Generate Markdown risk analysis section."""
        risk_analysis = self.risk_calculator.analyze_report_risk(report)
        
        # Handle empty reports
        if "error" in risk_analysis:
            return """## Risk Analysis

*No entries available for risk analysis.*

"""
        
        top_risks = risk_analysis["top_risks"]
        subsystem_risk = risk_analysis["subsystem_risk"]

        markdown = """## Risk Analysis

### Top Risk Entries

| Rank | Entry ID | Taxonomy ID | RPN | Risk Level |
|------|----------|-------------|-----|------------|
"""

        for i, risk in enumerate(top_risks[:10], 1):
            entry = next((e for e in report.entries if e.id == risk["id"]), None)
            if entry:
                risk_level = self.risk_calculator.thresholds.categorize_rpn(entry.rpn)
                markdown += (
                    f"| {i} | {entry.id} | {entry.taxonomy_id} | {entry.rpn} | "
                    f"{risk_level.value} |\n"
                )

        markdown += "\n### Risk by Subsystem\n\n"
        markdown += "| Subsystem | Count | Avg RPN | Max RPN |\n"
        markdown += "|-----------|-------|---------|--------|\n"

        for subsystem, data in sorted(
            subsystem_risk.items(),
            key=lambda x: x[1]["avg_rpn"], reverse=True
        ):
            markdown += (
                f"| {subsystem} | {data['count']} | {data['avg_rpn']:.1f} | "
                f"{data['max_rpn']} |\n"
            )

        return markdown + "\n"

    def _generate_markdown_visual_assessment(self, report: FMEAReport, chart_dir: str) -> str:
        """Generate visual risk assessment section with charts."""
        if not report.entries:
            return """## Visual Risk Assessment

*No data available for visualization.*

"""
        
        markdown = """## Visual Risk Assessment

This section provides visual analysis of the identified risks to help understand patterns, distributions, and priorities.

"""
        
        try:
            # Generate all charts and get their paths
            chart_paths = self.risk_calculator.generate_comprehensive_charts(
                report, output_dir=chart_dir, formats=['png']
            )
            
            # Add each chart with description
            chart_descriptions = {
                'risk_distribution': {
                    'title': 'Risk Level Distribution',
                    'description': 'Shows the distribution of entries across risk levels and the frequency distribution of RPN values. The left chart shows how many entries fall into each risk category, while the right chart shows the statistical distribution of RPN scores with threshold lines.'
                },
                'risk_matrix': {
                    'title': 'Risk Matrix',
                    'description': 'Traditional FMEA risk matrix plotting severity versus occurrence. Each cell shows the total RPN for entries in that severity-occurrence combination. Background colors indicate risk regions.'
                },
                'subsystem_comparison': {
                    'title': 'Subsystem Risk Analysis',
                    'description': 'Compares risk levels across different system components. The top chart shows average RPN by subsystem with risk threshold lines, while the bottom shows the number of identified failure modes per subsystem.'
                },
                'taxonomy_breakdown': {
                    'title': 'Failure Mode Taxonomy Analysis',
                    'description': 'Analysis of failure modes by their taxonomy categories. The pie chart shows the distribution of different failure mode types, while the bar chart shows average risk levels for each taxonomy category.'
                },
                'mitigation_analysis': {
                    'title': 'Mitigation Strategy Effectiveness',
                    'description': 'Analyzes the relationship between the number of mitigation strategies and risk levels. The scatter plot shows individual entries colored by risk level, while the histogram shows how mitigation strategies are distributed across entries.'
                }
            }
            
            for chart_name, chart_path in chart_paths.items():
                if chart_name in chart_descriptions:
                    chart_info = chart_descriptions[chart_name]
                    
                    markdown += f"""### {chart_info['title']}

{chart_info['description']}

![{chart_info['title']}]({chart_path})

"""
            
            # Add interpretation section
            markdown += self._generate_chart_interpretation(report)
            
        except Exception as e:
            markdown += f"*Chart generation failed: {e}*\n\n"
        
        return markdown

    def _generate_chart_interpretation(self, report: FMEAReport) -> str:
        """Generate interpretation and insights from the visual data."""
        analysis = self.risk_calculator.analyze_report_risk(report)
        
        if "error" in analysis:
            return ""
        
        stats = analysis["statistics"]
        risk_dist = analysis["risk_distribution"]
        
        interpretation = """### Key Visual Insights

"""
        
        # Risk distribution insights
        total_entries = stats['total_entries']
        critical_count = risk_dist.get('Critical', 0)
        high_count = risk_dist.get('High', 0)
        
        if critical_count > 0:
            critical_pct = (critical_count / total_entries) * 100
            interpretation += f"- **Critical Risk Alert**: {critical_count} entries ({critical_pct:.1f}%) are at critical risk levels, requiring immediate attention.\n"
        
        if high_count > 0:
            high_pct = (high_count / total_entries) * 100
            interpretation += f"- **High Risk Concentration**: {high_count} entries ({high_pct:.1f}%) are at high risk levels.\n"
        
        # RPN distribution insights
        mean_rpn = stats['mean_rpn']
        max_rpn = stats['max_rpn']
        
        if mean_rpn > self.risk_calculator.thresholds.high:
            interpretation += f"- **Elevated Average Risk**: Mean RPN of {mean_rpn:.1f} exceeds high-risk threshold, indicating systemic risk issues.\n"
        
        # Subsystem insights
        subsystem_risk = analysis.get("subsystem_risk", {})
        if subsystem_risk:
            highest_risk_subsystem = max(subsystem_risk.items(), 
                                       key=lambda x: x[1]["avg_rpn"])
            interpretation += f"- **Highest Risk Subsystem**: {highest_risk_subsystem[0]} shows the highest average risk level ({highest_risk_subsystem[1]['avg_rpn']:.1f} RPN).\n"
        
        # Mitigation insights
        mitigation_counts = [len(entry.mitigation) for entry in report.entries]
        avg_mitigations = sum(mitigation_counts) / len(mitigation_counts) if mitigation_counts else 0
        
        if avg_mitigations < 2:
            interpretation += f"- **Mitigation Gap**: Average of {avg_mitigations:.1f} mitigation strategies per entry suggests need for additional risk controls.\n"
        
        interpretation += "\n"
        return interpretation

    def _generate_markdown_taxonomy_guidance(self, report: FMEAReport) -> str:
        """Generate Markdown section showing taxonomy-specific guidance summary."""
        if not report.entries:
            return """## AI Safety Knowledge Base Summary

*No entries available for taxonomy guidance.*

"""
        
        markdown = """## AI Safety Knowledge Base Summary

This section provides domain-specific guidance from the Microsoft AI Red Team taxonomy for the failure modes identified in this analysis.

"""
        
        # Get unique taxonomy IDs from entries
        taxonomy_ids = list(set(entry.taxonomy_id for entry in report.entries))
        
        for taxonomy_id in sorted(taxonomy_ids):
            failure_mode = self.taxonomy_loader.get_failure_mode(taxonomy_id)
            if failure_mode:
                markdown += f"""### {taxonomy_id}

**Type:** {failure_mode.category.replace('_', ' ').title()} ({failure_mode.pillar.title()})
**Description:** {failure_mode.description}

"""
                
                if failure_mode.recommended_mitigations:
                    markdown += "**Key Mitigations:**\n"
                    for mitigation in failure_mode.recommended_mitigations[:3]:  # Show top 3
                        markdown += f"- {mitigation}\n"
                    markdown += "\n"
                
                if failure_mode.detection_strategies:
                    markdown += "**Detection Strategies:**\n"
                    for strategy in failure_mode.detection_strategies[:3]:  # Show top 3
                        markdown += f"- {strategy}\n"
                    markdown += "\n"
                
                if failure_mode.related_modes:
                    markdown += f"**Related Modes:** {', '.join(failure_mode.related_modes)}\n\n"
                
                markdown += "---\n\n"
        
        return markdown

    def _generate_markdown_entries_table(self, report: FMEAReport) -> str:
        """Generate Markdown table of all entries."""
        if not report.entries:
            return """## All FMEA Entries

*No entries to display.*

"""
        
        markdown = """## All FMEA Entries

| ID | Taxonomy | Subsystem | Severity | Occurrence | Detection | RPN | Risk Level |
|----|----------|-----------|----------|------------|-----------|-----|------------|
"""

        # Sort entries by RPN (highest first)
        sorted_entries = sorted(
            report.entries, key=lambda x: x.rpn, reverse=True
        )

        for entry in sorted_entries:
            risk_level = self.risk_calculator.thresholds.categorize_rpn(entry.rpn)
            markdown += (
                f"| {entry.id} | {entry.taxonomy_id} | {entry.subsystem.value} | "
                f"{entry.severity} | {entry.occurrence} | {entry.detection} | "
                f"{entry.rpn} | {risk_level.value} |\n"
            )

        return markdown + "\n"

    def _generate_markdown_detailed_entries(self, report: FMEAReport) -> str:
        """Generate detailed Markdown entries for high-risk items."""
        markdown = "## Detailed Analysis of High-Risk Entries\n\n"

        high_risk_entries = [
            entry for entry in report.entries
            if self.risk_calculator.thresholds.categorize_rpn(entry.rpn).value in ["Critical", "High"]
        ]

        if not high_risk_entries:
            return markdown + "*No high-risk entries found.*\n\n"

        # Sort by RPN
        high_risk_entries.sort(key=lambda x: x.rpn, reverse=True)

        for entry in high_risk_entries:
            failure_mode = self.taxonomy_loader.get_failure_mode(entry.taxonomy_id)
            markdown += self._generate_entry_detail(entry, failure_mode)

        return markdown

    def _generate_entry_detail(self, entry: FMEAEntry, failure_mode) -> str:
        """Generate detailed markdown for a single entry."""
        risk_score = self.risk_calculator.calculate_risk_score(entry)
        basic_recommendations = self.risk_calculator.recommend_actions(entry)
        detailed_recommendations = self.risk_calculator.get_detailed_recommendations(entry)

        markdown = f"""### {entry.id}

**Taxonomy:** {entry.taxonomy_id}
**System Type:** {entry.system_type.value}
**Subsystem:** {entry.subsystem.value}
**RPN:** {entry.rpn} ({risk_score['risk_level'].value})

**Failure Mode Description:**
{failure_mode.description if failure_mode else 'N/A'}

**Cause:** {entry.cause}

**Effect:** {entry.effect}

**Risk Assessment:**
- Severity: {entry.severity}/10 ({risk_score['severity_label']})
- Occurrence: {entry.occurrence}/10 ({risk_score['occurrence_label']})
- Detection: {entry.detection}/10 ({risk_score['detection_label']})

**Detection Method:** {entry.detection_method.value}

**Current Mitigation Strategies:**
"""

        for mitigation in entry.mitigation:
            markdown += f"- {mitigation}\n"

        # Add general recommendations
        markdown += "\n**General Recommended Actions:**\n"
        for recommendation in detailed_recommendations["general_actions"]:
            markdown += f"- {recommendation}\n"

        # Add taxonomy-specific guidance
        if detailed_recommendations["taxonomy_specific"].get("recommended_mitigations"):
            markdown += "\n**Failure Mode Specific Mitigations:**\n"
            for mitigation in detailed_recommendations["taxonomy_specific"]["recommended_mitigations"]:
                markdown += f"- {mitigation}\n"

        if detailed_recommendations["taxonomy_specific"].get("detection_strategies"):
            markdown += "\n**Detection Strategies:**\n"
            for strategy in detailed_recommendations["taxonomy_specific"]["detection_strategies"]:
                markdown += f"- {strategy}\n"

        if detailed_recommendations["taxonomy_specific"].get("implementation_notes"):
            markdown += "\n**Implementation Notes:**\n"
            for note in detailed_recommendations["taxonomy_specific"]["implementation_notes"]:
                markdown += f"- {note}\n"

        if detailed_recommendations["taxonomy_specific"].get("related_modes"):
            markdown += "\n**Related Failure Modes:**\n"
            for related in detailed_recommendations["taxonomy_specific"]["related_modes"]:
                markdown += f"- {related}\n"

        if entry.scenario:
            markdown += f"\n**Scenario:** {entry.scenario}\n"

        markdown += "\n---\n\n"

        return markdown

    def _generate_markdown_recommendations(self, report: FMEAReport) -> str:
        """Generate Markdown recommendations section."""
        high_risk_count = len([
            e for e in report.entries if self.risk_calculator.thresholds.categorize_rpn(e.rpn).value in ["Critical", "High"]
        ])

        markdown = """## Recommendations

### Immediate Actions Required

"""

        if high_risk_count > 0:
            markdown += (
                f"There are {high_risk_count} high-risk or critical entries that "
                f"require immediate attention:\n\n"
            )

            critical_entries = [
                e for e in report.entries if self.risk_calculator.thresholds.categorize_rpn(e.rpn).value == "Critical"
            ]
            high_entries = [
                e for e in report.entries if self.risk_calculator.thresholds.categorize_rpn(e.rpn).value == "High"
            ]

            if critical_entries:
                markdown += "**Critical Risk Entries:**\n"
                for entry in critical_entries:
                    markdown += (
                        f"- {entry.id}: {entry.taxonomy_id} (RPN: {entry.rpn})\n"
                    )
                markdown += "\n"

            if high_entries:
                markdown += "**High Risk Entries:**\n"
                for entry in high_entries:
                    markdown += (
                        f"- {entry.id}: {entry.taxonomy_id} (RPN: {entry.rpn})\n"
                    )
                markdown += "\n"
        else:
            markdown += "No critical or high-risk entries identified.\n\n"

        markdown += (
            """### General Recommendations

1. **Implement Continuous Monitoring:** Establish monitoring systems for all """
            + """failure modes with RPN > 100
2. **Regular Review Cycles:** Schedule quarterly reviews of this FMEA analysis
3. **Incident Response:** Develop incident response procedures for high-risk """
            + """scenarios
4. **Training:** Ensure team members are trained on identified failure modes """
            + """and mitigations
5. **Documentation:** Keep this FMEA analysis updated as the system evolves

### Next Steps

1. Prioritize mitigation efforts based on RPN rankings
2. Implement recommended actions for critical and high-risk entries
3. Establish monitoring and detection mechanisms
4. Schedule follow-up assessment in 3 months
5. Update this analysis when system architecture changes

"""
        )

        return markdown

    def save_markdown_report(self, report: FMEAReport, output_path: str, 
                           include_charts: bool = True, chart_dir: str = None) -> None:
        """
        Save Markdown report to file with optional chart generation.
        
        Args:
            report: FMEA report to save
            output_path: Path to save the markdown file
            include_charts: Whether to generate and include charts
            chart_dir: Directory for charts (relative to markdown file). 
                      If None, uses 'charts' subdirectory next to markdown file.
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Determine chart directory
        if chart_dir is None:
            chart_dir = output_path.parent / "charts"
        else:
            chart_dir = Path(chart_dir)
        
        # Generate markdown with relative chart paths
        if include_charts:
            # Use relative path from markdown file to charts
            relative_chart_dir = chart_dir.relative_to(output_path.parent)
            markdown_content = self.generate_markdown_report(report, include_charts=True, 
                                                           chart_dir=str(relative_chart_dir))
        else:
            markdown_content = self.generate_markdown_report(report, include_charts=False)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)

    def generate_csv_export(self, report: FMEAReport) -> str:
        """Generate CSV export of FMEA entries."""
        csv_content = (
            "ID,Taxonomy_ID,System_Type,Subsystem,Cause,Effect,Severity,Occurrence,"
            "Detection,RPN,Risk_Level,Detection_Method,Created_Date,Created_By\n"
        )

        for entry in report.entries:
            risk_level = self.risk_calculator.thresholds.categorize_rpn(entry.rpn)
            csv_content += (
                f'"{entry.id}","{entry.taxonomy_id}","{entry.system_type.value}",'
                f'"{entry.subsystem.value}","{entry.cause}","{entry.effect}",'
                f'{entry.severity},{entry.occurrence},{entry.detection},'
                f'{entry.rpn},"{risk_level.value}","{entry.detection_method.value}",'
                f'"{entry.created_date.isoformat()}","{entry.created_by}"\n'
            )

        return csv_content

    def save_csv_export(self, report: FMEAReport, output_path: str) -> None:
        """Save CSV export to file."""
        csv_content = self.generate_csv_export(report)

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)

    def generate_html_report(self, report: FMEAReport, include_charts: bool = True) -> str:
        """
        Generate professional HTML report using Jinja2 templates.
        
        Args:
            report: FMEA report to generate HTML for
            include_charts: Whether to include embedded visualizations
            
        Returns:
            Complete HTML report as string
        """
        # Generate charts if requested
        charts = {}
        if include_charts and report.entries:
            charts = self._generate_chart_images(report)
        
        # Analyze risk data
        risk_analysis = self.risk_calculator.analyze_report_risk(report)
        
        # Prepare template context
        context = self._prepare_template_context(report, risk_analysis, charts)
        
        # Render the main template
        template = self.jinja_env.get_template('base_report.html')
        return template.render(**context)

    def _generate_chart_images(self, report: FMEAReport) -> Dict[str, str]:
        """
        Generate base64 encoded chart images for embedding in HTML.
        
        Args:
            report: FMEA report to generate charts for
            
        Returns:
            Dictionary mapping chart names to base64 data URIs
        """
        charts = {}
        
        try:
            import matplotlib.pyplot as plt
            
            # Use the comprehensive chart generation from RiskCalculator
            chart_methods = {
                'risk_distribution': self.risk_calculator.plot_risk_distribution,
                'risk_matrix': self.risk_calculator.plot_risk_matrix,
                'subsystem_comparison': self.risk_calculator.plot_subsystem_comparison,
                'taxonomy_breakdown': self.risk_calculator.plot_taxonomy_breakdown,
                'mitigation_analysis': self.risk_calculator.plot_mitigation_analysis
            }
            
            for chart_name, chart_method in chart_methods.items():
                try:
                    if chart_name == 'risk_matrix':
                        # Special handling for risk matrix with custom title
                        fig = chart_method(report.entries, title="Risk Matrix: Severity vs Occurrence")
                    else:
                        fig = chart_method(report)
                    
                    charts[chart_name] = self._figure_to_base64(fig)
                    plt.close(fig)
                    
                except Exception as e:
                    print(f"Warning: Failed to generate {chart_name}: {e}")
                    continue
            
        except Exception as e:
            # If chart generation fails, continue without charts
            print(f"Warning: Chart generation failed: {e}")
            
        return charts
    
    def _figure_to_base64(self, fig) -> str:
        """
        Convert matplotlib figure to base64 data URI.
        
        Args:
            fig: Matplotlib figure object
            
        Returns:
            Base64 data URI string
        """
        # Save figure to bytes buffer
        buffer = io.BytesIO()
        fig.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        
        # Encode to base64
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()
        
        # Return as data URI
        return f"data:image/png;base64,{image_base64}"
    
    def _prepare_template_context(self, report: FMEAReport, risk_analysis: Dict[str, Any], charts: Dict[str, str]) -> Dict[str, Any]:
        """
        Prepare the context dictionary for Jinja2 template rendering.
        
        Args:
            report: FMEA report
            risk_analysis: Risk analysis results
            charts: Base64 encoded chart images
            
        Returns:
            Template context dictionary
        """
        # Handle empty reports
        if "error" in risk_analysis:
            statistics = {"total_entries": 0, "mean_rpn": 0, "max_rpn": 0, "median_rpn": 0}
            risk_distribution = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        else:
            statistics = risk_analysis["statistics"]
            risk_distribution = risk_analysis["risk_distribution"]
        
        # Sort entries by RPN (highest first)
        sorted_entries = sorted(report.entries, key=lambda x: x.rpn, reverse=True)
        
        # Add risk level to each entry for template convenience
        for entry in sorted_entries:
            entry.risk_level = self.risk_calculator.thresholds.categorize_rpn(entry.rpn)
            entry.severity_label = self.risk_calculator._get_severity_label(entry.severity)
            entry.occurrence_label = self.risk_calculator._get_occurrence_label(entry.occurrence)
            entry.detection_label = self.risk_calculator._get_detection_label(entry.detection)
        
        # Get high-risk entries for detailed analysis
        high_risk_entries = [
            entry for entry in sorted_entries
            if self.risk_calculator.thresholds.categorize_rpn(entry.rpn).value in ["Critical", "High"]
        ]
        
        # Prepare detailed recommendations for high-risk entries
        for entry in high_risk_entries:
            entry.detailed_recommendations = self.risk_calculator.get_detailed_recommendations(entry)
            entry.failure_mode = self.taxonomy_loader.get_failure_mode(entry.taxonomy_id)
        
        # Get unique taxonomy IDs for knowledge base
        unique_taxonomy_ids = list(set(entry.taxonomy_id for entry in report.entries))
        
        # Group entries by taxonomy for knowledge base section
        entries_by_taxonomy = {}
        for entry in report.entries:
            if entry.taxonomy_id not in entries_by_taxonomy:
                entries_by_taxonomy[entry.taxonomy_id] = []
            entries_by_taxonomy[entry.taxonomy_id].append(entry)
        
        # Separate entries by risk level for recommendations
        critical_entries = [
            entry for entry in sorted_entries
            if self.risk_calculator.thresholds.categorize_rpn(entry.rpn).value == "Critical"
        ]
        high_entries = [
            entry for entry in sorted_entries
            if self.risk_calculator.thresholds.categorize_rpn(entry.rpn).value == "High"
        ]
        
        return {
            'report': report,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'statistics': statistics,
            'risk_distribution': risk_distribution,
            'risk_analysis': risk_analysis,
            'charts': charts,
            'sorted_entries': sorted_entries,
            'high_risk_entries': high_risk_entries,
            'critical_entries': critical_entries,
            'high_entries': high_entries,
            'unique_taxonomy_ids': sorted(unique_taxonomy_ids),
            'entries_by_taxonomy': entries_by_taxonomy,
            'taxonomy_loader': self.taxonomy_loader,
        }

    def save_html_report(self, report: FMEAReport, output_path: str, include_charts: bool = True) -> None:
        """Save professional HTML report to file."""
        html_content = self.generate_html_report(report, include_charts)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
