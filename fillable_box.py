try:
    from . import utils as ut
    from . import global_state

except (ValueError, ImportError):
    import utils as ut
    import global_state

from tkinter import ttk
import tkinter as tk  # python 3
import tkinter.font as tk_Font


boxRoot = None
entryWidget = None
__enterboxText = ''
__enterboxDefaultText = ''
cancelButton = None
nButton = None
okButton = None


def __fillablebox(msg, title="", default="", mask=None, image=None, root=None, neutral=None):
    """
    Show a box in which a user can enter some text.
    You may optionally specify some default text, which will appear in the
    enterbox when it is displayed.
    Returns the text that the user entered, or None if he cancels the operation.
    """
    global boxRoot, __enterboxText, __enterboxDefaultText
    global cancelButton, nButton, entryWidget, okButton

    if title is None:
        title = ""
    if default is None:
        default = ""
    __enterboxDefaultText = default
    __enterboxText = __enterboxDefaultText

    if root:
        root.withdraw()
        boxRoot = tk.Toplevel(master=root)
        boxRoot.withdraw()
    else:
        boxRoot = tk.Tk()
        boxRoot.withdraw()

    #boxRoot.protocol('WM_DELETE_WINDOW', __enterboxQuit)
    def exit():
        geom = boxRoot.geometry()
        global_state.window_position = '+' + geom.split('+', 1)[1]
        global_state.window_size = geom[0: geom.index("+")]
        global_state.saveWindowPosition(boxRoot)
        import sys
        sys.exit(0)
    boxRoot.protocol('WM_DELETE_WINDOW', exit)
    boxRoot.title(title)
    #from os import name
    #if name == "nt":
    #    boxRoot.iconbitmap('icon.ico')
    boxRoot.geometry(global_state.window_size + global_state.window_position)
    boxRoot.bind("<Escape>", __enterboxCancel)

    # ------------- define the messageFrame ---------------------------------
    messageFrame = tk.Frame(master=boxRoot)
    messageFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the imageFrame ---------------------------------
    try:
        tk_Image = ut.load_tk_image(image)
    except Exception as inst:
        print(inst)
        tk_Image = None
    if tk_Image:
        imageFrame = tk.Frame(master=boxRoot)
        imageFrame.pack(side=tk.TOP, fill=tk.BOTH)
        label = tk.Label(imageFrame, image=tk_Image)
        label.image = tk_Image  # keep a reference!
        label.pack(side=tk.TOP, expand=tk.YES, fill=tk.X, padx='1m', pady='1m')

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = ttk.Frame(master=boxRoot)
    buttonsFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the entryFrame ---------------------------------
    entryFrame = ttk.Frame(master=boxRoot)
    entryFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # ------------- define the buttonsFrame ---------------------------------
    buttonsFrame = ttk.Frame(master=boxRoot)
    buttonsFrame.pack(side=tk.TOP, fill=tk.BOTH)

    # -------------------- the msg widget ----------------------------
    #messageWidget = tk.Message(messageFrame, width="4i", text=msg)

    messageWidget = tk.Text(
            messageFrame,
            padx=5,
            pady=5,
            height=5,
            width=200,
            background=global_state.inactive_background,
            font=(global_state.PROPORTIONAL_FONT_FAMILY, global_state.PROPORTIONAL_FONT_SIZE),
            wrap=tk.WORD,
        )
    messageWidget.delete(1.0, tk.END)
    messageWidget.insert(tk.END, msg)
    messageWidget.config(state=tk.DISABLED)
    messageWidget.pack(side=tk.TOP, expand=1, fill=tk.BOTH, padx='3m', pady='3m')

    # --------- entryWidget ----------------------------------------------
    entryWidget = ttk.Entry(entryFrame, width=500) # ширина окна текста

    entryWidget.configure(
        font=(global_state.MONOSPACE_FONT_SIZE, global_state.TEXT_ENTRY_FONT_SIZE))
    if mask:
        entryWidget.configure(show=mask)

    #entryWidget.configure(
    #    font=(global_state.MONOSPACE_FONT_FAMILY, global_state.MONOSPACE_FONT_SIZE)
    #)

    entryWidget.pack(side=tk.LEFT, padx="5m")
    entryWidget.bind("<Return>", __enterboxGetText)
    entryWidget.bind("<Escape>", __enterboxCancel)
    # put text into the entryWidget
    entryWidget.insert(0, __enterboxDefaultText)

    # ------------------ ok button -------------------------------
    okButton = ttk.Button(buttonsFrame, takefocus=1, text="OK")

    #okButton.grid(column=0, row=0, padx='3m', pady='3m', ipadx='2m', ipady='1m')
    okButton.pack(expand=1, side=tk.LEFT, padx='3m', pady='3m', ipadx='2m', ipady='1m')

    # for the commandButton, bind activation events to the activation event
    # handler
    commandButton = okButton
    handler = __enterboxGetText
    for selectionEvent in global_state.STANDARD_SELECTION_EVENTS:
        commandButton.bind("<{}>".format(selectionEvent), handler)

    # ------------------ neutral button -------------------------------
    if neutral!=None:
        nButton = ttk.Button(buttonsFrame, takefocus=1, text=neutral)

        if neutral!=None and neutral!="Очист.":
            #nButton.grid(column=1, row=0, padx='3m', pady='3m', ipadx='2m', ipady='1m')
            nButton.pack(expand=1, side=tk.LEFT, padx='3m', pady='3m', ipadx='2m', ipady='1m')

        # for the commandButton, bind activation events to the activation event
        # handler
        commandButton = nButton
        handler = __enterboxNeutral
        for selectionEvent in global_state.STANDARD_SELECTION_EVENTS:
            commandButton.bind("<{}>".format(selectionEvent), handler)

    # ------------------ cancel button -------------------------------
    cancelButton = ttk.Button(buttonsFrame, takefocus=1, text="Отмена")

    #cancelButton.grid(column=2, row=0, padx='3m', pady='3m', ipadx='2m', ipady='1m')
    cancelButton.pack(expand=1, side=tk.RIGHT, padx='3m', pady='3m', ipadx='2m', ipady='1m')

    # for the commandButton, bind activation events to the activation event
    # handler
    commandButton = cancelButton
    handler = __enterboxCancel
    for selectionEvent in global_state.STANDARD_SELECTION_EVENTS:
        commandButton.bind("<{}>".format(selectionEvent), handler)

    # ------------------- time for action! -----------------
    entryWidget.focus_force()  # put the focus on the entryWidget
    boxRoot.deiconify()
    boxRoot.mainloop()  # run it!

    # -------- after the run has completed ----------------------------------
    if root:
        root.deiconify()
    boxRoot.destroy()  # button_click didn't destroy boxRoot, so we do it now
    return __enterboxText

def __enterboxQuit():
    geom = boxRoot.geometry()
    global_state.window_position = '+' + geom.split('+', 1)[1]
    global_state.window_size = geom[0: geom.index("+")]
    return __enterboxCancel(None)


def __enterboxCancel(event):
    global __enterboxText
    geom = boxRoot.geometry()
    global_state.window_position = '+' + geom.split('+', 1)[1]
    global_state.window_size = geom[0: geom.index("+")]

    __enterboxText = None
    boxRoot.quit()

def __enterboxGetText(event):
    global __enterboxText

    __enterboxText = entryWidget.get()
    boxRoot.quit()

def __enterboxNeutral(event):
    global __enterboxText

    __enterboxText = "neutral"
    boxRoot.quit()

def __enterboxRestore(event):
    global entryWidget

    entryWidget.delete(0, len(entryWidget.get()))
    entryWidget.insert(0, __enterboxDefaultText)
