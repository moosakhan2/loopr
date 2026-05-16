"""
CLI entry point for the recursive testing agent.

Usage:
    python -m agent.cli ./sample-repo
    python -m agent.cli /path/to/your/project
"""

import argparse
import sys
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from agent.loop import run


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="loopr",
        description="Recursive AI-powered testing agent that finds bugs, suggests fixes, and loops until your codebase is clean.",
        epilog="Built with IBM Bob. Powered by watsonx.ai."
    )
    
    parser.add_argument(
        "path",
        type=str,
        help="Path to the target repository to test"
    )
    
    parser.add_argument(
        "--coverage",
        type=int,
        default=85,
        help="Target coverage threshold (default: 85)"
    )
    
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=3,
        help="Maximum number of iterations (default: 3)"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Suggest fixes without applying them"
    )
    
    parser.add_argument(
        "--auto-approve",
        action="store_true",
        help="Apply all fixes without prompting"
    )
    
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    # Validate path exists
    target_path = Path(args.path)
    if not target_path.exists():
        print(f"❌ Error: Path does not exist: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    if not target_path.is_dir():
        print(f"❌ Error: Path is not a directory: {args.path}", file=sys.stderr)
        sys.exit(1)
    
    # Print header
    print("🔁 Loopr - Recursive Testing Agent")
    print("=" * 60)
    print(f"Target: {target_path.absolute()}")
    print(f"Coverage goal: {args.coverage}%")
    print(f"Max iterations: {args.max_iterations}")
    if args.dry_run:
        print("Mode: Dry run (no fixes will be applied)")
    if args.auto_approve:
        print("Mode: Auto-approve (all fixes will be applied)")
    print("=" * 60)
    print()
    
    try:
        # Run the loop
        result = run(str(target_path.absolute()))
        
        # Print final status
        print("\n✨ Run completed successfully!")
        
        # Exit with appropriate code
        if result["tests_failed"] > 0:
            sys.exit(1)  # Exit with error if tests failed
        else:
            sys.exit(0)  # Exit successfully if all tests passed
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

# Made with Bob
