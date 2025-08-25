def main():
    """Main CLI entry point."""
    from fresh_blt.cli import main as _main
    return _main()


__all__ = ["models", "grammar", "parse", "cli", "main"]
