import logging

# Configure system-wide logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Set up logger for the package
logger = logging.getLogger(__name__)


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
