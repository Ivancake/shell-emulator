"""Точка входа эмулятора оболочки."""

import sys

from repl import repl

def main():
    """Запускает эмулятор и завершает процесс с его кодом возврата."""
    sys.exit(repl())

if __name__ == "__main__":
    main()