from tkinter import Button as tButton
from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Style, Button
import os
import subprocess
import sys
import winshell


def load_programs():
    directory = os.path.join(os.path.dirname(__file__), 'PGUI')
    shortcuts = [os.path.join(directory, p) for p in os.listdir(directory)]
    shortcuts = [p for p in shortcuts if p.lower().endswith('.lnk')]
    programs = []
    for shortcut in shortcuts:
        name = os.path.splitext(os.path.basename(shortcut))[0]
        shortcut = winshell.Shortcut(shortcut)
        program = Program(name, shortcut.path, shortcut.arguments)
        programs.append(program)
    return programs


class Program():
    def __init__(self, name, path, arguments):
        self.name = name
        self.path = os.path.abspath(path)
        self.arguments = arguments

    def __str__(self):
        return f'{self.name}: {self.path}'


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
        programs = load_programs()
        for (programindex, program) in enumerate(programs):
            print(y, x)
            newButton = Button(
                self,
                text=program.name,
                command=lambda prog=program: self.launch_program(prog),
            )
            print(f'creating button for {program.name} at {program.path}')
            newButton.configure(width=self.buttonwidth)
            newButton.grid(row=y, column=x)
            x += 1
            if x >= 3 and (programindex != len(programs)-1):
                x = 0
                y += 1
        print(y, x)

        self.pack()
        self.update()

    def launch_program(self, program):
        print('opening application', program.name)
        os.chdir(os.path.dirname(program.path))
        command = f'{program.path} {program.arguments}'
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
