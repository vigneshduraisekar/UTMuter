# mutator.py
"""
Module for applying mutations to C/C++ source code.
"""

import os
import logging
from typing import List, Tuple, Dict, Any

from parser import Parser
from builder import Builder
from tester import Tester
from constants import *

logger = logging.getLogger(__name__)

class Mutator:
    MUTATION_OPERATORS_MAP: Dict[str, str] = {
        '+': '-', '-': '+', '*': '/', '/': '*',
        '==': '!=', '!=': '==', '>': '<', '<': '>', '>=': '<=', '<=': '>=',
        '&&': '||', '||': '&&'
    }

    @staticmethod
    def apply_single_mutation(source_code: str, mutation_point: Tuple[int, int, str]) -> str:
        """Applies a single mutation to the source code at the given mutation point."""
        lines = source_code.splitlines()
        idx, col, op = mutation_point
        line = lines[idx]
        if line[col:col+len(op)] == op and op in Mutator.MUTATION_OPERATORS_MAP:
            mutated_op = Mutator.MUTATION_OPERATORS_MAP[op]
            lines[idx] = line[:col] + mutated_op + line[col+len(op):]
        return '\n'.join(lines)

    @staticmethod
    def generate_combined_mutants(source_code, mutation_points):
        """Generate a single string containing all mutants, each separated and annotated."""
        combined = []
        for idx, point in enumerate(mutation_points):
            mutant_code = Mutator.apply_single_mutation(source_code, point)
            combined.append(f"// ---- Mutant {idx+1} ----\n" + mutant_code + "\n// ---- End Mutant {idx+1} ----\n")
        return '\n'.join(combined)

    @staticmethod
    def process_mutants_for_source(source_path, source_code, mutation_points, test_paths, mutants_dir):
        """Process all mutants for a given source file."""
        total = killed = survived = 0
        mutant_test_records = []
        source_lines = source_code.splitlines()
        base_name = os.path.splitext(os.path.basename(source_path))[0]
        matching_tests = Parser.find_matching_tests(test_paths, base_name)
        print(f"{SHORT_DASH} Processing source file {SHORT_DASH}")
        logger.info(f"Source file: {source_path}")
        logger.info(f"Matching test files for source: \n {matching_tests}")
        if not matching_tests:
            logger.debug(f"No matching test files found for source {source_path}. Skipping.")
            return total, killed, survived, mutant_test_records

        func_mut_points = Parser.group_mutation_points_by_function(mutation_points, source_lines)

        for func_name, points in func_mut_points.items():
            relevant_tests = [
                test_path for test_path in matching_tests
                if func_name in os.path.splitext(os.path.basename(test_path))[0]
            ]
            logger.info(f"Relevant test files for function '{func_name}':\n {relevant_tests}")
            print(LONG_DASH)
            if not relevant_tests:
                logger.debug(f"No relevant test files found for function {func_name} in source {source_path}. Skipping mutants for this function.")
                continue
            for i, point in enumerate(points):
                mutant_base = f"mutant_{base_name}_{func_name}_{i}"
                mutant_code = Mutator.apply_single_mutation(source_code, point)
                mutant_path = os.path.join(mutants_dir, f"{mutant_base}.c")
                with open(mutant_path, 'w') as mf:
                    mf.write(mutant_code)

                mutant_killed = False
                killed_by = None
                survived_by = []
                for test_path in relevant_tests:
                    test_base = os.path.splitext(os.path.basename(test_path))[0]
                    binary_path = os.path.join(mutants_dir, f"{mutant_base}")
                    logger.info(f"Building... [Mutant {mutant_base}]")
                    build_ok = Builder.build_sources([mutant_path, test_path], binary_path)
                    if not build_ok:
                        logger.warning(f"[Pass] [Mutant {mutant_base} | Test {test_base}] Build failed. Counting as killed.")
                        mutant_killed = True
                        killed_by = test_path
                        mutant_test_records.append((mutant_path, test_path, "killed", source_path))
                        break
                    else:
                        logger.info(f"Build Success")

                    logger.info(f"Testing...")
                    result = Tester.run_tests(binary_path)
                    if not result:
                        logger.info(f"[Pass] [Mutant {mutant_base} | Test {test_base}] Killed.")
                        mutant_killed = True
                        killed_by = test_path
                        mutant_test_records.append((mutant_path, test_path, "killed", source_path))
                        break
                    else:
                        logger.error(f"[Fail] [Mutant {mutant_base} | Test {test_base}] Survived this test.")
                        survived_by.append(test_path)
                        mutant_test_records.append((mutant_path, test_path, "survived", source_path))
                print(LONG_DASH)
                
                total += 1
                if mutant_killed:
                    killed += 1
                else:
                    survived += 1

        return total, killed, survived, mutant_test_records
