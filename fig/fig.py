#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
File Grouper
Author: Dmytro Tarasiuk
"""

import gettext
import locale
import os
import sys

import fig.common as common

def main():
    global _

    common.init() # is called only here one time

    try:
        (lang, enc) = locale.getdefaultlocale()
        ix = lang.find('_')
        if ix != -1:
            lang = lang[:ix]
        uk = gettext.translation("fig", localedir='./locale', languages=[lang])
        uk.install()
        _ = uk.gettext # Ukraine
    except:
        _ = lambda _: _

    import fig.core as core

    common._ = _

    core.parse_options()

    """
        option_no_gui | is_wx_installed | is_any_to_work() | What to do
        --------------+-----------------+------------------+--------------------------------------------
    (1)    False     |      True       |        Any       | Work via GUI
    (2)    False     |      False      |        True      | Warning "wxPython absent" and work via CLI
    (3)    False     |      False      |        False     | Warning "wxPython absent" and exit
    (4)    True      |       Any       |        True      | work via CLI
    (5)    True      |       Any       |        False     | print help
    """

    if not common.option_no_gui:
        is_wx_installed = True
        try:
            #👇This module is not installed by default: see wxPython
            if common.is_win:
                # Avoid run error
                os.environ["WXSUPPRESS_SIZER_FLAGS_CHECK"] = "1"
            import wx
        except:
            print(_("*** Warning: wxPython module is not installed"), file=sys.stderr) # (2), (1/2 of 3)
            is_wx_installed = False

        if is_wx_installed:
            from fig.useful import switch_to_background
            from fig.gui import run_gui
            switch_to_background() # it does not work under Windows
            run_gui() # (1)
            quit(0)
        elif core.is_any_to_do():
            core.do_everything() # (1/2 of 3)
        quit(0)

    if core.is_any_to_do():
        core.do_everything() # (4)
    else:
        core.print_usage() # (5)

if __name__ == "__main__":
        main()
