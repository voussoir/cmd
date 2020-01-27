from tkinter import Button as tButton
from tkinter import Tk, BOTH
from tkinter.ttk import Frame, Style, Button
import os
import subprocess
import winshell


def load_programs():
    directory = os.path.join(os.path.dirname(__file__), 'PGUI')
    shortcuts = [os.path.join(directory, p) for p in os.listdir(directory)]
    shortcuts = [p for p in shortcuts if p.lower().endswith('.lnk')]
    programs = []
    for shortcut in shortcuts:
        name = os.path.splitext(os.path.basename(shortcut))[0]
        shortcut = winshell.Shortcut(shortcut)
        program = Program(name, f'{shortcut.path} {shortcut.arguments}')
        programs.append(program)
    return programs


class Program():
    def __init__(self, name, path):
        self.name = name
        self.path = os.path.abspath(path)

    def __str__(self):
        return f'{self.name}: {self.path}'


class PGUILauncher(Frame):
    def __init__(self, parent):
        Frame.__init__(self, parent)

        self.parent = parent
        self.init_ui()

    def launch_program(self, program):
        print('opening application', program.name)
        os.chdir(os.path.dirname(program.path))
        subprocess.Popen(program.path, shell=True)
        self.quit()

    def init_ui(self):
        self.parent.resizable(0,0)
        self.parent.title("PGUI")
        self.style = Style()
        self.style.theme_use("clam")
        self.pack(fill=BOTH, expand = 1)

        x = 0
        y = 0

        self.buttonwidth = 12
        programs = load_programs()
        for (programindex, program) in enumerate(programs):
            print(y, x)
            newButton = Button(self, text=program.name, command=lambda program=program: self.launch_program(program))
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

        width = self.parent.winfo_reqwidth()
        height = self.parent.winfo_reqheight()
        x_offset = (self.parent.winfo_screenwidth() - width) / 2
        y_offset = (self.parent.winfo_screenheight() - height) / 2

        self.parent.geometry('%dx%d+%d+%d' % (width, height, x_offset, y_offset-50))

def main():
    root = Tk()
    ex = PGUILauncher(root)
    root.mainloop()

if __name__ == '__main__':
    main()
