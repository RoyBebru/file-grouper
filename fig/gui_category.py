# -*- coding: utf-8 -*-

import fig.common as common
_ = common._ # for i18n

import wx
import wx.lib.agw.customtreectrl as ctree
import os

class CategoryWindow(wx.Frame):

    def __init__(self, *args, **kw):
        # Ensure the parent's __init__ is called
        super(CategoryWindow, self).__init__(*args, **kw, size=(800, 600))

        self.categories = common.categories.copy()

        # Disable resizing main window to be too small and
        # prevent GTK annoing messages like the folowing:
        # (fig:131363): Gtk-CRITICAL **: 17:30:08.178: gtk_box_gadget_distribute:
        # assertion 'size >= 0' failed in GtkScrollbar
        self.SetSizeHints(400,300,-1,-1)

        # Create a panel in the frame
        pnl = wx.Panel(self)

        # Put attention text with a larger bold font on it
        label_title = wx.StaticText(pnl, label="File Categories", style=wx.ALIGN_CENTER)
        font = label_title.GetFont()
        font.PointSize += 6
        font = font.Bold()
        label_title.SetFont(font)

        #<<< Create Editable Tree

        # Create image list common for both trees to add icons next to tree items
        tree_imlist = wx.ImageList(16, 16)
        self.tree_fldridx = tree_imlist.Add(wx.ArtProvider.GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, (16, 16)))
        self.tree_fldropenidx = tree_imlist.Add(wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_OTHER, (16, 16)))
        self.tree_fileidx = tree_imlist.Add(wx.ArtProvider.GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, (16, 16)))

        # Create a CustomTreeCtrl Tree instance

        self.tree_inst = ctree.CustomTreeCtrl(pnl, agwStyle=wx.TR_DEFAULT_STYLE
                |wx.TR_EDIT_LABELS|wx.TR_ROW_LINES|wx.TR_HIDE_ROOT)

        # Add a root node to it
        self.tree_root = self.tree_inst.AddRoot("Category")
        self.tree_root.my_type = 0 # root
        # self.tree_root.SetBold(True)
        self.tree_inst.EnableItem(self.tree_root, enable=False, torefresh=True)

        self.tree_inst.SetImageList(tree_imlist)
        self.tree_inst.SetItemImage(self.tree_root, self.tree_fldridx, wx.TreeItemIcon_Normal)
        self.tree_inst.SetItemImage(self.tree_root, self.tree_fldropenidx, wx.TreeItemIcon_Expanded)

        self.FillTreeUp()
        #>>>

        self.button_apply = wx.Button(pnl, label=_("Apply Changes"))
        self.button_apply.Enable(False)

        button_insert = wx.Button(pnl, label=_("Insert"))
        button_delete = wx.Button(pnl, label=_("Delete"))

        # Create a sizers to manage the layout of child widgets

        sizer_upper = wx.BoxSizer(wx.HORIZONTAL)
        sizer_upper.Add(button_insert, proportion=0, flag=wx.LEFT|wx.RIGHT|wx.TOP
                |wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_LEFT, border=5)
        sizer_upper.Add(label_title, proportion=1, flag=wx.ALL
                |wx.ALIGN_CENTER_HORIZONTAL|wx.ALIGN_CENTER_VERTICAL|wx.EXPAND, border=5)
        sizer_upper.Add(button_delete, proportion=0, flag=wx.LEFT|wx.RIGHT|wx.TOP
                |wx.ALIGN_CENTER_VERTICAL|wx.ALIGN_RIGHT, border=5)

        sizer_wrapper = wx.BoxSizer(wx.VERTICAL)
        sizer_wrapper.Add(sizer_upper, proportion=0, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM|wx.EXPAND, border=0)
        sizer_wrapper.Add(self.tree_inst, proportion=1, flag=wx.ALL|wx.EXPAND, border=5)
        sizer_wrapper.Add(self.button_apply, proportion=0, flag=wx.ALL|wx.EXPAND, border=5)

        pnl.SetSizer(sizer_wrapper)

        self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.OnItemActivated)
        # self.Bind(wx.EVT_TREE_BEGIN_LABEL_EDIT, self.OnItemBeginEdit)
        self.Bind(wx.EVT_TREE_END_LABEL_EDIT, self.OnItemEndEdit)
        # self.Bind(wx.EVT_TREE_SEL_CHANGED, self.OnSelChanged)
        self.button_apply.Bind(wx.EVT_BUTTON, self.OnButtonApply)
        button_insert.Bind(wx.EVT_BUTTON, self.OnButtonInsert)
        button_delete.Bind(wx.EVT_BUTTON, self.OnButtonDelete)
        self.Centre()


    def FillTreeUp(self):
        self.tree_inst.DeleteChildren(self.tree_inst.GetRootItem())
        for (category, exts) in self.categories.items():
            child = self.tree_inst.AppendItem(self.tree_root, category)
            self.tree_inst.SetItemImage(child, self.tree_fldridx, wx.TreeItemIcon_Normal)
            self.tree_inst.SetItemImage(child, self.tree_fldropenidx, wx.TreeItemIcon_Expanded)
            child.SetBold(True)
            # child.SetItalic(True) # cannot SetBold() & SetItalic() be call simultaneously
            item = self.tree_inst.AppendItem(child,  ' '.join(exts))
            self.tree_inst.SetItemImage(item, self.tree_fileidx, wx.TreeItemIcon_Normal)
            child.Expand()
            child.my_type = 1 # category
            item.my_type = 2 # item


    def OnButtonApply(self, event):
        root = self.tree_inst.GetRootItem()
        common.categories.clear()
        cookie = 0
        while True:
            (item, cookie) = self.tree_inst.GetNextChild(root, cookie)
            if not bool(item):
                break
            category = item.GetText()
            c = 0
            (ext_item, c) = self.tree_inst.GetNextChild(item, c)
            ext_list = common.ConvertExtsStringToSortedList(ext_item.GetText())
            common.categories[category] = ext_list
        self.Close()


    def OnButtonInsert(self, event):
        item = self.tree_inst.GetSelection()
        if isinstance(item, ctree.GenericTreeItem):
            if item.my_type == 0:
                wx.MessageBox(_("Select any category to insert after")
                              , "🔱 File Grouper 🔱"
                              , wx.OK|wx.ICON_INFORMATION)
                return
            elif item.my_type == 2:
                item = self.tree_inst.GetItemParent(item)
            base_item = self.tree_inst.InsertItemByItem(self.tree_inst.GetRootItem(), item, "<Please Edit>")
            base_item.my_type = 1
            self.tree_inst.SetItemImage(base_item, self.tree_fldridx, wx.TreeItemIcon_Normal)
            self.tree_inst.SetItemImage(base_item, self.tree_fldropenidx, wx.TreeItemIcon_Expanded)
            sub_item = self.tree_inst.InsertItemByItem(base_item, None, "<Please edit>")
            sub_item.my_type = 2
            self.tree_inst.SetItemImage(sub_item, self.tree_fileidx, wx.TreeItemIcon_Normal)
            base_item.Expand()
            self.tree_inst.SelectItem(base_item)
            self.tree_inst.EditLabel(base_item)
            self.button_apply.Enable(True)


    def OnButtonDelete(self, event):
        item = self.tree_inst.GetSelection()
        if isinstance(item, ctree.GenericTreeItem):
            cat_amount = self.tree_inst.GetChildrenCount(self.tree_inst.GetRootItem(), recursively=False)
            if cat_amount == 1 or item.my_type == 0:
                # Do not delete the last category or root
                return
            if item.my_type == 2:
                item = self.tree_inst.GetItemParent(item)
            self.tree_inst.Delete(item)
            self.button_apply.Enable(True)


    def OnItemActivated(self, event):
        tree_inst = event.GetEventObject()
        item = tree_inst.GetSelection()
        tree_inst.EditLabel(item)


    # def OnItemBeginEdit(self, event):
    #     tree_inst = event.GetEventObject()
    #     item = tree_inst.GetSelection()
    #     if item.my_type == 0:
    #         print("root cannot be edited")
    #         return
    #     return True


    # def OnSelChanged(self, event):
    #     tree_inst = event.GetEventObject()
    #     item = tree_inst.GetSelection()
    #     print(f"Sel{item}")


    def OnItemEndEdit(self, event):
        tree_inst = event.GetEventObject()
        item = tree_inst.GetSelection()
        new_text = event.GetLabel().strip() # it is not described in documents
        if item.my_type == 0:
            # Root cannot be changed
            return
        old_text = item.GetText()
        if old_text == new_text:
            # Nothing is changed
            return
        if item.my_type == 1:
            # Changed category folder name
            # self.categories[new_text] = self.categories[old_text]
            # self.categories.pop(old_text, None)
            self.button_apply.Enable(True)
            return
        if item.my_type == 2:
            # Changed extension list
            # self.categories[tree_inst.GetItemParent(item).GetText()] \
            #     = common.ConvertExtsStringToSortedList(new_text)
            self.button_apply.Enable(True)
            return
