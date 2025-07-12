"""
Risk assessment utilities for agentic AI FMEA.

This module provides functions for calculating Risk Priority Numbers (RPN),
generating risk matrices, and analyzing risk distributions.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import List, Dict, Optional, Any, Tuple, Union
from dataclasses import dataclass
from enum import Enum
import warnings
from pathlib import Path
import io
import base64

from .entry import FMEAEntry, FMEAReport
from .taxonomy import TaxonomyLoader


class RiskLevel(str, Enum):
    """Risk level categories based on RPN."""
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


@dataclass
class RiskThresholds:
    """Configurable risk thresholds for RPN categorization."""
    critical: int = 500
    high: int = 200
    medium: int = 100

    def categorize_rpn(self, rpn: int) -> RiskLevel:
        """Categorize an RPN value into risk level."""
        if rpn >= self.critical:
            return RiskLevel.CRITICAL
        elif rpn >= self.high:
            return RiskLevel.HIGH
        elif rpn >= self.medium:
            return RiskLevel.MEDIUM
        else:
            return RiskLevel.LOW


@dataclass
class ChartTheme:
    """Professional chart styling theme."""
    
    # Risk level colors matching HTML report styling
    risk_colors: Dict[str, str] = None
    
    # Professional color palette
    primary_color: str = "#2c3e50"
    secondary_color: str = "#34495e"
    accent_color: str = "#3498db"
    success_color: str = "#27ae60"
    warning_color: str = "#f39c12"
    danger_color: str = "#e74c3c"
    
    # Chart styling
    figure_facecolor: str = "white"
    axes_facecolor: str = "white"
    grid_color: str = "#ecf0f1"
    text_color: str = "#2c3e50"
    
    # Font settings
    font_family: str = "DejaVu Sans"
    title_size: int = 14
    label_size: int = 12
    tick_size: int = 10
    legend_size: int = 11
    
    # Chart dimensions
    dpi: int = 150
    figsize_single: Tuple[int, int] = (10, 6)
    figsize_double: Tuple[int, int] = (15, 6)
    figsize_large: Tuple[int, int] = (12, 8)
    
    def __post_init__(self):
        """Initialize risk colors if not provided."""
        if self.risk_colors is None:
            self.risk_colors = {
                "Critical": "#e74c3c",  # Red
                "High": "#f39c12",      # Orange
                "Medium": "#f1c40f",    # Yellow
                "Low": "#27ae60"        # Green
            }
    
    def apply_theme(self) -> None:
        """Apply theme settings to matplotlib."""
        plt.rcParams.update({
            'font.family': self.font_family,
            'font.size': self.label_size,
            'axes.titlesize': self.title_size,
            'axes.labelsize': self.label_size,
            'xtick.labelsize': self.tick_size,
            'ytick.labelsize': self.tick_size,
            'legend.fontsize': self.legend_size,
            'figure.facecolor': self.figure_facecolor,
            'axes.facecolor': self.axes_facecolor,
            'axes.edgecolor': self.text_color,
            'axes.labelcolor': self.text_color,
            'text.color': self.text_color,
            'xtick.color': self.text_color,
            'ytick.color': self.text_color,
            'grid.color': self.grid_color,
            'grid.alpha': 0.7,
            'axes.grid': True,
            'axes.axisbelow': True,
            'figure.dpi': self.dpi,
        })


class ChartThemes:
    """Predefined chart themes."""
    
    @staticmethod
    def professional() -> ChartTheme:
        """Professional corporate theme."""
        return ChartTheme()
    
    @staticmethod
    def academic() -> ChartTheme:
        """Academic presentation theme."""
        return ChartTheme(
            primary_color="#1f4e79",
            secondary_color="#2e5984",
            font_family="Times New Roman",
            title_size=16,
            label_size=14,
            tick_size=12
        )
    
    @staticmethod
    def colorblind_friendly() -> ChartTheme:
        """Colorblind-friendly theme."""
        return ChartTheme(
            risk_colors={
                "Critical": "#d73027",  # Red
                "High": "#fc8d59",      # Orange
                "Medium": "#fee08b",    # Light yellow
                "Low": "#4575b4"        # Blue
            }
        )


class RiskCalculator:
    """Calculates and analyzes risk metrics for FMEA entries."""

    def __init__(self, thresholds: Optional[RiskThresholds] = None, 
                 taxonomy_loader: Optional[TaxonomyLoader] = None,
                 chart_theme: Optional[ChartTheme] = None):
        """
        Initialize the risk calculator.

        Args:
            thresholds: Custom risk thresholds. If None, uses default.
            taxonomy_loader: Taxonomy loader instance. If None, creates default.
            chart_theme: Chart theme for visualizations. If None, uses professional theme.
        """
        self.thresholds = thresholds or RiskThresholds()
        self.taxonomy_loader = taxonomy_loader or TaxonomyLoader()
        self.theme = chart_theme or ChartThemes.professional()

    def calculate_rpn(self, severity: int, occurrence: int, detection: int) -> int:
        """Calculate Risk Priority Number."""
        return severity * occurrence * detection

    def calculate_risk_score(self, entry: FMEAEntry) -> Dict[str, Any]:
        """Calculate comprehensive risk score for an entry."""
        rpn = entry.rpn
        risk_level = self.thresholds.categorize_rpn(rpn)

        return {
            "rpn": rpn,
            "risk_level": risk_level,
            "severity": entry.severity,
            "occurrence": entry.occurrence,
            "detection": entry.detection,
            "severity_label": self._get_severity_label(entry.severity),
            "occurrence_label": self._get_occurrence_label(entry.occurrence),
            "detection_label": self._get_detection_label(entry.detection)
        }

    def _get_severity_label(self, severity: int) -> str:
        """Get descriptive label for severity score."""
        labels = {
            1: "Negligible", 2: "Minor", 3: "Moderate", 4: "Significant",
            5: "Major", 6: "Severe", 7: "Critical", 8: "Very Critical",
            9: "Catastrophic", 10: "Extreme"
        }
        return labels.get(severity, "Unknown")

    def _get_occurrence_label(self, occurrence: int) -> str:
        """Get descriptive label for occurrence score."""
        labels = {
            1: "Remote", 2: "Very Low", 3: "Low", 4: "Moderately Low",
            5: "Moderate", 6: "Moderately High", 7: "High", 8: "Very High",
            9: "Extremely High", 10: "Certain"
        }
        return labels.get(occurrence, "Unknown")

    def _get_detection_label(self, detection: int) -> str:
        """Get descriptive label for detection score."""
        labels = {
            1: "Very High (Easily Detected)", 2: "High", 3: "Moderately High",
            4: "Moderate", 5: "Low", 6: "Moderately Low", 7: "Low",
            8: "Very Low", 9: "Extremely Low", 10: "Cannot Detect"
        }
        return labels.get(detection, "Unknown")

    def analyze_report_risk(self, report: FMEAReport) -> Dict[str, Any]:
        """Analyze risk distribution across an entire FMEA report."""
        if not report.entries:
            return {"error": "No entries to analyze"}

        rpns = [entry.rpn for entry in report.entries]
        risk_levels = [self.thresholds.categorize_rpn(rpn) for rpn in rpns]

        # Basic statistics
        stats = {
            "total_entries": len(report.entries),
            "mean_rpn": np.mean(rpns),
            "median_rpn": np.median(rpns),
            "max_rpn": max(rpns),
            "min_rpn": min(rpns),
            "std_rpn": np.std(rpns)
        }

        # Risk level distribution
        risk_distribution = {level.value: 0 for level in RiskLevel}
        for level in risk_levels:
            risk_distribution[level.value] += 1

        # Top risk entries
        top_risks = sorted(
            report.entries, key=lambda x: x.rpn, reverse=True
        )[:10]

        # Risk by subsystem
        subsystem_risk = {}
        for entry in report.entries:
            subsystem = entry.subsystem.value
            if subsystem not in subsystem_risk:
                subsystem_risk[subsystem] = {
                    "count": 0, "total_rpn": 0, "max_rpn": 0
                }

            subsystem_risk[subsystem]["count"] += 1
            subsystem_risk[subsystem]["total_rpn"] += entry.rpn
            subsystem_risk[subsystem]["max_rpn"] = max(
                subsystem_risk[subsystem]["max_rpn"], entry.rpn
            )

        # Calculate average RPN per subsystem
        for subsystem in subsystem_risk:
            subsystem_risk[subsystem]["avg_rpn"] = (
                subsystem_risk[subsystem]["total_rpn"]
                / subsystem_risk[subsystem]["count"]
            )

        return {
            "statistics": stats,
            "risk_distribution": risk_distribution,
            "top_risks": [
                {"id": entry.id, "rpn": entry.rpn, "taxonomy_id": entry.taxonomy_id}
                for entry in top_risks
            ],
            "subsystem_risk": subsystem_risk
        }

    def generate_risk_matrix(
        self, entries: List[FMEAEntry],
        x_axis: str = "occurrence",
        y_axis: str = "severity"
    ) -> np.ndarray:
        """
        Generate a risk matrix visualization data.

        Args:
            entries: List of FMEA entries
            x_axis: Which dimension to use for x-axis (occurrence, severity, detection)
            y_axis: Which dimension to use for y-axis (occurrence, severity, detection)

        Returns:
            2D numpy array representing the risk matrix
        """
        if not entries:
            return np.zeros((10, 10))

        matrix = np.zeros((10, 10))

        for entry in entries:
            x_val = getattr(entry, x_axis) - 1  # Convert to 0-based index
            y_val = getattr(entry, y_axis) - 1  # Convert to 0-based index

            # Add RPN value to the matrix cell
            matrix[y_val, x_val] += entry.rpn

        return matrix

    def plot_risk_matrix(
        self, entries: List[FMEAEntry],
        x_axis: str = "occurrence",
        y_axis: str = "severity",
        title: str = "Risk Matrix",
        save_path: Optional[str] = None
    ) -> plt.Figure:
        """
        Plot a professional risk matrix visualization.

        Args:
            entries: List of FMEA entries
            x_axis: Which dimension to use for x-axis
            y_axis: Which dimension to use for y-axis
            title: Title for the plot
            save_path: Optional path to save the chart

        Returns:
            Matplotlib figure object
        """
        # Apply theme
        self.theme.apply_theme()
        
        matrix = self.generate_risk_matrix(entries, x_axis, y_axis)

        fig, ax = plt.subplots(figsize=self.theme.figsize_large, 
                              facecolor=self.theme.figure_facecolor)

        # Create custom colormap for risk levels
        from matplotlib.colors import LinearSegmentedColormap
        risk_colors = ['#ffffff', '#e8f5e8', '#fff3cd', '#fde2e4', '#dc3545']
        n_bins = 100
        cmap = LinearSegmentedColormap.from_list('risk', risk_colors, N=n_bins)

        # Create heatmap
        im = ax.imshow(matrix, cmap=cmap, aspect='auto', interpolation='nearest')

        # Set professional styling
        ax.set_xlabel(f'{x_axis.capitalize()} Rating', fontweight='bold')
        ax.set_ylabel(f'{y_axis.capitalize()} Rating', fontweight='bold')
        ax.set_title(title, fontweight='bold', pad=20)

        # Set tick labels with better formatting
        ax.set_xticks(range(10))
        ax.set_yticks(range(10))
        ax.set_xticklabels(range(1, 11))
        ax.set_yticklabels(range(1, 11))

        # Add risk level background regions
        self._add_risk_regions(ax, x_axis, y_axis)

        # Add colorbar with custom formatting
        cbar = plt.colorbar(im, ax=ax, shrink=0.8, aspect=20)
        cbar.set_label('Total RPN', fontweight='bold')

        # Add text annotations with better styling
        max_val = np.max(matrix) if np.max(matrix) > 0 else 1
        for i in range(10):
            for j in range(10):
                if matrix[i, j] > 0:
                    # Choose text color based on background intensity
                    text_color = 'white' if matrix[i, j] > max_val * 0.6 else 'black'
                    ax.text(j, i, f'{int(matrix[i, j])}',
                            ha="center", va="center", color=text_color,
                            fontweight='bold', fontsize=10)

        # Add grid for better readability
        ax.set_xticks(np.arange(-0.5, 10, 1), minor=True)
        ax.set_yticks(np.arange(-0.5, 10, 1), minor=True)
        ax.grid(which="minor", color="white", linestyle='-', linewidth=1)

        plt.tight_layout()
        
        if save_path:
            self._save_chart(fig, save_path)
        
        return fig

    def plot_risk_distribution(self, report: FMEAReport, save_path: Optional[str] = None) -> plt.Figure:
        """Plot professional risk level distribution for a report."""
        # Apply theme
        self.theme.apply_theme()
        
        analysis = self.analyze_report_risk(report)
        risk_dist = analysis.get("risk_distribution", {"Critical": 0, "High": 0, "Medium": 0, "Low": 0})

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.theme.figsize_double,
                                      facecolor=self.theme.figure_facecolor)

        # Bar chart of risk levels with professional styling
        levels = ["Critical", "High", "Medium", "Low"]
        counts = [risk_dist[level] for level in levels]
        colors = [self.theme.risk_colors[level] for level in levels]

        bars = ax1.bar(levels, counts, color=colors, edgecolor='white', linewidth=2)
        ax1.set_title('Risk Level Distribution', fontweight='bold', pad=15)
        ax1.set_ylabel('Number of Entries', fontweight='bold')
        ax1.set_xlabel('Risk Level', fontweight='bold')

        # Add count labels on bars with better formatting
        for i, (bar, count) in enumerate(zip(bars, counts)):
            if count > 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                        str(count), ha='center', va='bottom', fontweight='bold')
                
                # Add percentage labels
                total_entries = sum(counts)
                if total_entries > 0:
                    percentage = (count / total_entries) * 100
                    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height()/2,
                            f'{percentage:.1f}%', ha='center', va='center', 
                            color='white', fontweight='bold', fontsize=9)

        # Style the risk level chart
        ax1.set_ylim(0, max(counts) * 1.2 if max(counts) > 0 else 1)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # RPN histogram with professional styling
        if report.entries:
            rpns = [entry.rpn for entry in report.entries]
            n_bins = min(20, len(rpns))
            ax2.hist(rpns, bins=n_bins, color=self.theme.accent_color, 
                    alpha=0.7, edgecolor='white', linewidth=1.5)
        
            # Add threshold lines with professional styling
            threshold_colors = {
                'critical': self.theme.risk_colors['Critical'],
                'high': self.theme.risk_colors['High'], 
                'medium': self.theme.risk_colors['Medium']
            }
            
            ax2.axvline(x=self.thresholds.critical, color=threshold_colors['critical'], 
                       linestyle='--', linewidth=2, label=f'Critical ({self.thresholds.critical})')
            ax2.axvline(x=self.thresholds.high, color=threshold_colors['high'], 
                       linestyle='--', linewidth=2, label=f'High ({self.thresholds.high})')
            ax2.axvline(x=self.thresholds.medium, color=threshold_colors['medium'], 
                       linestyle='--', linewidth=2, label=f'Medium ({self.thresholds.medium})')
            
            ax2.legend(frameon=True, fancybox=True, shadow=True)
            
            # Add statistics text box
            stats_text = f'Mean: {np.mean(rpns):.1f}\nMedian: {np.median(rpns):.1f}\nMax: {max(rpns)}'
            ax2.text(0.02, 0.98, stats_text, transform=ax2.transAxes, 
                    verticalalignment='top', bbox=dict(boxstyle='round', 
                    facecolor='white', alpha=0.8))

        ax2.set_title('RPN Distribution', fontweight='bold', pad=15)
        ax2.set_xlabel('Risk Priority Number (RPN)', fontweight='bold')
        ax2.set_ylabel('Frequency', fontweight='bold')
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)

        plt.tight_layout()
        
        if save_path:
            self._save_chart(fig, save_path)
        
        return fig

    def plot_subsystem_comparison(self, report: FMEAReport, save_path: Optional[str] = None) -> plt.Figure:
        """Plot risk comparison across subsystems."""
        self.theme.apply_theme()
        
        analysis = self.analyze_report_risk(report)
        subsystem_risk = analysis.get("subsystem_risk", {})
        
        if not subsystem_risk:
            # Create empty plot for reports with no entries
            fig, ax = plt.subplots(figsize=self.theme.figsize_single)
            ax.text(0.5, 0.5, 'No subsystem data available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Subsystem Risk Comparison', fontweight='bold')
            return fig
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.theme.figsize_single,
                                      facecolor=self.theme.figure_facecolor)
        
        subsystems = list(subsystem_risk.keys())
        avg_rpns = [subsystem_risk[sub]["avg_rpn"] for sub in subsystems]
        max_rpns = [subsystem_risk[sub]["max_rpn"] for sub in subsystems]
        counts = [subsystem_risk[sub]["count"] for sub in subsystems]
        
        # Average RPN by subsystem
        bars1 = ax1.bar(subsystems, avg_rpns, color=self.theme.accent_color, 
                       edgecolor='white', linewidth=2)
        ax1.set_title('Average RPN by Subsystem', fontweight='bold', pad=10)
        ax1.set_ylabel('Average RPN', fontweight='bold')
        
        # Add value labels on bars
        for bar, val in zip(bars1, avg_rpns):
            ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 1,
                    f'{val:.1f}', ha='center', va='bottom', fontweight='bold')
        
        # Add risk threshold lines
        ax1.axhline(y=self.thresholds.critical, color=self.theme.risk_colors['Critical'], 
                   linestyle='--', alpha=0.7, label='Critical')
        ax1.axhline(y=self.thresholds.high, color=self.theme.risk_colors['High'], 
                   linestyle='--', alpha=0.7, label='High')
        ax1.axhline(y=self.thresholds.medium, color=self.theme.risk_colors['Medium'], 
                   linestyle='--', alpha=0.7, label='Medium')
        ax1.legend()
        
        # Entry count by subsystem
        bars2 = ax2.bar(subsystems, counts, color=self.theme.secondary_color,
                       edgecolor='white', linewidth=2)
        ax2.set_title('Number of Entries by Subsystem', fontweight='bold', pad=10)
        ax2.set_ylabel('Entry Count', fontweight='bold')
        ax2.set_xlabel('Subsystem', fontweight='bold')
        
        # Add value labels
        for bar, val in zip(bars2, counts):
            ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                    str(val), ha='center', va='bottom', fontweight='bold')
        
        # Style both plots
        for ax in [ax1, ax2]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        if save_path:
            self._save_chart(fig, save_path)
        
        return fig

    def plot_taxonomy_breakdown(self, report: FMEAReport, save_path: Optional[str] = None) -> plt.Figure:
        """Plot breakdown of failure modes by taxonomy categories."""
        self.theme.apply_theme()
        
        if not report.entries:
            fig, ax = plt.subplots(figsize=self.theme.figsize_single)
            ax.text(0.5, 0.5, 'No taxonomy data available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Failure Mode Taxonomy Breakdown', fontweight='bold')
            return fig
        
        # Group entries by taxonomy
        taxonomy_counts = {}
        taxonomy_avg_rpn = {}
        
        for entry in report.entries:
            tax_id = entry.taxonomy_id
            if tax_id not in taxonomy_counts:
                taxonomy_counts[tax_id] = 0
                taxonomy_avg_rpn[tax_id] = []
            
            taxonomy_counts[tax_id] += 1
            taxonomy_avg_rpn[tax_id].append(entry.rpn)
        
        # Calculate averages
        for tax_id in taxonomy_avg_rpn:
            taxonomy_avg_rpn[tax_id] = np.mean(taxonomy_avg_rpn[tax_id])
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.theme.figsize_double,
                                      facecolor=self.theme.figure_facecolor)
        
        # Pie chart of taxonomy distribution
        labels = list(taxonomy_counts.keys())
        sizes = list(taxonomy_counts.values())
        colors = plt.cm.Set3(np.linspace(0, 1, len(labels)))
        
        wedges, texts, autotexts = ax1.pie(sizes, labels=labels, autopct='%1.1f%%',
                                          colors=colors, startangle=90)
        ax1.set_title('Failure Mode Distribution\nby Taxonomy', fontweight='bold')
        
        # Horizontal bar chart of average RPN by taxonomy
        taxonomy_ids = list(taxonomy_avg_rpn.keys())
        avg_rpns = list(taxonomy_avg_rpn.values())
        
        # Color bars by risk level
        bar_colors = []
        for rpn in avg_rpns:
            risk_level = self.thresholds.categorize_rpn(int(rpn))
            bar_colors.append(self.theme.risk_colors[risk_level.value])
        
        bars = ax2.barh(taxonomy_ids, avg_rpns, color=bar_colors, 
                       edgecolor='white', linewidth=1.5)
        ax2.set_title('Average RPN by Taxonomy', fontweight='bold')
        ax2.set_xlabel('Average RPN', fontweight='bold')
        
        # Add value labels
        for bar, val in zip(bars, avg_rpns):
            ax2.text(bar.get_width() + 2, bar.get_y() + bar.get_height()/2,
                    f'{val:.1f}', ha='left', va='center', fontweight='bold')
        
        # Add risk threshold lines
        ax2.axvline(x=self.thresholds.critical, color=self.theme.risk_colors['Critical'], 
                   linestyle='--', alpha=0.7, label='Critical')
        ax2.axvline(x=self.thresholds.high, color=self.theme.risk_colors['High'], 
                   linestyle='--', alpha=0.7, label='High')
        ax2.axvline(x=self.thresholds.medium, color=self.theme.risk_colors['Medium'], 
                   linestyle='--', alpha=0.7, label='Medium')
        ax2.legend()
        
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        
        plt.tight_layout()
        
        if save_path:
            self._save_chart(fig, save_path)
        
        return fig

    def plot_mitigation_analysis(self, report: FMEAReport, save_path: Optional[str] = None) -> plt.Figure:
        """Plot analysis of mitigation strategies effectiveness."""
        self.theme.apply_theme()
        
        if not report.entries:
            fig, ax = plt.subplots(figsize=self.theme.figsize_single)
            ax.text(0.5, 0.5, 'No mitigation data available', 
                   ha='center', va='center', transform=ax.transAxes)
            ax.set_title('Mitigation Strategy Analysis', fontweight='bold')
            return fig
        
        # Analyze mitigation effectiveness (entries with more mitigations should have lower risk)
        mitigation_counts = []
        rpns = []
        
        for entry in report.entries:
            mitigation_counts.append(len(entry.mitigation))
            rpns.append(entry.rpn)
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=self.theme.figsize_double,
                                      facecolor=self.theme.figure_facecolor)
        
        # Scatter plot: Mitigation count vs RPN
        colors = [self.theme.risk_colors[self.thresholds.categorize_rpn(rpn).value] 
                 for rpn in rpns]
        
        scatter = ax1.scatter(mitigation_counts, rpns, c=colors, s=60, alpha=0.7, 
                             edgecolors='white', linewidth=1.5)
        ax1.set_xlabel('Number of Mitigation Strategies', fontweight='bold')
        ax1.set_ylabel('Risk Priority Number (RPN)', fontweight='bold')
        ax1.set_title('Mitigation Count vs Risk Level', fontweight='bold')
        
        # Add trend line if there are enough points
        if len(mitigation_counts) > 2:
            z = np.polyfit(mitigation_counts, rpns, 1)
            p = np.poly1d(z)
            ax1.plot(sorted(set(mitigation_counts)), 
                    [p(x) for x in sorted(set(mitigation_counts))],
                    linestyle='--', color=self.theme.primary_color, linewidth=2,
                    label=f'Trend (slope: {z[0]:.1f})')
            ax1.legend()
        
        # Histogram of mitigation counts
        mitigation_range = range(max(mitigation_counts) + 1) if mitigation_counts else [0]
        counts_hist = [mitigation_counts.count(i) for i in mitigation_range]
        
        bars = ax2.bar(mitigation_range, counts_hist, color=self.theme.accent_color,
                      edgecolor='white', linewidth=2)
        ax2.set_xlabel('Number of Mitigation Strategies', fontweight='bold')
        ax2.set_ylabel('Number of Entries', fontweight='bold')
        ax2.set_title('Distribution of Mitigation Strategies', fontweight='bold')
        
        # Add value labels
        for bar, val in zip(bars, counts_hist):
            if val > 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                        str(val), ha='center', va='bottom', fontweight='bold')
        
        # Style both plots
        for ax in [ax1, ax2]:
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            self._save_chart(fig, save_path)
        
        return fig

    def generate_comprehensive_charts(self, report: FMEAReport, 
                                    output_dir: str = "charts",
                                    formats: List[str] = None) -> Dict[str, str]:
        """
        Generate all available charts for a report.
        
        Args:
            report: FMEA report to generate charts for
            output_dir: Directory to save charts in
            formats: List of formats to save ('png', 'svg', 'pdf')
        
        Returns:
            Dictionary mapping chart names to file paths
        """
        if formats is None:
            formats = ['png']
        
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        
        chart_paths = {}
        
        chart_methods = {
            'risk_distribution': self.plot_risk_distribution,
            'risk_matrix': self.plot_risk_matrix,
            'subsystem_comparison': self.plot_subsystem_comparison,
            'taxonomy_breakdown': self.plot_taxonomy_breakdown,
            'mitigation_analysis': self.plot_mitigation_analysis
        }
        
        for chart_name, chart_method in chart_methods.items():
            try:
                # Handle different method signatures
                if chart_name == 'risk_matrix':
                    fig = chart_method(report.entries, title="Risk Matrix: Severity vs Occurrence")
                else:
                    fig = chart_method(report)
                
                for fmt in formats:
                    filename = f"{chart_name}.{fmt}"
                    filepath = Path(output_dir) / filename
                    
                    fig.savefig(filepath, dpi=self.theme.dpi, bbox_inches='tight',
                               facecolor=self.theme.figure_facecolor)
                    
                    if fmt == formats[0]:  # Store path for primary format
                        chart_paths[chart_name] = str(filepath)
                
                plt.close(fig)
                
            except Exception as e:
                warnings.warn(f"Failed to generate {chart_name}: {e}")
                continue
        
        return chart_paths

    def _add_risk_regions(self, ax, x_axis: str, y_axis: str) -> None:
        """Add background risk level regions to risk matrix."""
        # Define risk regions based on traditional FMEA methodology
        # This is a simplified version - real implementation would be more complex
        
        # High risk region (top-right)
        high_risk = patches.Rectangle((7, 7), 3, 3, linewidth=0, 
                                    edgecolor='none', facecolor='red', alpha=0.1)
        ax.add_patch(high_risk)
        
        # Medium risk regions
        med_risk1 = patches.Rectangle((4, 7), 3, 3, linewidth=0, 
                                    edgecolor='none', facecolor='yellow', alpha=0.1)
        med_risk2 = patches.Rectangle((7, 4), 3, 3, linewidth=0, 
                                    edgecolor='none', facecolor='yellow', alpha=0.1)
        ax.add_patch(med_risk1)
        ax.add_patch(med_risk2)
        
        # Low risk region (bottom-left)
        low_risk = patches.Rectangle((0, 0), 4, 4, linewidth=0, 
                                   edgecolor='none', facecolor='green', alpha=0.1)
        ax.add_patch(low_risk)

    def _save_chart(self, fig: plt.Figure, save_path: str) -> None:
        """Save chart to specified path with high quality settings."""
        Path(save_path).parent.mkdir(parents=True, exist_ok=True)
        fig.savefig(save_path, dpi=self.theme.dpi, bbox_inches='tight',
                   facecolor=self.theme.figure_facecolor, edgecolor='none')

    def recommend_actions(self, entry: FMEAEntry) -> List[str]:
        """Recommend actions based on risk level and characteristics."""
        recommendations = []

        risk_score = self.calculate_risk_score(entry)
        risk_level = risk_score["risk_level"]

        if risk_level == RiskLevel.CRITICAL:
            recommendations.extend([
                "Immediate action required - halt system deployment until resolved",
                "Implement emergency monitoring and alerting",
                "Establish incident response procedures",
                "Consider system redesign to eliminate failure mode"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations.extend([
                "High priority - implement mitigation before deployment",
                "Establish monitoring and detection mechanisms",
                "Develop contingency plans",
                "Regular risk assessment reviews"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations.extend([
                "Medium priority - address in next development cycle",
                "Implement preventive measures",
                "Monitor for trends",
                "Document lessons learned"
            ])
        else:  # LOW
            recommendations.extend([
                "Low priority - address as resources permit",
                "Maintain awareness of potential issues",
                "Include in routine monitoring"
            ])

        # Add specific recommendations based on failure mode characteristics
        if entry.detection >= 7:  # Hard to detect
            recommendations.append("Implement automated detection mechanisms")
            recommendations.append("Establish regular audit procedures")

        if entry.severity >= 8:  # High severity
            recommendations.append("Implement fail-safe mechanisms")
            recommendations.append("Add redundancy to critical paths")

        if entry.occurrence >= 7:  # High occurrence
            recommendations.append("Address root causes in system design")
            recommendations.append("Implement preventive controls")

        # Add taxonomy-specific mitigations
        failure_mode = self.taxonomy_loader.get_failure_mode(entry.taxonomy_id)
        if failure_mode and failure_mode.recommended_mitigations:
            recommendations.extend(failure_mode.recommended_mitigations)

        return recommendations

    def get_detailed_recommendations(self, entry: FMEAEntry) -> Dict[str, Any]:
        """Get detailed recommendations with taxonomy-specific guidance."""
        recommendations = {
            "general_actions": [],
            "taxonomy_specific": {},
            "detection_strategies": [],
            "implementation_notes": [],
            "related_modes": []
        }

        risk_score = self.calculate_risk_score(entry)
        risk_level = risk_score["risk_level"]

        # General risk-level recommendations
        if risk_level == RiskLevel.CRITICAL:
            recommendations["general_actions"].extend([
                "Immediate action required - halt system deployment until resolved",
                "Implement emergency monitoring and alerting",
                "Establish incident response procedures",
                "Consider system redesign to eliminate failure mode"
            ])
        elif risk_level == RiskLevel.HIGH:
            recommendations["general_actions"].extend([
                "High priority - implement mitigation before deployment",
                "Establish monitoring and detection mechanisms",
                "Develop contingency plans",
                "Regular risk assessment reviews"
            ])
        elif risk_level == RiskLevel.MEDIUM:
            recommendations["general_actions"].extend([
                "Medium priority - address in next development cycle",
                "Implement preventive measures",
                "Monitor for trends",
                "Document lessons learned"
            ])
        else:  # LOW
            recommendations["general_actions"].extend([
                "Low priority - address as resources permit",
                "Maintain awareness of potential issues",
                "Include in routine monitoring"
            ])

        # Add specific recommendations based on failure mode characteristics
        if entry.detection >= 7:  # Hard to detect
            recommendations["general_actions"].append("Implement automated detection mechanisms")
            recommendations["general_actions"].append("Establish regular audit procedures")

        if entry.severity >= 8:  # High severity
            recommendations["general_actions"].append("Implement fail-safe mechanisms")
            recommendations["general_actions"].append("Add redundancy to critical paths")

        if entry.occurrence >= 7:  # High occurrence
            recommendations["general_actions"].append("Address root causes in system design")
            recommendations["general_actions"].append("Implement preventive controls")

        # Get taxonomy-specific guidance
        failure_mode = self.taxonomy_loader.get_failure_mode(entry.taxonomy_id)
        if failure_mode:
            recommendations["taxonomy_specific"] = {
                "recommended_mitigations": failure_mode.recommended_mitigations or [],
                "detection_strategies": failure_mode.detection_strategies or [],
                "implementation_notes": failure_mode.implementation_notes or [],
                "related_modes": failure_mode.related_modes or []
            }

        return recommendations
