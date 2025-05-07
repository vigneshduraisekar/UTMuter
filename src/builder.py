# builder.py
"""
Module for building (compiling) C/C++ code.
"""
import subprocess
import logging

logger = logging.getLogger(__name__)

class Builder:
    @staticmethod
    def build_sources(source_paths, output_path, compiler="gcc", flags=None):
        """
        Compiles the C/C++ source file(s) using the specified compiler.
        :param source_paths: A list of source file paths.
        :param output_path: The path for the compiled output binary.
        :param compiler: The compiler command (e.g., 'gcc', 'g++', 'clang').
        :param flags: A list of additional compiler flags.
        :return: True if compilation is successful, False otherwise.
        """
        command = [compiler] + (flags if flags else []) + source_paths + ['-o', output_path]
        logger.debug(f"Build command: {' '.join(command)}")
        try:
            subprocess.check_call(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Build failed for {' '.join(source_paths)}: {e.stderr.decode() if e.stderr else e}")
            return False
