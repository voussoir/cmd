import tkinter
from tkinter import Button as tButton
from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Style, Button
import os
import subprocess
import sys

from voussoirkit import pathclass

def load_programs():
    directory = os.path.join(os.path.dirname(__file__), 'PGUI')
    shortcuts = [os.path.join(directory, p) for p in os.listdir(directory)]
    shortcuts = [p for p in shortcuts if p.lower().endswith('.lnk')]
    shortcuts = [pathclass.Path(p) for p in shortcuts]
    return shortcuts

class PGUILauncher(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent

        self.style = Style()
        self.style.theme_use("clam")
        self.pack(fill=BOTH, expand = 1)

        self.filter_var = tkinter.StringVar()
        self.filter_var.trace('w', self.filter)
        self.filter_entry = tkinter.Entry(self, textvariable=self.filter_var)
        self.filter_entry.grid(row=0, column=0, columnspan=999, sticky='ew')
        self.filter_entry.bind('<Return>', self.launch_filtered)
        self.filter_entry.focus()

        x = 0
        y = 1

        self.buttons = []
        self.buttonwidth = 12
        shortcuts = load_programs()
        for (index, shortcut) in enumerate(shortcuts):
            print(y, x)
            button = Button(
                self,
                text=shortcut.replace_extension('').basename,
                command=lambda sc=shortcut: self.launch_program(sc),
            )
            button.shortcut = shortcut
            print(f'Creating button for {shortcut.basename}')
            button.configure(width=self.buttonwidth)
            button.grid(row=y, column=x)
            self.buttons.append(button)
            x += 1
            if x >= 3 and (index != len(shortcuts)-1):
                x = 0
                y += 1
        print(y, x)

        self.pack()
        self.update()

    def filter(self, *args):
        text = self.filter_entry.get().lower()
        for button in self.buttons:
            if text == '':
                button['state'] = 'normal'
            elif text not in button['text'].lower():
                button['state'] = 'disabled'

    def launch_filtered(self, *args):
        enabled = [b for b in self.buttons if b['state'].string == 'normal']
        if len(enabled) != 1:
            return

        button = enabled[0]
        self.launch_program(button.shortcut)

    def launch_program(self, shortcut):
        print('opening application', shortcut.basename)
        os.chdir(shortcut.parent.absolute_path)
        command = f'"{shortcut.absolute_path}"'
        subprocess.Popen(command, shell=True)
        self.quit()


def main(argv):
    root = Tk()
    root.title("PGUI")
    root.resizable(0,0)

    ex = PGUILauncher(root)

    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    x_offset = (root.winfo_screenwidth() - width) / 2
    y_offset = (root.winfo_screenheight() - height) / 2

    root.geometry('%dx%d+%d+%d' % (width, height, x_offset, y_offset-50))
    root.mainloop()

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
