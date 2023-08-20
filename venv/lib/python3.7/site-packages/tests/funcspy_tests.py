#!/usr/bin/env python3
import logging
import unittest
import sys
from pathlib import Path
from unittest.mock import MagicMock

sys.path.insert(
    0, str(Path(__file__).parent.parent)
)  # Add the parent directory of tests to the system path

from myfuncs.funcs import logf, get_asctime, valid_uuid, trunc_str, ran_str

logging.basicConfig(level=logging.DEBUG)


class TestMyFuncs(unittest.TestCase):
    @logf()
    def test_get_asctime(self):
        asctime = get_asctime()
        self.assertIsNotNone(asctime)
        self.assertIsInstance(asctime, str)

    @logf()
    def test_valid_uuid(self):
        uuid_valid = "123e4567-e89b-12d3-a456-426614174000"
        uuid_invalid = "123e4567-e89b-12d3-a456-42661417400"

        self.assertTrue(valid_uuid(uuid_valid))
        self.assertFalse(valid_uuid(uuid_invalid))

    @logf()
    def test_trunc_str(self):
        s = "abcdefg"
        self.assertEqual(trunc_str(s, 5), "ab...")
        self.assertEqual(trunc_str(s, 7), "abcdefg")
        self.assertEqual(trunc_str(s, 10), "abcdefg")
        self.assertEqual(trunc_str(s, 0), "abcd...")

    @logf()
    def test_ran_str(self):
        s1, s2 = ran_str(32), ran_str(32)
        self.assertEqual(len(s1), 32)
        self.assertEqual(len(s1), len(s2))
        self.assertNotEqual(s1, s2)
        s3 = ran_str(16)
        self.assertEqual(len(s3), 16)


class TestLogF(unittest.TestCase):
    @logf()
    def test_logf_decorator(self):
        logger_mock = MagicMock()

        @logf(level=logging.DEBUG, log_args=True, log_return=True, measure_time=True)
        def example_func(a, b):
            return a + b

        with unittest.mock.patch('myfuncs.funcs.logger', logger_mock):
            result = example_func(1, 2)

        self.assertEqual(result, 3)
        self.assertEqual(logger_mock.log.call_count, 2)
        logger_mock.log.assert_any_call(logging.DEBUG, "example_func() | (1, 2) {}")
        log_message = logger_mock.log.call_args_list[1][0][1]
        self.assertTrue(log_message.startswith("example_func()"))
        self.assertTrue(log_message.endswith(" | 3"))

    @logf()
    def test_logf_no_args_no_return_no_time(self):
        logger_mock = MagicMock()

        @logf(level=logging.DEBUG, log_args=False, log_return=False, measure_time=False)
        def example_func(a, b):
            return a + b

        with unittest.mock.patch('myfuncs.funcs.logger', logger_mock):
            result = example_func(1, 2)

        self.assertEqual(result, 3)
        self.assertEqual(logger_mock.log.call_count, 1)

    @logf()
    def test_logf_max_str_len(self):
        logger_mock = MagicMock()

        @logf(
            level=logging.DEBUG,
            log_args=True,
            log_return=True,
            max_str_len=10,
            measure_time=True,
        )
        def example_func(a, b):
            return "abcde" * 1000  # Return a very long string

        with unittest.mock.patch('myfuncs.funcs.logger', logger_mock):
            result = example_func(
                "abcde" * 1000, 2
            )  # Pass a very long string as an argument

        self.assertEqual(result, "abcde" * 1000)
        self.assertEqual(logger_mock.log.call_count, 2)
        log_message = logger_mock.log.call_args_list[1][0][1]
        self.assertTrue(log_message.startswith("example_func()"))
        self.assertTrue("..." in log_message)  # Log message should be truncated

    @logf()
    def test_logf_different_level(self):
        logger_mock = MagicMock()

        @logf(level=logging.WARNING, log_args=True, log_return=True, measure_time=True)
        def example_func(a, b):
            return a + b

        with unittest.mock.patch('myfuncs.funcs.logger', logger_mock):
            result = example_func(1, 2)

        self.assertEqual(result, 3)
        self.assertEqual(logger_mock.log.call_count, 2)
        logger_mock.log.assert_any_call(logging.WARNING, "example_func() | (1, 2) {}")
        log_message = logger_mock.log.call_args_list[1][0][1]
        self.assertTrue(log_message.startswith("example_func()"))
        self.assertTrue(log_message.endswith(" | 3"))


if __name__ == "__main__":
    unittest.main()
