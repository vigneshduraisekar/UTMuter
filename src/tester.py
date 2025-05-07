# tester.py
"""
Module for running unit tests on compiled binaries.
"""
import subprocess
import logging

logger = logging.getLogger(__name__)

class Tester:
    @staticmethod
    def run_tests(test_command: str) -> bool:
        """Runs the provided test command and returns True if tests pass."""
        logger.debug(f"Running test command: {test_command}")
        try:
            # If test_command is just the path to an executable, shell=True is not strictly needed.
            # If it might contain arguments, passing as a list is safer:
            # e.g., subprocess.check_call([test_command, arg1, arg2], ...)
            subprocess.check_call(test_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            logger.debug(f"Test command '{test_command}' failed. Exit code: {e.returncode}. Stderr: {e.stderr.decode() if e.stderr else 'N/A'}")
            return False
