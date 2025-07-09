"""
Taxonomy loader and validator for agentic AI failure modes.

This module provides functionality to load and validate the Microsoft AI Red Team
taxonomy of failure modes for agentic AI systems.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class FailureMode:
    """Represents a single failure mode from the taxonomy."""

    id: str
    category: str  # novel_security, novel_safety, existing_security, existing_safety
    pillar: str  # security or safety
    novel: bool
    description: str
    potential_impact: str
    potential_effects: List[str]
    systems_likely_to_occur: str
    example: str
    canonical_effects: List[str]
    refs: List[str]

    # Optional fields for existing failure modes
    why_increased_risk: Optional[str] = None
    
    # New guidance fields for AI safety knowledge base
    recommended_mitigations: Optional[List[str]] = None
    detection_strategies: Optional[List[str]] = None
    implementation_notes: Optional[List[str]] = None
    related_modes: Optional[List[str]] = None


class TaxonomyLoader:
    """Loads and manages the agentic AI failure mode taxonomy."""

    def __init__(self, taxonomy_path: Optional[str] = None):
        """
        Initialize the taxonomy loader.

        Args:
            taxonomy_path: Path to taxonomy.json file. If None, uses default location.
        """
        if taxonomy_path is None:
            # Default to taxonomy.json in same directory as this module
            current_dir = Path(__file__).parent
            taxonomy_path = current_dir / Path("taxonomy.json")

        self.taxonomy_path = Path(taxonomy_path)
        self._taxonomy_data: Optional[Dict[str, Any]] = None
        self._failure_modes: Optional[Dict[str, FailureMode]] = None

    def load_taxonomy(self) -> Dict[str, Any]:
        """Load the taxonomy from JSON file."""
        if not self.taxonomy_path.exists():
            raise FileNotFoundError(f"Taxonomy file not found: {self.taxonomy_path}")

        with open(self.taxonomy_path, 'r', encoding='utf-8') as f:
            self._taxonomy_data = json.load(f)

        if self._taxonomy_data is None:
            raise ValueError("Failed to load taxonomy data.")

        return self._taxonomy_data

    def _parse_failure_modes(self) -> Dict[str, FailureMode]:
        """Parse the loaded taxonomy data into FailureMode objects."""
        if self._taxonomy_data is None:
            self.load_taxonomy()

        failure_modes = {}

        for category, modes in self._taxonomy_data.items():
            for mode_id, mode_data in modes.items():
                failure_mode = FailureMode(
                    id=mode_id,
                    category=category,
                    pillar=mode_data["pillar"],
                    novel=mode_data["novel"],
                    description=mode_data["description"],
                    potential_impact=mode_data["potential_impact"],
                    potential_effects=mode_data["potential_effects"],
                    systems_likely_to_occur=mode_data["systems_likely_to_occur"],
                    example=mode_data["example"],
                    canonical_effects=mode_data["canonical_effects"],
                    refs=mode_data["refs"],
                    why_increased_risk=mode_data.get("why_increased_risk"),
                    recommended_mitigations=mode_data.get("recommended_mitigations"),
                    detection_strategies=mode_data.get("detection_strategies"),
                    implementation_notes=mode_data.get("implementation_notes"),
                    related_modes=mode_data.get("related_modes")
                )
                failure_modes[mode_id] = failure_mode

        return failure_modes

    def get_failure_mode(self, mode_id: str) -> Optional[FailureMode]:
        """Get a specific failure mode by ID."""
        if self._failure_modes is None:
            self._failure_modes = self._parse_failure_modes()

        return self._failure_modes.get(mode_id)

    def get_all_failure_modes(self) -> Dict[str, FailureMode]:
        """Get all failure modes."""
        if self._failure_modes is None:
            self._failure_modes = self._parse_failure_modes()

        return self._failure_modes

    def get_failure_modes_by_category(self, category: str) -> List[FailureMode]:
        """Get all failure modes in a specific category."""
        all_modes = self.get_all_failure_modes()
        return [mode for mode in all_modes.values() if mode.category == category]

    def get_failure_modes_by_pillar(self, pillar: str) -> List[FailureMode]:
        """Get all failure modes in a specific pillar (security or safety)."""
        all_modes = self.get_all_failure_modes()
        return [mode for mode in all_modes.values() if mode.pillar == pillar]

    def get_novel_failure_modes(self) -> List[FailureMode]:
        """Get all novel failure modes (unique to agentic AI)."""
        all_modes = self.get_all_failure_modes()
        return [mode for mode in all_modes.values() if mode.novel]

    def get_existing_failure_modes(self) -> List[FailureMode]:
        """Get all existing failure modes (from other AI systems but increased risk)."""
        all_modes = self.get_all_failure_modes()
        return [mode for mode in all_modes.values() if not mode.novel]

    def search_failure_modes(self, query: str) -> List[FailureMode]:
        """Search failure modes by description or example content."""
        all_modes = self.get_all_failure_modes()
        query_lower = query.lower()

        results = []
        for mode in all_modes.values():
            if (query_lower in mode.description.lower()
                    or query_lower in mode.example.lower()
                    or query_lower in mode.potential_impact.lower()):
                results.append(mode)

        return results

    def get_guidance_for_failure_mode(self, mode_id: str) -> Optional[Dict[str, Any]]:
        """Get comprehensive guidance for a specific failure mode."""
        failure_mode = self.get_failure_mode(mode_id)
        if not failure_mode:
            return None
            
        guidance = {
            "id": failure_mode.id,
            "description": failure_mode.description,
            "category": failure_mode.category,
            "pillar": failure_mode.pillar,
            "novel": failure_mode.novel,
            "recommended_mitigations": failure_mode.recommended_mitigations or [],
            "detection_strategies": failure_mode.detection_strategies or [],
            "implementation_notes": failure_mode.implementation_notes or [],
            "related_modes": failure_mode.related_modes or [],
            "potential_effects": failure_mode.potential_effects,
            "example": failure_mode.example
        }
        
        return guidance

    def validate_taxonomy(self) -> List[str]:
        """Validate the taxonomy structure and return any errors."""
        errors = []

        try:
            if self._taxonomy_data is None:
                self.load_taxonomy()

            # Check required top-level categories
            required_categories = [
                "novel_security", "novel_safety", "existing_security", "existing_safety"
            ]
            for category in required_categories:
                if category not in self._taxonomy_data:
                    errors.append(f"Missing required category: {category}")

            # Check structure of each failure mode
            for category, modes in self._taxonomy_data.items():
                for mode_id, mode_data in modes.items():
                    required_fields = [
                        "pillar", "novel", "description", "potential_impact",
                        "potential_effects", "systems_likely_to_occur", "example",
                        "canonical_effects", "refs"
                    ]

                    for field in required_fields:
                        if field not in mode_data:
                            errors.append(
                                f"Missing required field '{field}' in "
                                f"{category}.{mode_id}"
                            )

                    # Validate pillar values
                    if mode_data.get("pillar") not in ["security", "safety"]:
                        errors.append(
                            f"Invalid pillar value in {category}.{mode_id}: "
                            f"{mode_data.get('pillar')}"
                        )

                    # Validate novel field consistency
                    is_novel = "novel" in category
                    if mode_data.get("novel") != is_novel:
                        errors.append(
                            f"Inconsistent novel field in {category}.{mode_id}"
                        )

        except Exception as e:
            errors.append(f"Error validating taxonomy: {str(e)}")

        return errors

    def get_taxonomy_stats(self) -> Dict[str, Any]:
        """Get statistics about the taxonomy."""
        all_modes = self.get_all_failure_modes()

        stats = {
            "total_failure_modes": len(all_modes),
            "novel_modes": len(self.get_novel_failure_modes()),
            "existing_modes": len(self.get_existing_failure_modes()),
            "security_modes": len(self.get_failure_modes_by_pillar("security")),
            "safety_modes": len(self.get_failure_modes_by_pillar("safety")),
            "by_category": {}
        }

        for category in [
            "novel_security", "novel_safety", "existing_security", "existing_safety"
        ]:
            stats["by_category"][category] = len(
                self.get_failure_modes_by_category(category)
            )

        return stats


# Global instance for easy access
_default_taxonomy_loader = None


def get_taxonomy_loader() -> TaxonomyLoader:
    """Get the default taxonomy loader instance."""
    global _default_taxonomy_loader
    if _default_taxonomy_loader is None:
        _default_taxonomy_loader = TaxonomyLoader()
    return _default_taxonomy_loader


def get_failure_mode(mode_id: str) -> Optional[FailureMode]:
    """Convenience function to get a failure mode by ID."""
    return get_taxonomy_loader().get_failure_mode(mode_id)


def search_failure_modes(query: str) -> List[FailureMode]:
    """Convenience function to search failure modes."""
    return get_taxonomy_loader().search_failure_modes(query)
