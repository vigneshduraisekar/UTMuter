# reporter.py
"""
Module for reporting mutation testing results.
"""

import os
from typing import List, Tuple, Optional

class Reporter:
    @staticmethod
    def report_results(total: int, killed: int, survived: int, mutant_test_records: Optional[List[Tuple[str, str, str, str]]] = None):
        """Prints a summary table of mutation testing results, including mutant/test details if provided."""
        print("\nMutation Testing Report")
        print("+----------------+---------+")
        print("| Result         | Count   |")
        print("+----------------+---------+")
        print(f"| Total mutants  | {total:<7} |")
        print(f"| Killed         | {killed:<7} |")
        print(f"| Survived       | {survived:<7} |")
        print("+----------------+---------+")
        if total > 0:
            score = killed / total * 100
            print(f"| Mutation Score | {score:6.1f}% |")
            print("+----------------+---------+")
        else:
            print(f"| Mutation Score |   N/A   |")
            print("+----------------+---------+")
        if mutant_test_records:
            print("\nDetailed Mutant/Test Results:")
            print("+-----+-------------------------+------------------------------+------------------------------+----------+")
            print("| No. | Source File             | Mutant File                  | Test File                    | Result   |")
            print("+-----+-------------------------+------------------------------+------------------------------+----------+")
            for idx, (mutant_file, test_file, result, source_file) in enumerate(mutant_test_records, 1):
                print(f"| {idx:<3} | {os.path.basename(source_file):<23} | {os.path.basename(mutant_file):<28} | {os.path.basename(test_file):<28} | {result:<8} |")
            print("+-----+-------------------------+------------------------------+------------------------------+----------+")
