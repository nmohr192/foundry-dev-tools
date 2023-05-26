"""These are miscancellous utility functions/classes."""
import os
from dataclasses import dataclass
from typing import Any, Callable, Sequence


@dataclass
class TailHelper:
    """Tails logs.

    Args:
        print_handler (Callable[[str],Any]): the way it prints the lines e.g. :py:meth:print
            or a :py:class:logging.Logger
        start_message (str | None): the start_message to print before the first line
            or if None it will print a horizontal line
        last_line (int | None): the last line that was printed, if not none the start_message
            will never be printed and the first line will be the line after :py:attr:last_line
    """

    print_handler: "Callable[[str], Any]"
    start_message: "str | None" = None
    last_line: "int | None" = None

    def tail(self, log_lines: "Sequence[str] | None"):
        """Handles the logs.

        If :py:attr:TailHelper.last_line is None it will print the :py:attr:TailHelper.start_message
        and print everything contained int :py:attr:logs
        But if the :py:attr:TailHelper.last_line is an integer it will print the
        logs from that given line number, this will only print new lines.

        Args:
            log_lines (Sequence[str] | None): a list of lines, if None execution will be skipped
        """
        if log_lines is not None:
            if self.last_line is None:
                if self.start_message:
                    self.print_handler(self.start_message)
                else:
                    print_horizontal_line(print_handler=self.print_handler)
                self.print_handler("\n".join(log_lines))
            else:
                new_lines = log_lines[self.last_line :]
                if new_lines:
                    self.print_handler("\n".join(new_lines))
            self.last_line = len(log_lines)


def print_horizontal_line(c: str = "-", print_handler: "Callable[[str],Any]" = print):
    """Print a horizontal line with `:py:attr:c`.

    It uses the amount of terminal columns to print a line of good length
    Args:
        c (str): the char to print
        print_handler (Callable[[str],Any]): the function to use for printing
    """
    print_handler(c * os.get_terminal_size().columns)
