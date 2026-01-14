"""
Setup script for CardioCode - Installation without build tools.
"""

from setuptools import setup, find_packages

setup(
    name="cardiocode",
    version="1.0.0",
    description="ESC Guidelines encoded as executable clinical logic",
    long_description="""
    CardioCode is a comprehensive cardiology decision support system that encodes European Society 
    of Cardiology (ESC) clinical guidelines as executable Python code.
    
    Features:
    • 9 complete ESC guideline modules (2019-2024)
    • 15 MCP tools for clinical decision support
    • Automatic PDF ingestion and knowledge extraction
    • Type-safe recommendations with evidence levels
    • Cross-guideline conflict detection
    • Ready-to-use MCP server
    
    Guidelines Included:
    • Heart Failure (ESC 2021)
    • Ventricular Arrhythmias (ESC 2022)
    • Pulmonary Hypertension (ESC 2022)
    • Cardio-Oncology (ESC 2022)
    • Valvular Heart Disease (ESC 2021)
    • Atrial Fibrillation (ESC 2020/2024)
    • Chronic Coronary Syndromes (ESC 2019)
    • NSTE-ACS (ESC 2020)
    • STEMI (ESC 2023)
    
    Installation:
    pip install cardiocode
    
    Usage:
    python -m cardiocode.mcp.server  # Start MCP server
    """,
    author="miltosdoc",
    author_email="miltosdoc@users.noreply.github.com",
    url="https://github.com/miltosdoc/cardiocode",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Medical Science",
    ],
    python_requires=">=3.8",
    install_requires=[
        "mcp>=1.0.0",
        "dataclasses>=0.6; python_version<'3.11'",
        "enum34>=1.1.10; python_version<'3.11'",
    ],
    entry_points={
        "console_scripts": [
            "cardiocode-mcp=cardiocode.mcp.server:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=[
        "cardiology", "esc guidelines", "medical ai", "clinical decision support",
        "mcp server", "atrial fibrillation", "heart failure",
        "valvular disease", "coronary syndromes",
    ],
    project_urls={
        "Bug Reports": "https://github.com/miltosdoc/cardiocode/issues",
        "Source": "https://github.com/miltosdoc/cardiocode",
        "Documentation": "https://github.com/miltosdoc/cardiocode/blob/main/README.md",
    },
)