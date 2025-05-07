import re
import os
import logging
from typing import List, Tuple, Dict, Set

logger = logging.getLogger(__name__)

class Parser:
    @staticmethod
    def collect_c_cpp_files(path: str, recursive: bool = True) -> List[str]:
        """
        Return a list of C/C++ source and header files from a file or directory path.
        Searches recursively by default.
        Supported extensions: .c, .cpp, .h, .hpp
        """
        collected_files: List[str] = []
        supported_extensions: Set[str] = {'.c', '.cpp', '.h', '.hpp'}

        if os.path.isfile(path):
            if os.path.splitext(path)[1] in supported_extensions:
                collected_files.append(os.path.abspath(path))
        elif os.path.isdir(path):
            for root, _, files in os.walk(path):
                for fname in files:
                    if os.path.splitext(fname)[1] in supported_extensions:
                        collected_files.append(os.path.abspath(os.path.join(root, fname)))
                if not recursive:
                    break
        else:
            logger.warning(f"Path not found or is not a file/directory: {path}")

        if not collected_files:
            logger.debug(f"No C/C++ files found in: {path}")
        return collected_files

    @staticmethod
    def find_matching_tests(test_paths: List[str], source_base_name: str) -> List[str]:
        """Find test files whose name contains the source base name."""
        if not source_base_name:
            return []
        return [
            test_path for test_path in test_paths
            if source_base_name in os.path.splitext(os.path.basename(test_path))[0]
        ]

    @staticmethod
    def get_function_name(source_lines: List[str], line_idx: int) -> str:
        """
        Extract the function name for a given line index in C/C++ code,
        scanning upwards for a function definition. This is a best-effort
        approach using regex and may not cover all C/C++ syntax complexities.
        """
        # Regex attempts to match: type_and_modifiers function_name (params) {
        # It allows for pointers (*), references (&), and 'const' modifiers.
        pattern = re.compile(
            r'^\s*[\w\s\*&:,<>]+?\s+([a-zA-Z_][a-zA-Z0-9_:]*(?:<[^>]*>)?)\s*\([^)]*\)\s*(?:const)?\s*(?:throw\s*\([^)]*\))?\s*\{'
        )
        for i in range(line_idx, -1, -1):
            line = source_lines[i].strip()
            # Basic skip for lines that are obviously not function definitions
            if not line or \
               line.startswith('//') or \
               line.startswith('/*') or \
               line.startswith('*') or \
               line.startswith('#') or \
               line.startswith('}') or \
               line.endswith(';') : # e.g. struct/class definitions, forward declarations
                continue
            m = pattern.match(line)
            if m:
                func_name = m.group(1)
                # Avoid matching 'if', 'for', 'while', 'switch' as function names
                if func_name not in ['if', 'for', 'while', 'switch']:
                    return func_name
        logger.debug(f"Could not determine function name for mutation point near line {line_idx + 1}. Defaulting to 'unknownfunc'.")
        return "unknownfunc"

    @staticmethod
    def group_mutation_points_by_function(mutation_points: List[Tuple[int, int, str]], source_lines: List[str]) -> Dict[str, List[Tuple[int, int, str]]]:
        """Group mutation points by function name."""
        func_mut_points: Dict[str, List[Tuple[int, int, str]]] = {}
        for point in mutation_points:
            line_idx, _, _ = point
            func_name = Parser.get_function_name(source_lines, line_idx)
            func_mut_points.setdefault(func_name, []).append(point)
        return func_mut_points

    @staticmethod
    def find_mutation_points(source_code: str) -> List[Tuple[int, int, str]]:
        """
        Finds all mutation operator points, skipping those in comments, string/char literals,
        and preprocessor directives.
        Operators: +, -, *, /, ==, !=, >, <, >=, <=, &&, ||
        """
        points: List[Tuple[int, int, str]] = []
        in_block_comment: bool = False

        # Order matters: longer operators first (e.g., >= before >)
        operator_patterns = [
            (r'==', '=='), (r'!=', '!='), (r'>=', '>='), (r'<=', '<='),
            (r'&&', '&&'), (r'\|\|', '||'),
            (r'\+', '+'), (r'-', '-'), (r'\*', '*'), (r'/', '/'),
            (r'>', '>'), (r'<', '<')
        ]

        source_lines = source_code.splitlines()

        for idx, original_line in enumerate(source_lines):
            line_to_process = original_line

            # 1. Handle block comments
            # Create a version of the line where comments are replaced by spaces
            # to preserve character indexing for operator finding.
            processed_chars = list(original_line)

            # Handle block comments continuing from previous lines or starting/ending on this line
            temp_line_idx = 0
            while temp_line_idx < len(processed_chars):
                if in_block_comment:
                    if temp_line_idx + 1 < len(processed_chars) and \
                       processed_chars[temp_line_idx] == '*' and processed_chars[temp_line_idx+1] == '/':
                        processed_chars[temp_line_idx] = ' '
                        processed_chars[temp_line_idx+1] = ' '
                        in_block_comment = False
                        temp_line_idx += 2
                    else:
                        processed_chars[temp_line_idx] = ' '
                        temp_line_idx += 1
                elif temp_line_idx + 1 < len(processed_chars) and \
                     processed_chars[temp_line_idx] == '/' and processed_chars[temp_line_idx+1] == '*':
                    processed_chars[temp_line_idx] = ' '
                    processed_chars[temp_line_idx+1] = ' '
                    in_block_comment = True
                    temp_line_idx += 2
                else:
                    temp_line_idx += 1
            
            line_after_block_comments = "".join(processed_chars)

            # 2. Handle line comments (replace with spaces)
            line_after_line_comments = re.sub(r'//.*', lambda m: ' ' * len(m.group(0)), line_after_block_comments)

            # 3. Handle string literals (replace with spaces)
            # Handles simple escaped quotes like \"
            line_after_strings = re.sub(r'"(\\.|[^"\\])*"', lambda m: ' ' * len(m.group(0)), line_after_line_comments)

            # 4. Handle char literals (replace with spaces)
            line_after_chars = re.sub(r"'(\\.|[^'\\])*'", lambda m: ' ' * len(m.group(0)), line_after_strings)

            # 5. Skip preprocessor directives
            if line_after_chars.strip().startswith('#'):
                continue

            # 6. Find operators in the processed line
            for pattern, op in operator_patterns:
                try:
                    for match in re.finditer(pattern, line_after_chars):
                        # Sanity check: ensure the matched operator in the processed line
                        # corresponds to the same operator in the original line at that position.
                        # This helps avoid mutating parts of complex tokens that were partially spaced out.
                        original_segment = original_line[match.start() : match.end()]
                        if op in original_segment and not (op == '/' and original_segment.startswith('/*')) and not (op == '/' and original_segment.startswith('//')):
                             # Additional check for division operator to not pick up start of comments if somehow missed
                            points.append((idx, match.start(), op))
                except re.error as e:
                    logger.error(f"Regex error finding operator '{op}' on line {idx+1}: {e}. Line: '{line_after_chars}'")

        if not points:
            logger.debug(f"No mutation points found in the provided source code.")
        else:
            logger.debug(f"Found {len(points)} potential mutation points.")
        return points
