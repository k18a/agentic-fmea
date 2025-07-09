#!/usr/bin/env python3
"""
Example demonstrating the flexible enum system in agentic-fmea.

This example shows how to use the new OTHER enum values with custom fields
to handle real-world edge cases that don't fit standard enum categories.
"""

from datetime import datetime
from agentic_fmea import FMEAEntry, SystemType, Subsystem, DetectionMethod

def main():
    print("=== Flexible Enum System Example ===\n")
    
    # Example 1: Standard enum usage (backwards compatible)
    print("1. Standard enum usage (backwards compatible):")
    standard_entry = FMEAEntry(
        id="standard_example",
        taxonomy_id="memory_poisoning",
        system_type=SystemType.SINGLE_AGENT,
        subsystem=Subsystem.MEMORY,
        cause="Malicious input in training data",
        effect="Model outputs harmful content",
        severity=8,
        occurrence=6,
        detection=4,
        detection_method=DetectionMethod.LIVE_TELEMETRY,
        mitigation=["Input validation", "Content filtering"],
        agent_capabilities=["autonomy", "learning"],
        potential_effects=["Reputation damage", "User harm"],
        created_date=datetime.now(),
        last_updated=datetime.now(),
        created_by="Security Team"
    )
    
    print(f"  System Type: {standard_entry.system_type}")
    print(f"  Subsystem: {standard_entry.subsystem}")
    print(f"  Detection Method: {standard_entry.detection_method}")
    print(f"  Custom Fields: {standard_entry.custom_system_type}, {standard_entry.custom_subsystem}, {standard_entry.custom_detection_method}")
    print(f"  RPN: {standard_entry.rpn}\n")
    
    # Example 2: Custom system type for specialized AI architecture
    print("2. Custom system type for specialized AI architecture:")
    federated_entry = FMEAEntry(
        id="federated_learning_example",
        taxonomy_id="model_poisoning",
        system_type=SystemType.OTHER,
        custom_system_type="Federated Learning Network",
        subsystem=Subsystem.OTHER,
        custom_subsystem="Edge Device Coordinator",
        cause="Malicious model updates from compromised edge devices",
        effect="Degraded global model performance and potential data leakage",
        severity=9,
        occurrence=7,
        detection=6,
        detection_method=DetectionMethod.OTHER,
        custom_detection_method="Blockchain-based Consensus Monitoring",
        mitigation=["Byzantine fault tolerance", "Secure aggregation", "Participant verification"],
        agent_capabilities=["distributed_learning", "model_aggregation"],
        potential_effects=["Global model corruption", "Privacy breach"],
        created_date=datetime.now(),
        last_updated=datetime.now(),
        created_by="Federated Learning Team"
    )
    
    print(f"  System Type: {federated_entry.system_type} -> {federated_entry.custom_system_type}")
    print(f"  Subsystem: {federated_entry.subsystem} -> {federated_entry.custom_subsystem}")
    print(f"  Detection Method: {federated_entry.detection_method} -> {federated_entry.custom_detection_method}")
    print(f"  RPN: {federated_entry.rpn}\n")
    
    # Example 3: Healthcare AI system with domain-specific requirements
    print("3. Healthcare AI system with domain-specific requirements:")
    healthcare_entry = FMEAEntry(
        id="healthcare_ai_example",
        taxonomy_id="bias_amplification",
        system_type=SystemType.OTHER,
        custom_system_type="Clinical Decision Support System",
        subsystem=Subsystem.OTHER,
        custom_subsystem="HIPAA Compliance Module",
        cause="Biased training data from non-representative patient populations",
        effect="Inappropriate treatment recommendations for minority groups",
        severity=10,  # Critical in healthcare
        occurrence=5,
        detection=3,
        detection_method=DetectionMethod.OTHER,
        custom_detection_method="Medical Professional Review Board",
        mitigation=[
            "Diverse dataset collection",
            "Regular bias audits",
            "Clinical validation studies",
            "Continuous monitoring by medical professionals"
        ],
        agent_capabilities=["clinical_reasoning", "patient_assessment"],
        potential_effects=["Patient harm", "Health disparities", "Loss of trust"],
        created_date=datetime.now(),
        last_updated=datetime.now(),
        created_by="Healthcare AI Ethics Team"
    )
    
    print(f"  System Type: {healthcare_entry.system_type} -> {healthcare_entry.custom_system_type}")
    print(f"  Subsystem: {healthcare_entry.subsystem} -> {healthcare_entry.custom_subsystem}")
    print(f"  Detection Method: {healthcare_entry.detection_method} -> {healthcare_entry.custom_detection_method}")
    print(f"  RPN: {healthcare_entry.rpn}\n")
    
    # Example 4: Mixed usage - some standard, some custom
    print("4. Mixed usage - some standard enums, some custom:")
    mixed_entry = FMEAEntry(
        id="mixed_example",
        taxonomy_id="prompt_injection",
        system_type=SystemType.SINGLE_AGENT,  # Standard enum
        subsystem=Subsystem.OTHER,  # Custom subsystem
        custom_subsystem="Natural Language Security Filter",
        cause="Adversarial prompts bypass security filters",
        effect="Unauthorized access to sensitive information",
        severity=7,
        occurrence=6,
        detection=5,
        detection_method=DetectionMethod.AUTOMATED_MONITORING,  # Standard enum
        mitigation=["Prompt sanitization", "Content filtering", "Rate limiting"],
        agent_capabilities=["language_understanding", "content_generation"],
        potential_effects=["Data breach", "Privacy violation"],
        created_date=datetime.now(),
        last_updated=datetime.now(),
        created_by="Security Team"
    )
    
    print(f"  System Type: {mixed_entry.system_type} (standard)")
    print(f"  Subsystem: {mixed_entry.subsystem} -> {mixed_entry.custom_subsystem}")
    print(f"  Detection Method: {mixed_entry.detection_method} (standard)")
    print(f"  RPN: {mixed_entry.rpn}\n")
    
    # Example 5: Custom detection methods from different domains
    print("5. Various custom detection methods:")
    custom_detection_methods = [
        ("Peer Review by Domain Experts", "Academic research validation"),
        ("Regulatory Compliance Auditing", "Meeting industry standards"),
        ("A/B Testing with Control Groups", "Statistical significance testing"),
        ("Third-party Security Assessment", "External security evaluation"),
        ("Customer Feedback Analysis", "User experience monitoring")
    ]
    
    for i, (method, description) in enumerate(custom_detection_methods):
        entry = FMEAEntry(
            id=f"custom_detection_{i}",
            taxonomy_id="general_failure",
            system_type=SystemType.SINGLE_AGENT,
            subsystem=Subsystem.PLANNING,
            cause=f"Failure requiring {description}",
            effect="System reliability concerns",
            severity=5,
            occurrence=4,
            detection=3,
            detection_method=DetectionMethod.OTHER,
            custom_detection_method=method,
            mitigation=[f"Implement {method.lower()}"],
            agent_capabilities=["planning"],
            potential_effects=["Service degradation"],
            created_date=datetime.now(),
            last_updated=datetime.now(),
            created_by="Quality Assurance Team"
        )
        print(f"  {method}: RPN = {entry.rpn}")
    
    print("\n=== Summary ===")
    print("The flexible enum system allows:")
    print("- Backwards compatibility with existing standard enums")
    print("- Custom system types for specialized AI architectures")
    print("- Custom subsystems for domain-specific components")
    print("- Custom detection methods for various validation approaches")
    print("- Mixed usage of standard and custom enums in the same entry")
    print("- Proper validation to ensure custom fields are provided when needed")

if __name__ == "__main__":
    main()