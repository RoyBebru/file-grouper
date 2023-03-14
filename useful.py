# -*- coding: utf-8 -*-

import os
import sys

def silent_quit(exit_code=0):
    """
    Do not raise SystemExit exception and quit
    """
    os._exit(exit_code) 

def switch_to_background() -> None:
    """
    Switching to background allows to untie terminal
    and continue using command line while program
    continue to work
    """
    # Create a child process using os.fork() method.
    # Pid greater than 0 represents the parent process
    if os.fork() > 0:
        silent_quit()
    # Pid equal to 0 represents the created child process
    return None


def remove_prefix(text, prefix):
    """ Removing prefix from string """
    if text.startswith(prefix):
        return text[len(prefix):]
    return text


def remove_suffix(text, suffix):
    """ Removing suffix from string """
    if text.startswith(suffix):
        return text[:len(suffix)]
    return text
