# Agentic FMEA

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

**Failure Mode and Effects Analysis (FMEA) for Agentic AI Systems**

A Python library for conducting systematic risk analysis of agentic AI systems using the failure mode taxonomy developed by Microsoft's AI Red Team.

## 🚨 Why This Matters

Agentic AI systems are moving from proof-of-concept to production. Unlike traditional AI models, these systems can:
- Make autonomous decisions
- Modify their own behavior through memory
- Interact with external tools and systems
- Collaborate with other agents

This introduces entirely new failure modes that existing AI safety frameworks don't adequately address.

## 🎯 Features

- **Comprehensive Taxonomy**: 27 failure modes from Microsoft's AI Red Team research
- **Risk Assessment**: Traditional FMEA methodology (Severity × Occurrence × Detection)
- **Report Generation**: Markdown, CSV, and HTML export formats
- **Visualization**: Risk matrices and distribution charts
- **Case Studies**: Real-world examples including memory poisoning attacks
- **Extensible**: Easy to add custom failure modes and risk assessments

## 📦 Installation

```bash
pip install agentic-fmea
```

Or install from source:

```bash
git clone https://github.com/etherium/agentic-fmea.git
cd agentic-fmea
pip install -e .
```

## 🚀 Quick Start

```python
from agentic_fmea import FMEAEntry, FMEAReport, SystemType, Subsystem, DetectionMethod
from agentic_fmea import RiskCalculator, FMEAReportGenerator
from datetime import datetime

# Create an FMEA entry for memory poisoning
entry = FMEAEntry(
    id="memory_poisoning_001",
    taxonomy_id="memory_poisoning",
    system_type=SystemType.MULTI_AGENT_COLLABORATIVE,
    subsystem=Subsystem.MEMORY,
    cause="Malicious email with embedded instructions",
    effect="Agent forwards sensitive information to unauthorized recipients",
    severity=8,  # High severity
    occurrence=6,  # Moderate occurrence
    detection=7,  # Hard to detect
    detection_method=DetectionMethod.LIVE_TELEMETRY,
    mitigation=["Input validation", "Memory access controls"],
    agent_capabilities=["autonomy", "memory", "environment_interaction"],
    potential_effects=["Agent misalignment", "Agent action abuse"],
    created_date=datetime.now(),
    last_updated=datetime.now(),
    created_by="Security Team"
)

# RPN is calculated automatically: 8 × 6 × 7 = 336 (High Risk)
print(f"Risk Priority Number: {entry.rpn}")
print(f"Risk Level: {entry.risk_level}")

# Create a report
report = FMEAReport(
    title="Email Assistant Security Analysis",
    system_description="Agentic AI email assistant with memory capabilities",
    entries=[entry],
    created_date=datetime.now(),
    created_by="Security Team"
)

# Generate markdown report
generator = FMEAReportGenerator()
markdown_report = generator.generate_markdown_report(report)
print(markdown_report)
```

## 📊 Failure Mode Taxonomy

The library includes Microsoft's comprehensive taxonomy of 27 failure modes across 4 categories:

### Novel Security Failures (6 modes)
- **Agent Compromise**: Hijacking existing agents
- **Agent Injection**: Introducing malicious agents  
- **Agent Impersonation**: Fake agents mimicking legitimate ones
- **Agent Flow Manipulation**: Disrupting agent communication
- **Agent Provisioning Poisoning**: Corrupting agent deployment
- **Multi-Agent Jailbreaks**: Coordinated attacks across agents

### Novel Safety Failures (4 modes)
- **Intra-Agent RAI Issues**: Harmful content in agent communications
- **Harms of Allocation**: Biased resource distribution
- **Organizational Knowledge Loss**: Over-reliance on agents
- **Prioritization Safety Issues**: Agents prioritizing goals over safety

### Existing Security Failures (10 modes)
- **Memory Poisoning**: Corrupting agent memory
- **Targeted Knowledge Base Poisoning**: Malicious training data
- **Cross-Domain Prompt Injection**: Indirect prompt manipulation
- **Human-in-the-Loop Bypass**: Circumventing human oversight
- **Tool Compromise**: Exploiting agent tools
- **Incorrect Permissions**: Privilege escalation
- **Resource Exhaustion**: Denial of service attacks
- **Insufficient Isolation**: Breaking containment
- **Excessive Agency**: Agents exceeding intended scope
- **Loss of Data Provenance**: Untraceable information flow

### Existing Safety Failures (8 modes)
- **Insufficient Transparency**: Poor auditability
- **User Impersonation**: Agents pretending to be human
- **Parasocial Relationships**: Unhealthy user attachments
- **Bias Amplification**: Reinforcing harmful biases
- **Insufficient Consent**: Inadequate user consent mechanisms
- **Hallucinations**: False information generation
- **Misinterpretation**: Incorrect understanding of instructions

## 🔍 Case Study: Memory Poisoning Attack

The library includes a detailed case study of a memory poisoning attack on an agentic AI email assistant, based on Microsoft's research showing an 80% attack success rate.

Run the example:

```python
# See examples/memory_poisoning_email_assistant.ipynb
jupyter notebook examples/memory_poisoning_email_assistant.ipynb
```

## 📈 Risk Analysis

The library provides comprehensive risk analysis capabilities:

```python
from agentic_fmea import RiskCalculator

calculator = RiskCalculator()

# Analyze a single entry
risk_score = calculator.calculate_risk_score(entry)
print(f"RPN: {risk_score['rpn']}")
print(f"Risk Level: {risk_score['risk_level']}")
print(f"Severity: {risk_score['severity_label']}")

# Analyze entire report
analysis = calculator.analyze_report_risk(report)
print(f"Mean RPN: {analysis['statistics']['mean_rpn']}")
print(f"High Risk Entries: {analysis['risk_distribution']['High']}")

# Get recommendations
recommendations = calculator.recommend_actions(entry)
for rec in recommendations:
    print(f"- {rec}")
```

## 📋 Report Generation

Generate comprehensive reports in multiple formats:

```python
from agentic_fmea import FMEAReportGenerator

generator = FMEAReportGenerator()

# Markdown report
markdown = generator.generate_markdown_report(report)
generator.save_markdown_report(report, "fmea_report.md")

# CSV export
csv_data = generator.generate_csv_export(report)
generator.save_csv_export(report, "fmea_export.csv")

# HTML report
html = generator.generate_html_report(report)
```

## 📊 Visualization

Create risk matrices and distribution charts:

```python
import matplotlib.pyplot as plt
from agentic_fmea import RiskCalculator

calculator = RiskCalculator()

# Risk distribution plot
fig = calculator.plot_risk_distribution(report)
plt.show()

# Risk matrix
fig = calculator.plot_risk_matrix(report.entries, 
                                 x_axis="occurrence", 
                                 y_axis="severity")
plt.show()
```

## 🏗️ Architecture

The library is structured around four core modules:

- **`entry.py`**: Core data structures (FMEAEntry, FMEAReport)
- **`taxonomy.py`**: Failure mode taxonomy management
- **`risk.py`**: Risk calculation and analysis
- **`report.py`**: Report generation and export

## 🔧 Advanced Usage

### Custom Risk Thresholds

```python
from agentic_fmea import RiskThresholds, RiskCalculator

custom_thresholds = RiskThresholds(
    critical=400,
    high=150,
    medium=75
)

calculator = RiskCalculator(thresholds=custom_thresholds)
```

### Adding Custom Failure Modes

```python
from agentic_fmea import TaxonomyLoader

loader = TaxonomyLoader()
taxonomy = loader.load_taxonomy()

# Add your custom failure modes to the taxonomy
taxonomy["custom_security"]["my_failure_mode"] = {
    "pillar": "security",
    "novel": True,
    "description": "Custom failure mode description",
    # ... other required fields
}
```

## 🔬 Research Foundation

This library is based on:

- **Microsoft AI Red Team**: "Taxonomy of Failure Modes in Agentic AI Systems" (2025)
- **NASA Software Engineering**: Software FMEA methodology
- **Traditional FMEA**: MIL-STD-1629 standard

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup

```bash
git clone https://github.com/etherium/agentic-fmea.git
cd agentic-fmea
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Quality

```bash
black agentic_fmea/
ruff check agentic_fmea/
mypy agentic_fmea/
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Microsoft AI Red Team for the comprehensive failure mode taxonomy
- NASA Software Engineering Handbook for FMEA methodology
- The broader AI safety research community

## 📚 Citation

If you use this library in your research, please cite:

```bibtex
@software{agentic_fmea,
  author = {Claude and Karthi},
  title = {Agentic FMEA: Failure Mode and Effects Analysis for Agentic AI Systems},
  url = {https://github.com/etherium/agentic-fmea},
  version = {0.1.0},
  year = {2025}
}
```

---

**Built with 🤖 by [Etherium](https://github.com/etherium) - Infrastructure as an act of love**