# UTMuter: Automatic Mutation Testing for C/C++ Unit Tests

UTMuter is a Python-based framework for mutation testing of C and C++ codebases. It identifies mutation points in your source files, applies mutation operators, rebuilds the code, runs your unit tests, and reports which mutants are killed or survived.

## Features
- Parses C/C++ source files to identify mutation points
- Applies common mutation operators (arithmetic, logical, relational, etc.)
- Automates build and test execution for each mutant
- Generates detailed mutation testing reports (killed/survived mutants)

## Project Structure
- `src/` — Python modules:
  - `main.py`: Entry point for mutation testing
  - `parser.py`: Source code parsing and mutation point detection
  - `mutator.py`: Mutation operator logic
  - `builder.py`: Handles build automation
  - `tester.py`: Executes unit tests and collects results
  - `reporter.py`: Generates mutation testing reports
- `mutant/` — Generated mutant source files (auto-created)

## Getting Started
1. Place your C/C++ source and test files in the workspace.
2. Ensure your test source files can be compiled and run with the mutated source.
3. Run the main script to start mutation testing.

## Requirements
- Python 3.8+
- C/C++ compiler (e.g., gcc, clang)
- Existing unit tests as C/C++ source files

## Usage

Basic usage:
```
python src/main.py --source <source_file_or_dir> [<source_file_or_dir> ...] --test <test_file_or_dir> [--mut <mutant_output_dir>]
```
- `--source`: Path(s) to C/C++ source file(s) or directory(ies) to mutate.
- `--test`: Path to a C/C++ test source file or directory.
- `--mut`: (Optional) Path to output mutant source folder (default: `mutant`).

Example:
```
python src/main.py --source test_project/src/example.c --test test_project/test/
```

## Output
- Mutated source files are saved in the `mutant/` directory.
- Mutation testing results are printed to the console.

## License
MIT
