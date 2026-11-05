"""Read and print the contents of a requested .txt statement file."""

import sys

from mcp_server import read_test_statement_file


def main() -> None:
    file_name = sys.argv[1] if len(sys.argv) > 1 else input("Enter the .txt file name to read: ").strip()

    if not file_name:
        raise ValueError("Please provide a .txt file name.")

    if not file_name.lower().endswith(".txt"):
        raise ValueError("Only .txt files are supported.")

    print(read_test_statement_file(file_name=file_name, container_name="test-statements"))


if __name__ == "__main__":
    main()
