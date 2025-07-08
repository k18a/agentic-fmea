"""
FMEA Entry data model for agentic AI systems.

This module defines the core data structure for Failure Mode and Effects Analysis (FMEA)
entries, incorporating the Microsoft AI Red Team taxonomy for agentic AI systems.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime


class DetectionMethod(str, Enum):
    """Methods for detecting failure modes in agentic AI systems."""
    STATIC_ANALYSIS = "static_analysis"
    RED_TEAMING = "red_teaming"
    LIVE_TELEMETRY = "live_telemetry"
    HUMAN_OVERSIGHT = "human_oversight"
    AUTOMATED_MONITORING = "automated_monitoring"
    TESTING = "testing"
    CODE_REVIEW = "code_review"
    AUDIT_TRAIL = "audit_trail"


class SystemType(str, Enum):
    """Types of agentic AI systems."""
    SINGLE_AGENT = "single_agent"
    MULTI_AGENT_HIERARCHICAL = "multi_agent_hierarchical"
    MULTI_AGENT_COLLABORATIVE = "multi_agent_collaborative"
    MULTI_AGENT_DISTRIBUTED = "multi_agent_distributed"
    USER_DRIVEN = "user_driven"
    EVENT_DRIVEN = "event_driven"
    DECLARATIVE = "declarative"
    EVALUATIVE = "evaluative"


class Subsystem(str, Enum):
    """Subsystems within agentic AI systems."""
    PLANNING = "planning"
    MEMORY = "memory"
    TOOLING = "tooling"
    COMMUNICATION = "communication"
    ENVIRONMENT_OBSERVATION = "environment_observation"
    ENVIRONMENT_INTERACTION = "environment_interaction"
    KNOWLEDGE_BASE = "knowledge_base"
    COORDINATION = "coordination"
    IDENTITY = "identity"
    CONTROL_FLOW = "control_flow"


@dataclass
class FMEAEntry:
    """
    A single FMEA entry for agentic AI systems.

    Incorporates traditional FMEA methodology with agentic AI-specific taxonomy.
    """

    # Basic identification
    id: str
    taxonomy_id: str  # Links to taxonomy.json

    # System context
    system_type: SystemType
    subsystem: Subsystem

    # FMEA core elements
    cause: str
    effect: str

    # Risk assessment (1-10 scale)
    severity: int  # 1 = negligible, 10 = catastrophic
    occurrence: int  # 1 = remote, 10 = very high
    detection: int  # 1 = very high (easily detected), 10 = very low (hard to detect)

    # Detection and mitigation
    detection_method: DetectionMethod
    mitigation: List[str]

    # Additional agentic AI context
    agent_capabilities: List[str]  # e.g., ["autonomy", "memory", "collaboration"]
    potential_effects: List[str]  # From taxonomy

    # Metadata
    created_date: datetime
    last_updated: datetime
    created_by: str

    # Optional fields
    scenario: Optional[str] = None
    existing_controls: Optional[List[str]] = None
    recommended_actions: Optional[List[str]] = None
    priority: Optional[str] = None

    @property
    def rpn(self) -> int:
        """Risk Priority Number = Severity × Occurrence × Detection."""
        return self.severity * self.occurrence * self.detection

    @property
    def risk_level(self) -> str:
        """Categorize risk based on RPN."""
        if self.rpn >= 500:
            return "Critical"
        elif self.rpn >= 200:
            return "High"
        elif self.rpn >= 100:
            return "Medium"
        else:
            return "Low"

    def __post_init__(self):
        """Validate the entry after initialization."""
        # Validate severity, occurrence, detection are in range 1-10
        for field_name, value in [("severity", self.severity),
                                  ("occurrence", self.occurrence),
                                  ("detection", self.detection)]:
            if not 1 <= value <= 10:
                raise ValueError(f"{field_name} must be between 1 and 10, got {value}")

        # Validate that mitigation list is not empty
        if not self.mitigation:
            raise ValueError("At least one mitigation strategy must be provided")


@dataclass
class FMEAReport:
    """
    A collection of FMEA entries forming a complete analysis.
    """

    title: str
    system_description: str
    entries: List[FMEAEntry]
    created_date: datetime
    created_by: str

    # Optional metadata
    version: str = "1.0"
    scope: Optional[str] = None
    assumptions: Optional[List[str]] = None
    limitations: Optional[List[str]] = None

    @property
    def high_risk_entries(self) -> List[FMEAEntry]:
        """Get entries with high or critical risk levels."""
        return [
            entry for entry in self.entries if entry.risk_level in ["High", "Critical"]
        ]

    @property
    def entries_by_risk(self) -> List[FMEAEntry]:
        """Get entries sorted by RPN (highest risk first)."""
        return sorted(self.entries, key=lambda x: x.rpn, reverse=True)

    @property
    def risk_summary(self) -> dict:
        """Summary of risk levels in the report."""
        summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for entry in self.entries:
            summary[entry.risk_level] += 1
        return summary

    def get_entries_by_subsystem(self, subsystem: Subsystem) -> List[FMEAEntry]:
        """Get all entries for a specific subsystem."""
        return [
            entry for entry in self.entries if entry.subsystem == subsystem
        ]

    def get_entries_by_taxonomy(self, taxonomy_id: str) -> List[FMEAEntry]:
        """Get all entries related to a specific taxonomy failure mode."""
        return [
            entry for entry in self.entries if entry.taxonomy_id == taxonomy_id
        ]
