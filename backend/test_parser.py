"""Test AWR Parser with Real Reports"""

import os
import sys
import json
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.parser.factory import AWRParserFactory


def test_parser(html_file_path):
    """Test parser with a real AWR report"""
    print(f"\n{'='*80}")
    print(f"Testing: {html_file_path}")
    print(f"{'='*80}\n")

    # Read HTML file
    try:
        with open(html_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            html_content = f.read()
        print(f"✓ Successfully read file ({len(html_content)} bytes)")
    except Exception as e:
        print(f"✗ Failed to read file: {e}")
        return False

    # Create parser
    try:
        parser = AWRParserFactory.create_parser(html_content)
        print(f"✓ Created parser: {parser.__class__.__name__}")
    except Exception as e:
        print(f"✗ Failed to create parser: {e}")
        return False

    # Parse report
    try:
        result = parser.parse()
        print(f"✓ Successfully parsed report")
    except Exception as e:
        print(f"✗ Failed to parse report: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Display results
    print("\n" + "-"*80)
    print("PARSING RESULTS:")
    print("-"*80)

    # Instance Info
    if 'instance_info' in result:
        print("\n[Instance Info]")
        for key, value in result['instance_info'].items():
            print(f"  {key}: {value}")

    # Snapshot Info
    if 'snapshot_info' in result:
        print("\n[Snapshot Info]")
        for key, value in result['snapshot_info'].items():
            print(f"  {key}: {value}")

    # Load Profile
    if 'load_profile' in result:
        print(f"\n[Load Profile] - {len(result['load_profile'])} metrics")
        for i, (metric, values) in enumerate(list(result['load_profile'].items())[:5]):
            print(f"  {metric}: {values}")
        if len(result['load_profile']) > 5:
            print(f"  ... and {len(result['load_profile']) - 5} more")

    # Wait Events
    if 'wait_events' in result and 'events' in result['wait_events']:
        events = result['wait_events']['events']
        print(f"\n[Wait Events] - {len(events)} events")
        for event in events[:5]:
            print(f"  {event.get('name', 'Unknown')}: {event.get('time_waited', 0)} ms")
        if len(events) > 5:
            print(f"  ... and {len(events) - 5} more")

    # Top SQL
    if 'top_sql' in result:
        for category, sqls in result['top_sql'].items():
            if sqls:
                print(f"\n[Top SQL - {category}] - {len(sqls)} statements")
                break

    print("\n" + "="*80)
    print("✓ PARSING TEST PASSED")
    print("="*80 + "\n")

    return True


def main():
    """Test all AWR reports in the awrrpt directory"""
    # Get awrrpt directory
    project_root = Path(__file__).parent.parent
    awrrpt_dir = project_root / "awrrpt"

    if not awrrpt_dir.exists():
        print(f"Error: awrrpt directory not found: {awrrpt_dir}")
        return

    # Find all HTML files
    html_files = list(awrrpt_dir.rglob("*.html"))

    if not html_files:
        print(f"No HTML files found in {awrrpt_dir}")
        return

    print(f"Found {len(html_files)} AWR report(s)")
    print()

    # Test each file
    results = {}
    for html_file in sorted(html_files):
        relative_path = html_file.relative_to(awrrpt_dir)
        success = test_parser(str(html_file))
        results[str(relative_path)] = success

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)

    passed = sum(1 for v in results.values() if v)
    failed = len(results) - passed

    for file, success in results.items():
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {file}")

    print()
    print(f"Total: {len(results)} | Passed: {passed} | Failed: {failed}")
    print("="*80)


if __name__ == "__main__":
    main()
