"""
Agentic FMEA - Failure Mode and Effects Analysis for Agentic AI Systems

A Python library for conducting FMEA (Failure Mode and Effects Analysis) on agentic AI systems,
based on the Microsoft AI Red Team taxonomy of failure modes.

Example usage:
    >>> from agentic_fmea import FMEAEntry, FMEAReport, SystemType, Subsystem
    >>> from agentic_fmea import RiskCalculator, FMEAReportGenerator
    >>> from datetime import datetime
    >>> 
    >>> # Create an FMEA entry
    >>> entry = FMEAEntry(
    ...     id="memory_poisoning_001",
    ...     taxonomy_id="memory_poisoning",
    ...     system_type=SystemType.MULTI_AGENT_COLLABORATIVE,
    ...     subsystem=Subsystem.MEMORY,
    ...     cause="Malicious email with embedded instructions",
    ...     effect="Agent forwards sensitive information to unauthorized recipients",
    ...     severity=8,
    ...     occurrence=6,
    ...     detection=7,
    ...     detection_method=DetectionMethod.LIVE_TELEMETRY,
    ...     mitigation=["Input validation", "Memory access controls"],
    ...     agent_capabilities=["autonomy", "memory", "environment_interaction"],
    ...     potential_effects=["Agent misalignment", "Agent action abuse", "Data exfiltration"],
    ...     created_date=datetime.now(),
    ...     last_updated=datetime.now(),
    ...     created_by="Security Team"
    ... )
    >>> 
    >>> # Create a report
    >>> report = FMEAReport(
    ...     title="Email Assistant FMEA",
    ...     system_description="Agentic AI email assistant with memory capabilities",
    ...     entries=[entry],
    ...     created_date=datetime.now(),
    ...     created_by="Security Team"
    ... )
    >>> 
    >>> # Generate markdown report
    >>> generator = FMEAReportGenerator()
    >>> markdown = generator.generate_markdown_report(report)
    >>> print(markdown)
"""

from .entry import (
    FMEAEntry, 
    FMEAReport, 
    DetectionMethod, 
    SystemType, 
    Subsystem
)

from .taxonomy import (
    TaxonomyLoader,
    FailureMode,
    get_taxonomy_loader,
    get_failure_mode,
    search_failure_modes
)

from .risk import (
    RiskCalculator,
    RiskLevel,
    RiskThresholds
)

from .report import (
    FMEAReportGenerator
)

__version__ = "0.1.0"
__author__ = "Claude & Karthi"
__email__ = "claude@etherium.ai"
__description__ = "Failure Mode and Effects Analysis for Agentic AI Systems"

__all__ = [
    # Core data structures
    "FMEAEntry",
    "FMEAReport",
    "DetectionMethod",
    "SystemType", 
    "Subsystem",
    
    # Taxonomy management
    "TaxonomyLoader",
    "FailureMode",
    "get_taxonomy_loader",
    "get_failure_mode",
    "search_failure_modes",
    
    # Risk analysis
    "RiskCalculator",
    "RiskLevel",
    "RiskThresholds",
    
    # Report generation
    "FMEAReportGenerator",
]