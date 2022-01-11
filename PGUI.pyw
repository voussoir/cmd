import tkinter
import os
import subprocess
import sys

from voussoirkit import pathclass
from voussoirkit import vlogging

log = vlogging.get_logger(__name__, 'pgui')

BUTTON_WIDTH = 12

MAIN_BG = '#000'
MAIN_FG = '#FFF'
ENTRY_BG = '#222'
BUTTON_BG_NORMAL = '#000'
BUTTON_BG_HIGHLIGHT = '#00aa00'
FOLDER_EMOJI = '\U0001F4C1'

PGUI_FOLDER = pathclass.Path(__file__).parent.with_child('PGUI')

def load_programs():
    log.debug('Loading programs from %s.', PGUI_FOLDER.absolute_path)
    shortcuts = PGUI_FOLDER.glob_files('*.lnk')
    shortcuts.sort()
    return shortcuts

class PGUILauncher(tkinter.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=MAIN_BG)

        self._init_filter_entry()
        self._init_buttons()

        self.ready_to_launch = None

        self.pack()
        self.update()

    def _init_buttons(self):
        shortcuts = load_programs()

        # This keeps the grid looking mostly square regardless of input count.
        column_count = int(len(shortcuts) ** 0.5)
        column_count = max(column_count, 1)

        self.buttons = []

        for (index, shortcut) in enumerate(shortcuts):
            button = tkinter.Button(
                self,
                bg=BUTTON_BG_NORMAL,
                command=lambda sc=shortcut: self.launch_program(sc),
                fg=MAIN_FG,
                height=2,
                text=shortcut.replace_extension('').basename,
                width=BUTTON_WIDTH,
            )
            button.shortcut = shortcut
            print(f'Creating button for {shortcut.basename}')
            # Plus 1 because row 0 is the search box.
            button.grid(
                row=(index // column_count) + 1,
                column=index % column_count,
                padx=1,
                pady=1,
            )
            self.buttons.append(button)

    def _init_filter_entry(self):
        # The only way to add padding around the text entry is to put it in its
        # own frame element. Thanks Kevin
        # https://stackoverflow.com/a/51823093/5430534
        self.filter_var = tkinter.StringVar()
        self.filter_var.trace('w', self.filter)
        self.upper_frame = tkinter.Frame(self, bg=ENTRY_BG)
        self.filter_entry = tkinter.Entry(
            self.upper_frame,
            bg=ENTRY_BG,
            fg=MAIN_FG,
            insertbackground=MAIN_FG,
            relief=tkinter.FLAT,
            textvariable=self.filter_var,
        )
        self.filter_entry.bind('<Return>', self.launch_filtered)
        self.filter_entry.bind('<Escape>', self.quit)

        self.open_folder_button = tkinter.Button(
            self.upper_frame,
            text=FOLDER_EMOJI,
            bg=BUTTON_BG_NORMAL,
            fg=MAIN_FG,
            command=lambda: self.open_pgui_folder(),
        )

        self.upper_frame.columnconfigure(0, weight=1)
        self.upper_frame.grid(row=0, column=0, columnspan=999, sticky='ew', padx=8, pady=8)
        self.filter_entry.grid(row=0, column=0, sticky='news', padx=2, pady=2)
        self.open_folder_button.grid(row=0, column=1, sticky='news', padx=2, pady=2)
        return self.filter_entry

    def filter(self, *args):
        text = self.filter_entry.get().lower()
        enabled = []
        for button in self.buttons:
            button.configure(bg=BUTTON_BG_NORMAL)
            if text == '' or text in button['text'].lower():
                button['state'] = 'normal'
                enabled.append(button)
            else:
                button['state'] = 'disabled'

        if len(enabled) == 1:
            enabled[0].configure(bg=BUTTON_BG_HIGHLIGHT)
            self.ready_to_launch = enabled[0]
        else:
            self.ready_to_launch = None

    def launch_filtered(self, *args):
        if self.ready_to_launch is None:
            return

        self.launch_program(self.ready_to_launch.shortcut)

    def launch_program(self, shortcut):
        print('opening application', shortcut.basename)
        os.chdir(shortcut.parent.absolute_path)
        command = f'"{shortcut.absolute_path}"'
        subprocess.Popen(command, shell=True)
        self.quit()

    def open_pgui_folder(self):
        if os.name == 'nt':
            command = ['explorer.exe', PGUI_FOLDER.absolute_path]
        else:
            command = ['xdg-open', PGUI_FOLDER.absolute_path]
        subprocess.Popen(command, shell=True)

    def quit(self, *args):
        return super().quit()

@vlogging.main_decorator
def main(argv):
    root = tkinter.Tk()
    root.withdraw()
    root.title('PGUI')
    root.resizable(0,0)

    pgui = PGUILauncher(root)
    pgui.pack(fill=tkinter.BOTH, expand=True)
    pgui.filter_entry.focus()

    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    x_offset = (root.winfo_screenwidth() - width) / 2
    y_offset = (root.winfo_screenheight() - height) / 2

    root.geometry('%dx%d+%d+%d' % (width, height, x_offset, y_offset-50))
    root.deiconify()
    root.mainloop()

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
