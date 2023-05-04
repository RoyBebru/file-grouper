# -*- coding: utf-8 -*-

import fig.common as common
_ = common._ # for i18n

import wx
import wx.lib.agw.customtreectrl as ctree
import os
import sys
from wx.lib.embeddedimage import PyEmbeddedImage
from pathlib import Path

import fig.core as core
import fig.gui_help as gui_help
import fig.gui_category as gui_category

OPEN_FOLDER_ICON_BUFFER = PyEmbeddedImage(
    b'iVBORw0KGgoAAAANSUhEUgAAABgAAAAYCAYAAADgdz34AAAACXBIWXMAAAsTAAALEwEAmpwY'
    b'AAAAIGNIUk0AAHolAACAgwAA+f8AAIDoAABSCAABFVgAADqXAAAXb9daH5AAAAGRSURBVHja'
    b'7NU9aBRRFAXgb+O6RawExYCmUSMSO8VeBBvBMv4UYi8SkKQO1lZaWGksbETBVixE7QKCW9ho'
    b'saLYSURETUBNMjZnYdjMuMFhOw9c3uPd+859c/+mVRSFUWLMiDFyB62s23EaB7CtpPuAZ/jc'
    b'xMlOvEBRI29xsImDuRDN4RiOluRcdI+bhOghTmECPyts3mMPzqAzkLex3HkXqcQDLGN3jf7u'
    b'X8LXl1VcrLrcxka+pK6i5vOV7ZCVsZ57N3EPS+gNOhiGL3gyxGYCi8lbbxR98CnralWI6nAo'
    b'VXQ4IVyvsdvAkewXMJNieIrFdkXTwWXcyv5bhX4Qv/AR+9MzHZzHVNnBWtYLIe/iGl5tIZz9'
    b'amrFWQcvcQnul0bBdAxfY0eDnJwNz/V+H/RSAW8S0+kG5CdD3sW41O9yBluRrv5X7MNXfMdk'
    b'//B2KYZXGpB3kq9Nj7yRw0cNyHfhTnhmB4fdCTzPUOtWDDRDqmcNx7E3j71aZTiTyvmNFfzY'
    b'oqxkmi6lKTeP6/8//WH4MwD7oHVpnMu90QAAAABJRU5ErkJggg==')

class FileGrouperWindow(wx.Frame):

    def __init__(self, *args, **kw):
        # Ensure the parent's __init__ is called
        super(FileGrouperWindow, self).__init__(*args, **kw, size=(800, 600))

        self.help_window = None # help window is not opened yet
        self.category_window = None # category window is not opened yet
        self.sanity_window = None # sanity window is not opened

        # Disable resizing main window to be too small and
        # prevent GTK annoing messages like the folowing:
        # (fig:131363): Gtk-CRITICAL **: 17:30:08.178: gtk_box_gadget_distribute:
        # assertion 'size >= 0' failed in GtkScrollbar
        self.SetSizeHints(400,300,-1,-1)

        # Create a panel in the frame
        pnl = wx.Panel(self)

        # Put attention text with a larger bold font on it
        label_attention = wx.StaticText(pnl, label="File Grouper")
        font = label_attention.GetFont()
        font.PointSize += 6
        font = font.Bold()
        label_attention.SetFont(font)

        # Titles for From-Tree and To-Tree
        label_title_from = wx.StaticText(pnl, label=_("From"))
        font = label_title_from.GetFont()
        font.PointSize += 4
        font = font.Bold()
        label_title_from.SetFont(font)
        label_title_to = wx.StaticText(pnl, label=_("To"))
        label_title_to.SetFont(font)

        # Create Run Bitmap Button
        bmp = wx.Bitmap(str(Path(__file__).parent / "icon-run.png"))
        self.button_run = wx.BitmapButton(pnl, id=-1, bitmap=bmp, size=(40,36))

        bmp_dir_dialog = OPEN_FOLDER_ICON_BUFFER.GetBitmap();

        text_dir_from = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER)
        text_dir_to = wx.TextCtrl(pnl, style=wx.TE_PROCESS_ENTER)

        button_from = wx.BitmapButton(pnl, id=-1, bitmap=bmp_dir_dialog, size=(48, max(text_dir_from.GetSize()[1], 32)))
        button_to = wx.BitmapButton(pnl, id=-1, bitmap=bmp_dir_dialog, size=(48, max(text_dir_to.GetSize()[1], 32)))

        # To reach text ctrl in OnOpen() event handler
        button_from.my_text_ctrl = text_dir_from
        button_from.my_prepare_project = True
        button_to.my_text_ctrl = text_dir_to
        button_to.my_prepare_project = False

        # Create checkboxes
        cb_make_links = wx.CheckBox(pnl, label = _("Instead removing do file links"))

        #<<< Create From-Tree and To-Tree

        # Create image list common for both trees to add icons next to tree items
        tree_imlist = wx.ImageList(16, 16)
        self.tree_fldridx = tree_imlist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.tree_fldropenidx = tree_imlist.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        self.tree_fileidx = tree_imlist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))

        #<<< Create a CustomTreeCtrl From Tree instances

        self.tree_from = ctree.CustomTreeCtrl(pnl, agwStyle=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)

        # Add a root node to it
        root = self.tree_from.AddRoot("The Root Item")

        self.tree_from.SetImageList(tree_imlist)
        self.tree_from.SetItemImage(root, self.tree_fldridx, wx.TreeItemIcon_Normal)
        self.tree_from.SetItemImage(root, self.tree_fldropenidx, wx.TreeItemIcon_Expanded)

        # Create CustomTreeCtrl To Tree instance

        self.tree_to = ctree.CustomTreeCtrl(pnl, agwStyle=wx.TR_DEFAULT_STYLE|wx.TR_HIDE_ROOT)

        # Add a root node to it
        root = self.tree_to.AddRoot("The Root Item")

        self.tree_to.SetImageList(tree_imlist)
        self.tree_to.SetItemImage(root, self.tree_fldridx, wx.TreeItemIcon_Normal)
        self.tree_to.SetItemImage(root, self.tree_fldropenidx, wx.TreeItemIcon_Expanded)

        #>>>

        # Create a sizers to manage the layout of child widgets

        sizer_dir_dialog_from = wx.BoxSizer(wx.HORIZONTAL)
        sizer_dir_dialog_from.Add(label_title_from, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer_dir_dialog_from.Add(text_dir_from, proportion=1, flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, border=5)
        sizer_dir_dialog_from.Add(button_from, proportion=0, flag=wx.ALL, border=5)

        sizer_dir_dialog_to = wx.BoxSizer(wx.HORIZONTAL)
        sizer_dir_dialog_to.Add(label_title_to, proportion=0, flag=wx.ALL|wx.ALIGN_CENTER_VERTICAL, border=5)
        sizer_dir_dialog_to.Add(text_dir_to, proportion=1, flag=wx.LEFT|wx.TOP|wx.BOTTOM|wx.EXPAND, border=5)
        sizer_dir_dialog_to.Add(button_to, proportion=0, flag=wx.ALL, border=5)

        sizer_tree_from = wx.BoxSizer(wx.VERTICAL)
        sizer_tree_from.Add(sizer_dir_dialog_from, proportion=0, flag=wx.TOP|wx.LEFT|wx.RIGHT|wx.EXPAND, border=0)
        sizer_tree_from.Add(self.tree_from, proportion=1, flag=wx.TOP|wx.LEFT|wx.EXPAND, border=0)

        sizer_tree_to = wx.BoxSizer(wx.VERTICAL)
        sizer_tree_to.Add(sizer_dir_dialog_to, proportion=0, flag=wx.TOP|wx.LEFT|wx.EXPAND, border=0)
        sizer_tree_to.Add(self.tree_to, proportion=1, flag=wx.TOP|wx.LEFT|wx.EXPAND, border=0)

        sizer_trees = wx.BoxSizer(wx.HORIZONTAL)
        sizer_trees.Add(sizer_tree_from, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND, border=10)
        sizer_trees.Add(sizer_tree_to, proportion=1, flag=wx.RIGHT|wx.EXPAND, border=10)

        sizer_top = wx.BoxSizer(wx.HORIZONTAL)
        sizer_top.Add(label_attention, proportion=0, flag=wx.TOP|wx.LEFT|wx.ALIGN_RIGHT|wx.ALIGN_CENTER_VERTICAL, border=10)
        sizer_top.Add(self.button_run, proportion=0, flag=wx.LEFT|wx.TOP|wx.ALIGN_LEFT|wx.ALIGN_CENTER_VERTICAL, border=10)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(sizer_top, proportion=0, flag=wx.ALIGN_CENTER|wx.ALIGN_CENTER_VERTICAL, border=0)
        sizer.Add(sizer_trees, proportion=1, flag=wx.TOP|wx.EXPAND, border=5)
        sizer.Add(cb_make_links, proportion=0, flag=wx.TOP|wx.BOTTOM|wx.RIGHT|wx.ALIGN_RIGHT, border=10)

        pnl.SetSizer(sizer)

        # Create a menu bar
        self.makeMenuBar()

        # Create a status bar
        self.statusbar = self.CreateStatusBar()
        self.statusbar.SetForegroundColour(wx.BLUE)

        # Set default focus on button to open source path
        button_from.SetFocus()

        button_from.Bind(wx.EVT_BUTTON, self.OnOpen) # button click event
        button_to.Bind(wx.EVT_BUTTON, self.OnOpen) # button click event
        self.Bind(wx.EVT_CHECKBOX, self.onChecked) # checkbox event
        text_dir_from.Bind(wx.EVT_TEXT_ENTER, self.OnTextFrom)
        text_dir_to.Bind(wx.EVT_TEXT_ENTER, self.OnTextTo)
        self.button_run.Bind(wx.EVT_BUTTON, self.OnButtonRun)

        cb_make_links.SetValue(common.option_make_links)
        if bool(common.option_inspected_dir):
            text_dir_from.SetValue(common.option_inspected_dir)
            self.RepresentDir(common.option_inspected_dir, self.tree_from)
            self.PrepareProject()
        if bool(common.option_inspected_dir):
            text_dir_to.SetValue(common.option_base_dir)
        if bool(common.option_base_dir):
            text_dir_to.SetValue(common.option_base_dir)
        self.ExamStateStatus()

        self.Centre()


    def onChecked(self, e):
        cb = e.GetEventObject()
        common.option_make_links = cb.GetValue()


    def makeMenuBar(self):
        """
        A menu bar is composed of menus, which are composed of menu items.
        This method builds a set of menus and binds handlers to be called
        when the menu item is selected.
        """

        # Make a file menu with Hello and Exit items
        file_menu = wx.Menu()

        # The "\t..." syntax defines an accelerator key
        category_item = file_menu.Append(-1
                                           , _("Ca&tegory Filter...\tCtrl-T")
                                           , _("Edit category list and corresponded extensions"))
        sanity_item = file_menu.Append(-1
                                          , _("&Sanity Filter...\tCtrl-S")
                                          , _("Edit filename symbols substitution list"))
        file_menu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's label
        exit_item = file_menu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        help_menu = wx.Menu()
        help_item = help_menu.Append(-1, _("Help"), _("Show help window"))
        about_item = help_menu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(file_menu, "&File")
        menuBar.Append(help_menu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnCategory, category_item)
        self.Bind(wx.EVT_MENU, self.OnSanity, sanity_item)
        self.Bind(wx.EVT_MENU, self.OnSanity, sanity_item)
        self.Bind(wx.EVT_MENU, self.OnExit,  exit_item)
        self.Bind(wx.EVT_MENU, self.OnAbout, about_item)
        self.Bind(wx.EVT_MENU, self.OnHelp, help_item)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnAbout(self, event):
        """Display About Dialog"""
        wx.MessageBox(_("Author: Dmytro Tarasiuk") + os.linesep
                      + _("Email: RoyBebru@Gmail.Com") + os.linesep
                      + "Git: https://github.com/RoyBebru/file-grouper",
                      "🔱 File Grouper 🔱",
                      wx.OK|wx.ICON_INFORMATION)


    def OnHelp(self, event):
        """Display only single Help Window"""
        if isinstance(self.help_window, gui_help.HelpWindow):
            return
        self.help_window = gui_help.HelpWindow(self, title=_("Description Of Application"))
        self.help_window.Bind(wx.EVT_CLOSE, self.OnHelpClose)
        self.help_window.Show()


    def OnHelpClose(self, event):
        """While help is closing there must be allowed
            in the next time help would be opened"""
        self.help_window.Destroy()
        self.help_window = None


    def OnCategory(self, event):
        """Display only single Category Edit Window"""
        if isinstance(self.category_window, gui_category.CategoryWindow):
            return
        self.category_window = gui_category.CategoryWindow(self
                            , title=_("Description Of Application")
                            , style = wx.DEFAULT_FRAME_STYLE|wx.STAY_ON_TOP)
        self.category_window.Bind(wx.EVT_CLOSE, self.OnCategoryClose)
        self.category_window.Show()


    def OnCategoryClose(self, event):
        """While Category window is closing there must be allowed
            in the next time one would be opened"""
        self.category_window.Destroy()
        self.category_window = None


    def OnSanity(self, event):
        wx.MessageBox(_("Does not realized yet.")
                      , "🔱 File Grouper 🔱"
                      , wx.OK|wx.ICON_INFORMATION)


    def OnTextFrom(self, event):
        tc = event.GetEventObject()
        common.option_inspected_dir = tc.GetLineText(0)
        self.RepresentDir(common.option_inspected_dir, self.tree_from)
        self.PrepareProject()


    def OnTextTo(self, event):
        tc = event.GetEventObject()
        common.option_base_dir = tc.GetLineText(0).strip()
        self.ExamStateStatus()
        self.tree_to.SetFocus()

    def OnOpen(self, event):
        pathdir = ""

        # Ask the user what new dir to open
        with wx.DirDialog(self, _("Choose Directory"), defaultPath="..",
                           style=wx.DD_DEFAULT_STYLE | wx.DD_DIR_MUST_EXIST) as dirDialog:

            if dirDialog.ShowModal() == wx.ID_CANCEL:
                return # the user changed their mind

            # Proceed loading the dir chosen by the user
            pathdir = dirDialog.GetPath()
            try:
                button = event.GetEventObject()
                button.my_text_ctrl.SetValue(pathdir) # Will be call OnTextFrom()

                if button.my_prepare_project:
                    common.option_inspected_dir = pathdir
                    self.RepresentDir(pathdir, self.tree_from)
                    self.PrepareProject()
                else:
                    common.option_base_dir = pathdir

                self.ExamStateStatus()
            except IOError:
                wx.LogError("Cannot open dir '%s'." % pathdir)


    def RepresentDir(self, pathdir: str, tree):
        folder = Path(pathdir)
        if not folder.exists() or not folder.is_dir:
            wx.MessageBox(_("Folder") + os.linesep
                        + f"'{pathdir}'" + os.linesep
                        + _("is not valid. Try again."),
                        "🔱 File Grouper 🔱",
                        wx.OK|wx.ICON_INFORMATION)
            return

        dirs = core.get_reverse_sorted_path_dirs(pathdir, alldirs=True)
        root = tree.GetRootItem()

        tree.DeleteChildren(root) # clear tree

        if len(dirs) == 0:
            return

        nodes = {}
        nodes[dirs[-1]] = root
        while len(dirs) > 0:
            dir = dirs[-1]
            dirs = dirs[:-1]
            node = nodes[dir]
            for i in range(len(dirs)-1, -1, -1):
                if dirs[i].parent == dir:
                    child = tree.AppendItem(node, dirs[i].name)
                    tree.SetItemImage(child, self.tree_fldridx, wx.TreeItemIcon_Normal)
                    tree.SetItemImage(child, self.tree_fldropenidx, wx.TreeItemIcon_Expanded)
                    child.SetBold(True)
                    child.Expand()
                    nodes[dirs[i]] = child
            for file in dir.iterdir():
                if file.is_file():
                    child = tree.AppendItem(node, file.name)
                    tree.SetItemImage(child, self.tree_fileidx, wx.TreeItemIcon_Normal)
                    child.SetBold(True)


    def PrepareProject(self):
        project_tree = {}

        def resolve_existent_filename_collision(category, name, ext):
            """Add version for the file with the same name"""
            if (name + ext) not in project_tree[category]:
                return name + ext
            ver = 1
            while (name + "_{:03d}".format(ver) + ext) in project_tree[category]:
                ver += 1
            return name + "_{:03d}".format(ver) + ext


        def TreeNodeRunner(node):
            """Recursive Tree Runner"""
            cookie = 0
            while True:
                (item, cookie) = self.tree_from.GetNextChild(node, cookie)
                if not bool(item):
                    break
                if self.tree_from.ItemHasChildren(item):
                    # Folder
                    TreeNodeRunner(item)
                else:
                    # File
                    (category, name, ext) = core.find_category(item.GetText())
                    if not bool(category):
                        # Category is absent for this file extension
                        continue
                    # Sanity filename
                    name = name.translate(common.filename_translation_table)
                    if category in project_tree:
                        project_tree[category].append(resolve_existent_filename_collision(category, name, ext))
                    else:
                        project_tree[category] = [name + ext]

        TreeNodeRunner(self.tree_from.GetRootItem())

        # Preparing Tree_To Project
        root = self.tree_to.GetRootItem()
        self.tree_to.DeleteChildren(root) # clear tree
        for (category, file_list) in project_tree.items():
            child = self.tree_to.AppendItem(root, category)
            self.tree_to.SetItemImage(child, self.tree_fldridx, wx.TreeItemIcon_Normal)
            self.tree_to.SetItemImage(child, self.tree_fldropenidx, wx.TreeItemIcon_Expanded)
            child.SetItalic(True)
            child.Expand()
            file_list.sort()
            for file in file_list:
                item = self.tree_from.AppendItem(child, file)
                self.tree_to.SetItemImage(item, self.tree_fileidx, wx.TreeItemIcon_Normal)
                item.SetItalic(True)


    def ExamStateStatus(self):
        if (bool(common.option_base_dir)
                and bool(common.option_inspected_dir)
                and core.AreDirsAdequate()):
            self.button_run.Enable(True)
        else:
            self.button_run.Enable(False)

        if not bool(common.option_inspected_dir):
            self.statusbar.SetStatusText(_("Select folder to inspect"))
            return
        if not bool(common.option_base_dir):
            self.statusbar.SetStatusText(_("You see only expectation result: select folder to put it"))
            return
        if core.AreDirsAdequate():
            self.statusbar.SetStatusText(_("Press Run button to realize your project in life"))
        else:
            self.statusbar.SetStatusText(_("Selected folders are not suitable to work"))


    def OnButtonRun(self, event):
        if not core.AreDirsAdequate:
            self.ExamStateStatus()
            return

        core.do_everything()

        # Show the result
        self.RepresentDir(common.option_base_dir, self.tree_to)
        if not common.option_make_links:
            # Inspectred folder must be deleted: clear tree_from
            self.tree_from.DeleteChildren(self.tree_from.GetRootItem()) # from tree


def run_gui():
    app = wx.App()
    frame = FileGrouperWindow(None, title="FIG")
    frame.Show()
    app.MainLoop()
