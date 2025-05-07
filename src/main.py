import os
import argparse
import logging
from typing import List, Optional, Tuple

from parser import Parser
from mutator import Mutator
from reporter import Reporter

DEFAULT_MUTANTS_SUBDIR = "mutants_output" # Changed from "mutant" to be more descriptive

logger = logging.getLogger(__name__)

class MutationTester:
    def __init__(self, source_args: List[str], test_arg: List[str], base_mutants_dir: Optional[str] = None):
        self.source_args = source_args
        self.test_arg = test_arg

        # Determine mutants_dir
        if base_mutants_dir is None:
            self.mutants_dir = DEFAULT_MUTANTS_SUBDIR
        else:
            self.mutants_dir = os.path.join(base_mutants_dir, DEFAULT_MUTANTS_SUBDIR)
        os.makedirs(self.mutants_dir, exist_ok=True)
        self.source_paths = []
        self.test_paths = []
        self.all_mutant_test_records = []
        self.total = 0
        self.killed = 0
        self.survived = 0

    @staticmethod
    def parse_args() -> argparse.Namespace:
        parser = argparse.ArgumentParser(description="Automatic Mutation Testing for C/C++ Unit Tests")
        parser.add_argument('--source', required=True, nargs='+', help='Path(s) to C/C++ source file(s) or folder(s)')
        parser.add_argument('--test', required=True, help='Path to a C/C++ test source file or folder')
        parser.add_argument('--mut', required=False, help='Base directory to store generated mutant files and binaries.')
        return parser.parse_args()

    def collect_files(self) -> bool:
        self.source_paths = Parser.collect_c_cpp_files(self.source_args)
        if not self.source_paths:
            logger.error(f"No source files found in specified paths: {self.source_args}")
            return False

        self.test_paths = Parser.collect_c_cpp_files(self.test_arg)
        if not self.test_paths:
            logger.error(f"No test source files found in {self.test_arg}")
            return False

        logger.info(f"Found {len(self.source_paths)} source file(s) and {len(self.test_paths)} test file(s).")
        return True

    def run(self):
        if not self.collect_files():
            return

        for source_path in self.source_paths:
            with open(source_path, 'r') as f:
                source_code = f.read()
            mutation_points = Parser.find_mutation_points(source_code)
            if not mutation_points:
                logger.info(f"No mutation points found in {source_path}.")
                continue

            t, k, s, mutant_test_records = Mutator.process_mutants_for_source(
                source_path, source_code, mutation_points, self.test_paths, self.mutants_dir
            )
            self.total += t
            self.killed += k
            self.survived += s
            self.all_mutant_test_records.extend(mutant_test_records)

        Reporter.report_results(
            total=self.total,
            killed=self.killed,
            survived=self.survived,
            mutant_test_records=self.all_mutant_test_records
        )

def main():
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
    print("*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*")
    print("*=*=*=*=*=*=*=*=*=*=*= UTMuter: Automatic Mutation Testing for C/C++ Unit Tests *=*=*=*=*=*=*=*=*=*=*=*")
    print("*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*=*")
    args = MutationTester.parse_args()
    tester = MutationTester(args.source, args.test, args.mut)
    tester.run()

if __name__ == "__main__":
    main()