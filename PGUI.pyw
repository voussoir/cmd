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

        x = 0
        y = 0

        self.buttonwidth = 12
        shortcuts = load_programs()
        for (index, shortcut) in enumerate(shortcuts):
            print(y, x)
            newButton = Button(
                self,
                text=shortcut.replace_extension('').basename,
                command=lambda sc=shortcut: self.launch_program(sc),
            )
            print(f'Creating button for {shortcut.basename}')
            newButton.configure(width=self.buttonwidth)
            newButton.grid(row=y, column=x)
            x += 1
            if x >= 3 and (index != len(shortcuts)-1):
                x = 0
                y += 1
        print(y, x)

        self.pack()
        self.update()

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
