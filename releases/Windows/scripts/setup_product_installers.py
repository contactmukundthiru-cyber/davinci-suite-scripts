#!/usr/bin/env python3
"""
Generate installers for each standalone product.

This script copies and customizes the installer template for each tool
in the products/ directory.
"""

import os
from pathlib import Path

PRODUCTS_DIR = Path(__file__).parent.parent / "products"
TEMPLATE_FILE = PRODUCTS_DIR / "install_template.sh"

# Tool ID to display name mapping
TOOL_NAMES = {
    "t1_revision_resolver": "Revision Resolver",
    "t2_relink_across_projects": "Relink Across Projects",
    "t3_smart_reframer": "Smart Reframer",
    "t4_caption_layout_protector": "Caption Layout Protector",
    "t5_feedback_compiler": "Feedback Compiler",
    "t6_timeline_normalizer": "Timeline Normalizer",
    "t7_component_graphics": "Component Graphics",
    "t8_delivery_spec_enforcer": "Delivery Spec Enforcer",
    "t9_change_impact_analyzer": "Change Impact Analyzer",
    "t10_brand_drift_detector": "Brand Drift Detector",
}


def generate_installer(tool_id: str, tool_name: str, product_dir: Path):
    """Generate a customized installer for a tool."""
    template = TEMPLATE_FILE.read_text()

    # Replace placeholders
    customized = template.replace(
        'TOOL_NAME="Tool Name"',
        f'TOOL_NAME="{tool_name}"'
    ).replace(
        'TOOL_ID="t1_revision_resolver"',
        f'TOOL_ID="{tool_id}"'
    )

    installer_path = product_dir / "install.sh"
    installer_path.write_text(customized)
    installer_path.chmod(0o755)

    print(f"  Created: {installer_path}")


def main():
    print("Setting up standalone product installers...")
    print()

    if not TEMPLATE_FILE.exists():
        print(f"Error: Template not found at {TEMPLATE_FILE}")
        return 1

    for tool_id, tool_name in TOOL_NAMES.items():
        product_dir = PRODUCTS_DIR / tool_id

        if product_dir.exists():
            generate_installer(tool_id, tool_name, product_dir)
        else:
            print(f"  Skipped: {tool_id} (directory not found)")

    print()
    print("Done! Each product now has its own install.sh")
    return 0


if __name__ == "__main__":
    exit(main())
