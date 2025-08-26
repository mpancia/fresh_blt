def main():
    """Main CLI entry point."""
    from fresh_blt.cli import main as _main
    return _main()


# Import fixtures for easy access
from .fixtures import BLTGenerators, BLTProvider

__all__ = [
    "models",
    "grammar",
    "parse",
    "cli",
    "export",
    "fixtures",
    "main",
    # Fixture exports
    "BLTProvider",
    "BLTGenerators",
]
