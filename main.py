import tkinter as tk
import tkinter.ttk as ttk
import tkinter.tix as tix
from tkinter.filedialog import askdirectory, askopenfilename, asksaveasfilename, askopenfilenames
from PIL import Image, ImageTk
import os
import json
import pickle


# ZOOP_PATH = os.getcwd()
ZOOP_PATH = os.getcwd() + '\\converted\\'
VERSION = "VAlpha"

with open('res/supported.json', 'r') as supported_files:
    SUPPORTED_FILES_EXT = json.load(supported_files)


class MenuBar(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.theme_opt_var = tk.StringVar()

        self.file_menu = ttk.Menubutton(self, text='File')
        self.file_menu.pack(side=tk.LEFT)

        menu = tk.Menu(self.file_menu, tearoff=False, bg='white', bd=0, fg='black',
                        activebackground='gray',
                        relief=tk.FLAT)

        menu.add_command(label='📂 Add image(s) to convert', command=self.parent.callOpenImg, accelerator='Ctrl+A')
        menu.add_command(label='✂ Delete selected image(s)', accelerator='Ctrl+D', command=self.parent.callRemoveImage)
        menu.add_command(label='🗑 Clear image list', accelerator='Ctrl+Alt+D', command=self.parent.callRemoveAll)
        menu.add_separator()
        menu.add_command(label='Exit', command=self.parent.destroy, accelerator='Esc')
        self.file_menu.config(menu=menu)

        self.view_menu = ttk.Menubutton(self, text='View')
        self.view_menu.pack(side=tk.LEFT)

        menu = tk.Menu(self.view_menu, tearoff=False, bg='white', bd=0, fg='black',
                        activebackground='gray',
                        relief=tk.FLAT)

        sub_menu = tk.Menu(menu, tearoff=False, bg='white', bd=0, fg='black',
                        activebackground='gray',
                        relief=tk.FLAT)

        self.style = ttk.Style()
        for theme in self.style.theme_names():
            sub_menu.add_radiobutton(label=theme, value=theme, variable=self.theme_opt_var, command=self.switch_theme)

        menu.add_cascade(label='🎨 Application Theme', menu=sub_menu)
        self.view_menu.config(menu=menu)

        self.theme_opt_var.set(self.parent.data['theme'])

        self.convert_menu = ttk.Menubutton(self, text='Convert')
        self.convert_menu.pack(side=tk.LEFT)

        menu = tk.Menu(self.convert_menu, tearoff=False, bg='white', bd=0, fg='black',
                        activebackground='gray',
                        relief=tk.FLAT)
        
        menu.add_command(label='✔ Convert All', accelerator='Ctrl+O', command=self.parent.callConvertAll)
        menu.add_command(label='📌Convert Selected', accelerator='Ctrl+L', command=self.parent.callConvertSelected)

        self.convert_menu.config(menu=menu)

        self.credits_menu = ttk.Button(self, text='Credits', command=self.openCredits)
        self.credits_menu.pack(side=tk.LEFT)

        self.pack(fill=tk.X)

    def openCredits(self):
        credits_toplevel = tix.Toplevel(self.parent)
        credits_toplevel.iconbitmap('zoop.ico')
        credits_toplevel.geometry('500x300')

        main_frame = ttk.Frame(credits_toplevel)
        main_frame.pack(fill=tk.BOTH, expand=tk.YES)

        title_label = ttk.Label(main_frame, text='Zoop Image Converter [{}]'.format(VERSION), font='Calibri 18 bold')
        title_label.pack(anchor='nw', padx=12, pady=12)

        text = """
Zoop Image Converter 2021 (c) - MOIGNOUX Valentin, All rights reserved

This software is provided by a pythonista...
And it's open-source...

Check out the source code on github :
https://www.github.com/MartinGate/Zoop
        """

        credits_label = ttk.Label(main_frame, text=text)
        credits_label.pack(anchor='nw', padx=12)

    def switch_theme(self):
        self.parent.theme.theme_use(self.theme_opt_var.get())
        with open('preferences.zoopdat', 'wb') as rec:
            pickle.dump({'theme': self.theme_opt_var.get()}, rec)

        self.parent.optionsFrame.logview.logviewcanvas.config(bg=self.style.lookup('TFrame', 'background'),
                                                                highlightbackground=self.style.lookup('TFrame', 'background'))
        self.parent.optionsFrame.logview.logviewstatelabel.config(bg=self.style.lookup('TFrame', 'background'))


class ZoopTooltip(tix.Balloon):
    def __init__(self, parent, color='white'):
        tix.Balloon.__init__(self, parent)
        self.parent = parent

        self.config(bg='light grey')
        self.label.config(fg=color)
        for i in self.subwidgets_all():
            i.config(bg=color)

    def assignTooltip(self, obj, msg):
        self.bind_widget(obj, balloonmsg=msg)


class ZoopFrame(ttk.Frame):
    def __init__(self, parent,
                    default_text='No data to display yet',
                    default_image='res/Icons/add.png',
                    default_cursor='hand2',
                    default_cmd=None,
                    default_tooltip=None):

        ttk.Frame.__init__(self, parent, relief=tk.FLAT)
        self.parent = parent
        self.default_text = default_text
        self.default_image = default_image
        self.default_cursor = default_cursor
        self.default_cmd = default_cmd
        self.default_tooltip = default_tooltip
        self.default_deleted = False
        self.treeview_id_count = 0

        self.tooltip = ZoopTooltip(self)

        img_temp = Image.open(self.default_image)
        img_temp = img_temp.resize((90, 90), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img_temp)

        self.__instanciateDefault()
        self.__doBindings()
        self.__packDefault()

        self.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)

    def __instanciateDefault(self):
        self.default_frame = ttk.Frame(self)

        self.default_image = ttk.Label(self.default_frame, image=self.img, cursor=self.default_cursor)
        self.default_image.image = self.img

        self.default_label = ttk.Label(self.default_frame, text=self.default_text, cursor=self.default_cursor, justify='center')

        if self.default_tooltip is not None:
            self.tooltip.assignTooltip(self.default_image, self.default_tooltip)
            self.tooltip.assignTooltip(self.default_label, self.default_tooltip)

    def __instanciateTreeView(self):
        self.tree_frame = ttk.Frame(self)

        self.treeview = ttk.Treeview(self.tree_frame)

        # Define our columns
        self.treeview['columns'] = ('File', 'File Type')
        self.treeview.column('#0', width=0, stretch=tk.NO)
        self.treeview.column('File', width=80, minwidth=50, anchor=tk.W)
        self.treeview.column('File Type', width=100, minwidth=90, anchor=tk.CENTER)

        self.treeview.heading('#0', text='')
        self.treeview.heading('File', text='File')
        self.treeview.heading('File Type', text='File Type')

        self.tree_scrollbar = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=self.tree_scrollbar.set)

    def __packTreeView(self):
        self.treeview.pack(expand=tk.YES, fill=tk.BOTH, side=tk.LEFT)
        self.tree_scrollbar.pack(fill=tk.Y, expand=tk.NO, side=tk.RIGHT)

        self.tree_frame.pack(fill=tk.BOTH, expand=tk.YES)

    def __packDefault(self):
        self.default_image.pack(expand=tk.YES, pady=18)
        self.default_label.pack(expand=tk.YES)
        self.default_frame.pack(expand=tk.YES)

        self.default_deleted = False
    
    def delete_default(self):
        self.default_frame.destroy()
        self.__instanciateDefault()

        self.default_deleted = True

    def delete_treeview(self):
        self.treeview.destroy()
        self.tree_scrollbar.destroy()
        self.tree_frame.destroy()
        self.__instanciateTreeView()

        self.default_deleted = False

    def ask_default(self, doBindings=True):
        self.__packDefault()
        if doBindings:
            self.__doBindings()

    def askTreeView(self):
        self.delete_default()
        self.__instanciateTreeView()
        self.__packTreeView()

    def remove_selected(self):
        try:
            selected_items = self.treeview.selection()        
            for selected_item in selected_items:          
                self.treeview.delete(selected_item)

            if not self.treeview.get_children():
                self.delete_treeview()
                self.ask_default()

        except AttributeError:
            pass

        return selected_items

    def clear_all(self):
        try:
            self.parent.master.msgbox.destroy()
            self.treeview.delete(*self.treeview.get_children())
            self.delete_treeview()
            self.ask_default()
        except AttributeError:
            pass

    def __doBindings(self):
        for sub in self.default_frame.winfo_children():
            sub.bind('<Button-1>', self.default_cmd)


class InputFrame(ZoopFrame):
    def __init__(self, parent):
        ZoopFrame.__init__(self, parent, default_text='Click here to add images', default_cmd=self.openImageFiles, default_tooltip="Click here to add image(s) to convert")
        self.parent = parent
        self.has_input = False
        self.paths_list = []
        self.not_concerned_paths = []

    def openImageFiles(self, evt):
        def addImageToPathsList(list_to_add, arg):
            list_to_add.append(arg)
            self.paths_list.append(arg)

            try:
                self.remove_mbbox()
            except AttributeError:
                pass

        try:
            filenames = askopenfilenames(title = "Select file(s)")
            
            if not filenames:
                print('No selected files...')
            else:
                temp_list = []
                for i in filenames:
                    if os.path.splitext(i)[1] in SUPPORTED_FILES_EXT:
                        if i in self.paths_list:
                            msg = "{} already exists,\nDo you want to replace it ?".format(os.path.basename(i))
                            self.mbbox = ZoopMessageBox(self, title='Zoop Alert !', msg=msg, buttons_cmds=[lambda arg=temp_list, arg2=i: addImageToPathsList(arg, i), self.remove_mbbox, self.remove_mbbox])

                        else:
                            addImageToPathsList(temp_list, i)

                if temp_list == []:
                    print("Non supported file(s) selected")
                else:

                    if self.default_deleted == False:
                        self.askTreeView()
                    
                    count = self.treeview_id_count
                    for i in temp_list:
                        filename, file_type = os.path.basename(i), os.path.splitext(i)[1]
                        self.treeview.insert(parent='', iid=count, index='end', values=(filename, file_type))
                        count += 1
                    
                    self.treeview_id_count = count

        except OSError:
            print("ERROR : An error has occured opening file(s).")

    def Convert(self, mode='all'):
        to_convert = self.getToConvert(mode)
        success = 0
        aborted = 0
        try:

            for img in to_convert:
                try:
                    saved_image = Image.open(img)

                    img_filename = '/' + os.path.basename(img).split('.')[0]
                    save_ext = self.parent.master.optionsFrame.outputFileFormat.get()
                    save_dir = self.parent.master.optionsFrame.outputDir.get()

                    save_path = os.path.join(save_dir + img_filename + save_ext)
                    
                    try:
                        self.parent.master.optionsFrame.logview.log(color='green', msg="INFO : Converting " + img + " to " + save_ext +  " ...")
                        saved_image.save(save_path)
                        success += 1
                    except:
                        self.parent.master.optionsFrame.logview.log(color='red', msg="ERROR : Failed to convert " + img + " to " + save_ext)
                        aborted += 1

                except:
                    pass

        except AttributeError as e:
            pass

        self.parent.master.optionsFrame.logview.logview_state.set('No conversion started')

        if success or aborted != 0:
            msg = """
Conversion report :
{} file(s) converted successfully.
{} file(s) aborted.
            """.format(success, aborted)

            self.mbbox = ZoopMessageBox(self, title="Conversion report", msg=msg, buttons=['Ok'], buttons_cmds=[self.remove_mbbox], image='res/Icons/info.png')

    def remove_mbbox(self):
        self.mbbox.destroy()

    def getToConvert(self, mode):
        to_convert = self.paths_list[:]

        for i in range(len(self.paths_list)):
            for n in self.not_concerned_paths:
                if i == int(n):
                    print('Deleted file :', self.paths_list[int(n)])
                    to_convert.pop(i)

        if mode == 'selected':
            temp = []
            for i in range(len(to_convert)):
                for n in self.treeview.selection():
                    if i == int(n):
                        temp.append(to_convert[i])

            to_convert = temp

        return to_convert


class ZoopLogView(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent
        self.logs_list = []
        self.log_x = 5
        self.log_y = 12
        self.scroll_region_x = 0
        self.scroll_region_y = 30
        self.logview_state = tk.StringVar()
        self.logview_state.set('No conversion started')

        logview_bg = ttk.Style().lookup('TFrame', 'background')

        self.logviewframe = ttk.Frame(self)
        self.logviewcanvas = tk.Canvas(self.logviewframe, scrollregion=(0, 0, self.scroll_region_x, self.scroll_region_y), bg=logview_bg, highlightbackground=logview_bg)
        self.logviewcanvas.pack(fill=tk.BOTH, expand=tk.YES, side=tk.LEFT)

        self.logview_scrollbar = ttk.Scrollbar(self.logviewframe)
        self.logviewcanvas.bind('<Enter>', self._bound_to_mousewheel)
        self.logviewcanvas.bind('<Leave>', self._unbound_to_mousewheel)
        self.logview_scrollbar.config(command=self.logviewcanvas.yview)
        self.logviewcanvas.config(yscrollcommand=self.logview_scrollbar.set)

        self.logview_scrollbar2 = ttk.Scrollbar(self, orient='horizontal')
        self.logview_scrollbar2.config(command=self.logviewcanvas.xview)
        self.logviewcanvas.config(xscrollcommand=self.logview_scrollbar2.set)

        self.logview_scrollbar.pack(side=tk.LEFT, fill=tk.Y)
        self.logviewframe.pack(expand=tk.YES, fill=tk.BOTH)

        self.infos_frame = ttk.Frame(self)
        self.logviewlabel = ttk.Label(self.infos_frame, text='💬 Log View')
        self.logviewlabel.pack(side=tk.RIGHT, padx=5)

        self.logviewstatelabel = tk.Label(self.infos_frame, bg=logview_bg, fg='red', textvariable=self.logview_state)
        self.logviewstatelabel.pack(side=tk.LEFT, padx=5)
        
        self.infos_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.logview_scrollbar2.pack(side=tk.BOTTOM, fill=tk.X)

        self.log(color='cyan', msg="Zoop Image Converter (c) 2021 [Vbeta 0.1] \nMOIGNOUX Valentin - All rights reserved")
    
    def _bound_to_mousewheel(self, event):
        self.logviewcanvas.bind_all("<MouseWheel>", self._on_mousewheel)

    def _unbound_to_mousewheel(self, event):
        self.logviewcanvas.unbind_all("<MouseWheel>")

    def _on_mousewheel(self, event):
        self.logviewcanvas.yview("scroll",int(-1*(event.delta/120)),"units")

    def log(self, header='', msg='', color='black', infos=None):
        self.logs_list.append([msg, color, infos])

        text = self.logviewcanvas.create_text(self.log_x, self.log_y, text=header + msg, fill=color, justify='left', anchor='w')

        bounds = self.logviewcanvas.bbox(text)
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]

        self.log_y += height + 2
        self.scroll_region_y += height + 2

        if width > self.scroll_region_x:
            self.scroll_region_x = width

        self.logviewcanvas.config(scrollregion=(0,0,self.scroll_region_x + self.log_x, self.scroll_region_y))
        self.logviewcanvas.yview("moveto", 10)


class ConversionOptionsFrame(ttk.LabelFrame):
    def __init__(self, parent):
        ttk.LabelFrame.__init__(self, parent, text='🛠 Convertion options')
        self.parent = parent
        self.outputFileFormat = tk.StringVar()
        self.outputDir = tk.StringVar()

        self.pack(side=tk.RIGHT, fill=tk.BOTH, expand=tk.NO)

        self.outputFileFormatFrame = ttk.Frame(self)
        self.outputLabel = ttk.Label(self.outputFileFormatFrame, text='Output Format :')
        self.outputCombo = ttk.Combobox(self.outputFileFormatFrame, values=SUPPORTED_FILES_EXT, textvariable=self.outputFileFormat)
        self.outputFileFormat.set('.jpg')
        self.outputCombo.current(0)
        
        self.outputLabel.pack(side=tk.LEFT, padx=8)
        self.outputCombo.pack(side=tk.RIGHT, padx=5)
        self.outputFileFormatFrame.pack(side=tk.TOP, fill=tk.X, pady=15)

        self.outputDirFrame = ttk.Frame(self)
        self.outputDirLabel = ttk.Label(self.outputDirFrame, text='Output Directory :')

        self.outputDirEntryFrame = ttk.Frame(self.outputDirFrame)
        self.outputDirEntry = ttk.Entry(self.outputDirEntryFrame, textvariable=self.outputDir)
        self.outputDirButton = ttk.Button(self.outputDirEntryFrame, text='..', width=1, command=self.setOutputDir)

        self.outputDir.set(ZOOP_PATH)

        self.outputDirLabel.pack(side=tk.LEFT, padx=8)
        self.outputDirButton.pack(side=tk.RIGHT)
        self.outputDirEntry.pack(side=tk.RIGHT)
        self.outputDirEntryFrame.pack(side=tk.RIGHT, padx=5)
        self.outputDirFrame.pack(side=tk.TOP, fill=tk.X)

        self.logview = ZoopLogView(self)
        self.logview.pack(fill=tk.BOTH, expand=tk.YES, padx=10, pady=(20, 5))

    def setOutputDir(self):
        directory = askdirectory(title='Select conversion output directory')
        if directory != '':
            self.outputDir.set(directory)


class ZoopMessageBox(tix.Toplevel):
    def __init__(self, parent, title='Zoop Says...', msg='Nothing to say', buttons=["Yes", "No", "Cancel"], buttons_cmds=[None, None, None], image='res/Icons/alert.png'):
        tix.Toplevel.__init__(self, parent)
        self.geometry('370x170')
        self.title(title)
        self.attributes('-topmost', True)

        windowWidth = self.winfo_reqwidth()
        windowHeight = self.winfo_reqheight()
        
        positionRight = int(self.winfo_screenwidth()/2 - windowWidth/2)
        positionDown = int(self.winfo_screenheight()/2 - windowHeight/2)
        
        self.geometry("+{}+{}".format(positionRight, positionDown))
        self.overrideredirect(True)

        img_temp = Image.open(image)
        img_temp = img_temp.resize((90, 90), Image.ANTIALIAS)
        self.img = ImageTk.PhotoImage(img_temp)

        main_frame = tk.Frame(self, highlightbackground="red",
                            highlightcolor="red",
                            highlightthickness=1)

        main_frame.pack(fill=tk.BOTH, expand=tk.YES)

        self.msg = ttk.Frame(main_frame)

        self.msgImg = ttk.Label(self.msg, image=self.img)
        self.msgImg.image = self.img
        self.msgImg.pack(expand=tk.NO, side=tk.LEFT, padx=21)

        self.msgLabel = ttk.Label(self.msg, text=msg, font='Calibri 11 bold')
        self.msgLabel.pack(side=tk.LEFT)

        self.msg.pack(fill=tk.BOTH, expand=tk.YES)

        self.buttons_frame = ttk.Frame(main_frame)

        self.buttons_list = {}
        count = len(buttons) - 1
        for i in range(len(buttons)):
            self.buttons_list[count] = ttk.Button(self.buttons_frame, text=buttons[count], command=buttons_cmds[count])
            self.buttons_list[count].pack(side=tk.RIGHT, padx=12, pady=12)
            count -= 1

        self.buttons_frame.pack(side=tk.BOTTOM, fill=tk.X)


class ToolBar(ttk.Frame):
    def __init__(self, parent):
        ttk.Frame.__init__(self, parent)
        self.parent = parent

        self.tooltip = ZoopTooltip(self)

        self.add_files = ttk.Button(self, text='➕', command=self.parent.callOpenImg, width=3)
        self.tooltip.assignTooltip(self.add_files, msg="Add image(s)")
        self.add_files.pack(side=tk.LEFT, pady=10, padx=5, expand=tk.NO)

        self.remove_files = ttk.Button(self, text='➖', command=self.parent.callRemoveImage, width=3)
        self.tooltip.assignTooltip(self.remove_files, msg="Remove image(s)")
        self.remove_files.pack(side=tk.LEFT, pady=10, padx=5, expand=tk.NO)

        self.clear_files = ttk.Button(self, text='🗑', command=self.parent.callRemoveAll, width=3)
        self.tooltip.assignTooltip(self.clear_files, msg="Remove all images from the list")
        self.clear_files.pack(side=tk.LEFT, pady=10, padx=5, expand=tk.NO)

        self.convert_selected_btn = ttk.Button(self, text='Convert selected', command=self.parent.callConvertSelected)
        self.tooltip.assignTooltip(self.convert_selected_btn, msg="Click here to convert all the selected images from the list.")
        self.convert_selected_btn.pack(side=tk.LEFT, pady=10, padx=5)

        self.convert_all = ttk.Button(self, text='Convert All ✔', command=self.parent.callConvertAll)
        self.tooltip.assignTooltip(self.convert_all, msg="Click here to convert all the images from the list.")
        self.convert_all.pack(side=tk.LEFT, pady=10, padx=5)

        self.status_label = ttk.Label(self, text='❗ Zoop V0.1')
        self.status_label.pack(side=tk.RIGHT, pady=10, padx=15)

        self.pack(fill=tk.X, side=tk.BOTTOM)


class Window(tix.Tk):
    def __init__(self):
        tix.Tk.__init__(self)
        self.title('Zoop Image Converter - [{}]'.format(str(VERSION)))
        self.geometry('800x560')
        self.iconbitmap('zoop.ico')
        self.minsize(width=300, height=300)
        self.config(cursor='@res/Cursors/cursor.cur')
        
        self.theme = ttk.Style(self)

        self.tk.eval("""
            set base_theme_dir themes/

            package ifneeded awthemes 10.3.0 \
                [list source [file join $base_theme_dir awthemes-10.3.0/awthemes.tcl]]
            package ifneeded colorutils 4.8 \
                [list source [file join $base_theme_dir awthemes-10.3.0/colorutils.tcl]]
            package ifneeded awdark 7.11 \
                [list source [file join $base_theme_dir awthemes-10.3.0/awdark.tcl]]
            package ifneeded awlight 7.9 \
                [list source [file join $base_theme_dir awthemes-10.3.0/awlight.tcl]]
        """)

        self.tk.call("package", "require", 'awdark')
        self.tk.call("package", "require", 'awlight')
        
        self.bind('<Escape>', self.quit)
        self.set_saved_theme()
        self.__setupMenu()
        self.__setupUI()

        self.__doShorcutsBindings()

    def set_saved_theme(self):
        try:
            with open('preferences.zoopdat', 'rb') as rec:
                self.data = pickle.load(rec)

        except:
            self.data = {'theme': 'awdark'}

        self.theme.theme_use(self.data['theme'])

    def __setupMenu(self):
        self.mb = MenuBar(self)

    def __setupUI(self):
        frame = ttk.Frame(self)
        self.inputFrame = InputFrame(frame)
        self.optionsFrame = ConversionOptionsFrame(frame)

        frame.pack(fill=tk.BOTH, expand=tk.YES)

        self.toolbar = ToolBar(self)

    def __doShorcutsBindings(self):
        self.bind('<Control-a>', self.inputFrame.openImageFiles)
        self.bind('<Control-d>', self.callRemoveImage)
        self.bind('<Control-Alt-d>', self.callRemoveAll)
        self.bind('<Control-o>', self.callConvertAll)
        self.bind('<Control-l>', self.callConvertSelected)

    def callOpenImg(self, evt=None):
        self.inputFrame.openImageFiles(None)

    def showConvertingState(self):
        self.optionsFrame.logview.logview_state.set('Converting...')
        self.optionsFrame.logview.logviewstatelabel.update()

    def callConvertSelected(self, evt=None):
        self.showConvertingState()
        self.inputFrame.Convert(mode='selected')

    def callConvertAll(self, evt=None):
        self.showConvertingState()
        self.inputFrame.Convert(mode='all')
    
    def callRemoveImage(self, evt=None):
        try:
            to_remove = self.inputFrame.remove_selected()

            for i in to_remove:
                self.inputFrame.not_concerned_paths.append(i)
        except UnboundLocalError:
            pass

    def callRemoveAll(self, evt=None):
        if self.inputFrame.default_deleted:
            self.msgbox = ZoopMessageBox(self, msg="Are you sure you want to \ncompletely delete the \nimages of the list ?", buttons_cmds=[self.callClearAll, self.destroy_msg, self.destroy_msg])
        
    def callClearAll(self, evt=None):
        self.inputFrame.clear_all()
        self.inputFrame.paths_list = []
        self.inputFrame.not_concerned_paths = []

    def destroy_msg(self):
        self.msgbox.destroy()

    def quit(self, evt):
        self.destroy()


if __name__ in '__main__':
    Window().mainloop()