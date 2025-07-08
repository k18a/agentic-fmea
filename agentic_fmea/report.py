"""
Report generation utilities for agentic AI FMEA.

This module provides functions for generating Markdown and HTML reports
from FMEA entries and analysis results.
"""

from typing import List, Dict, Optional
from datetime import datetime
import os
from pathlib import Path

from .entry import FMEAEntry, FMEAReport, SystemType, Subsystem
from .risk import RiskCalculator, RiskThresholds
from .taxonomy import TaxonomyLoader


class FMEAReportGenerator:
    """Generates various types of reports from FMEA data."""
    
    def __init__(self, risk_calculator: Optional[RiskCalculator] = None,
                 taxonomy_loader: Optional[TaxonomyLoader] = None):
        """
        Initialize the report generator.
        
        Args:
            risk_calculator: Risk calculator instance. If None, creates default.
            taxonomy_loader: Taxonomy loader instance. If None, creates default.
        """
        self.risk_calculator = risk_calculator or RiskCalculator()
        self.taxonomy_loader = taxonomy_loader or TaxonomyLoader()
    
    def generate_markdown_report(self, report: FMEAReport) -> str:
        """Generate a comprehensive Markdown report."""
        markdown = self._generate_markdown_header(report)
        markdown += self._generate_markdown_summary(report)
        markdown += self._generate_markdown_risk_analysis(report)
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
        stats = risk_analysis["statistics"]
        risk_dist = risk_analysis["risk_distribution"]
        
        return f"""## Executive Summary

- **Total Failure Modes Analyzed:** {stats['total_entries']}
- **Mean RPN:** {stats['mean_rpn']:.1f}
- **Median RPN:** {stats['median_rpn']:.1f}
- **Maximum RPN:** {stats['max_rpn']}

### Risk Distribution

| Risk Level | Count | Percentage |
|------------|-------|------------|
| Critical   | {risk_dist['Critical']} | {risk_dist['Critical']/stats['total_entries']*100:.1f}% |
| High       | {risk_dist['High']} | {risk_dist['High']/stats['total_entries']*100:.1f}% |
| Medium     | {risk_dist['Medium']} | {risk_dist['Medium']/stats['total_entries']*100:.1f}% |
| Low        | {risk_dist['Low']} | {risk_dist['Low']/stats['total_entries']*100:.1f}% |

"""
    
    def _generate_markdown_risk_analysis(self, report: FMEAReport) -> str:
        """Generate Markdown risk analysis section."""
        risk_analysis = self.risk_calculator.analyze_report_risk(report)
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
                markdown += f"| {i} | {entry.id} | {entry.taxonomy_id} | {entry.rpn} | {risk_level.value} |\n"
        
        markdown += "\n### Risk by Subsystem\n\n"
        markdown += "| Subsystem | Count | Avg RPN | Max RPN |\n"
        markdown += "|-----------|-------|---------|--------|\n"
        
        for subsystem, data in sorted(subsystem_risk.items(), 
                                     key=lambda x: x[1]["avg_rpn"], reverse=True):
            markdown += f"| {subsystem} | {data['count']} | {data['avg_rpn']:.1f} | {data['max_rpn']} |\n"
        
        return markdown + "\n"
    
    def _generate_markdown_entries_table(self, report: FMEAReport) -> str:
        """Generate Markdown table of all entries."""
        markdown = """## All FMEA Entries

| ID | Taxonomy | Subsystem | Severity | Occurrence | Detection | RPN | Risk Level |
|----|----------|-----------|----------|------------|-----------|-----|------------|
"""
        
        # Sort entries by RPN (highest first)
        sorted_entries = sorted(report.entries, key=lambda x: x.rpn, reverse=True)
        
        for entry in sorted_entries:
            risk_level = self.risk_calculator.thresholds.categorize_rpn(entry.rpn)
            markdown += f"| {entry.id} | {entry.taxonomy_id} | {entry.subsystem.value} | "
            markdown += f"{entry.severity} | {entry.occurrence} | {entry.detection} | "
            markdown += f"{entry.rpn} | {risk_level.value} |\n"
        
        return markdown + "\n"
    
    def _generate_markdown_detailed_entries(self, report: FMEAReport) -> str:
        """Generate detailed Markdown entries for high-risk items."""
        markdown = "## Detailed Analysis of High-Risk Entries\n\n"
        
        high_risk_entries = [entry for entry in report.entries 
                           if entry.risk_level in ["Critical", "High"]]
        
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
        recommendations = self.risk_calculator.recommend_actions(entry)
        
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
        
        markdown += "\n**Recommended Actions:**\n"
        for recommendation in recommendations:
            markdown += f"- {recommendation}\n"
        
        if entry.scenario:
            markdown += f"\n**Scenario:** {entry.scenario}\n"
        
        markdown += "\n---\n\n"
        
        return markdown
    
    def _generate_markdown_recommendations(self, report: FMEAReport) -> str:
        """Generate Markdown recommendations section."""
        high_risk_count = len([e for e in report.entries if e.risk_level in ["Critical", "High"]])
        
        markdown = """## Recommendations

### Immediate Actions Required

"""
        
        if high_risk_count > 0:
            markdown += f"There are {high_risk_count} high-risk or critical entries that require immediate attention:\n\n"
            
            critical_entries = [e for e in report.entries if e.risk_level == "Critical"]
            high_entries = [e for e in report.entries if e.risk_level == "High"]
            
            if critical_entries:
                markdown += "**Critical Risk Entries:**\n"
                for entry in critical_entries:
                    markdown += f"- {entry.id}: {entry.taxonomy_id} (RPN: {entry.rpn})\n"
                markdown += "\n"
            
            if high_entries:
                markdown += "**High Risk Entries:**\n"
                for entry in high_entries:
                    markdown += f"- {entry.id}: {entry.taxonomy_id} (RPN: {entry.rpn})\n"
                markdown += "\n"
        else:
            markdown += "No critical or high-risk entries identified.\n\n"
        
        markdown += """### General Recommendations

1. **Implement Continuous Monitoring:** Establish monitoring systems for all failure modes with RPN > 100
2. **Regular Review Cycles:** Schedule quarterly reviews of this FMEA analysis
3. **Incident Response:** Develop incident response procedures for high-risk scenarios
4. **Training:** Ensure team members are trained on identified failure modes and mitigations
5. **Documentation:** Keep this FMEA analysis updated as the system evolves

### Next Steps

1. Prioritize mitigation efforts based on RPN rankings
2. Implement recommended actions for critical and high-risk entries
3. Establish monitoring and detection mechanisms
4. Schedule follow-up assessment in 3 months
5. Update this analysis when system architecture changes

"""
        
        return markdown
    
    def save_markdown_report(self, report: FMEAReport, output_path: str) -> None:
        """Save Markdown report to file."""
        markdown_content = self.generate_markdown_report(report)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
    
    def generate_csv_export(self, report: FMEAReport) -> str:
        """Generate CSV export of FMEA entries."""
        csv_content = "ID,Taxonomy_ID,System_Type,Subsystem,Cause,Effect,Severity,Occurrence,Detection,RPN,Risk_Level,Detection_Method,Created_Date,Created_By\n"
        
        for entry in report.entries:
            risk_level = self.risk_calculator.thresholds.categorize_rpn(entry.rpn)
            csv_content += f'"{entry.id}","{entry.taxonomy_id}","{entry.system_type.value}","{entry.subsystem.value}",'
            csv_content += f'"{entry.cause}","{entry.effect}",{entry.severity},{entry.occurrence},{entry.detection},'
            csv_content += f'{entry.rpn},"{risk_level.value}","{entry.detection_method.value}",'
            csv_content += f'"{entry.created_date.isoformat()}","{entry.created_by}"\n'
        
        return csv_content
    
    def save_csv_export(self, report: FMEAReport, output_path: str) -> None:
        """Save CSV export to file."""
        csv_content = self.generate_csv_export(report)
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(csv_content)
    
    def generate_html_report(self, report: FMEAReport) -> str:
        """Generate HTML report (basic implementation)."""
        # Convert markdown to HTML (basic implementation)
        markdown_content = self.generate_markdown_report(report)
        
        # Simple markdown to HTML conversion
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>FMEA Report: {report.title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        .critical {{ background-color: #ffebee; }}
        .high {{ background-color: #fff3e0; }}
        .medium {{ background-color: #f3e5f5; }}
        .low {{ background-color: #e8f5e8; }}
    </style>
</head>
<body>
    <pre>{markdown_content}</pre>
</body>
</html>"""
        
        return html_content