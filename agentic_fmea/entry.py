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
    OTHER = "other"


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
    OTHER = "other"


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
    OTHER = "other"


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
    
    # Custom fields for flexible enum support
    custom_system_type: Optional[str] = None
    custom_subsystem: Optional[str] = None
    custom_detection_method: Optional[str] = None

    @property
    def rpn(self) -> int:
        """Risk Priority Number = Severity × Occurrence × Detection."""
        return self.severity * self.occurrence * self.detection


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
        
        # Validate custom fields when OTHER enum values are used
        if self.system_type == SystemType.OTHER:
            if self.custom_system_type is None:
                raise ValueError("custom_system_type must be provided when system_type is OTHER")
            if not self.custom_system_type.strip():
                raise ValueError("custom_system_type cannot be empty or whitespace")
                
        if self.subsystem == Subsystem.OTHER:
            if self.custom_subsystem is None:
                raise ValueError("custom_subsystem must be provided when subsystem is OTHER")
            if not self.custom_subsystem.strip():
                raise ValueError("custom_subsystem cannot be empty or whitespace")
                
        if self.detection_method == DetectionMethod.OTHER:
            if self.custom_detection_method is None:
                raise ValueError("custom_detection_method must be provided when detection_method is OTHER")
            if not self.custom_detection_method.strip():
                raise ValueError("custom_detection_method cannot be empty or whitespace")
        
        # Validate that custom fields are not provided when NOT using OTHER
        if self.system_type != SystemType.OTHER and self.custom_system_type is not None:
            raise ValueError("custom_system_type should only be provided when system_type is OTHER")
            
        if self.subsystem != Subsystem.OTHER and self.custom_subsystem is not None:
            raise ValueError("custom_subsystem should only be provided when subsystem is OTHER")
            
        if self.detection_method != DetectionMethod.OTHER and self.custom_detection_method is not None:
            raise ValueError("custom_detection_method should only be provided when detection_method is OTHER")


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

    def high_risk_entries(self, risk_calculator=None) -> List[FMEAEntry]:
        """Get entries with high or critical risk levels."""
        from .risk import RiskCalculator, RiskLevel
        if risk_calculator is None:
            risk_calculator = RiskCalculator()
        
        return [
            entry for entry in self.entries 
            if risk_calculator.thresholds.categorize_rpn(entry.rpn) in [RiskLevel.HIGH, RiskLevel.CRITICAL]
        ]

    @property
    def entries_by_risk(self) -> List[FMEAEntry]:
        """Get entries sorted by RPN (highest risk first)."""
        return sorted(self.entries, key=lambda x: x.rpn, reverse=True)

    def risk_summary(self, risk_calculator=None) -> dict:
        """Summary of risk levels in the report."""
        from .risk import RiskCalculator, RiskLevel
        if risk_calculator is None:
            risk_calculator = RiskCalculator()
        
        summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
        for entry in self.entries:
            risk_level = risk_calculator.thresholds.categorize_rpn(entry.rpn)
            summary[risk_level.value] += 1
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
