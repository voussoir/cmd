import argparse
import os
import PIL.ImageTk
import qrcode
import sys
import tkinter
import tkinter.filedialog

from voussoirkit import pipeable

def save_image(root, image):
    filename = tkinter.filedialog.asksaveasfilename(
        parent=root,
        initialdir=os.getcwd(),
        filetypes=[('PNG', '*.png')],
        defaultextension='png',
    )
    if not filename:
        return
    image.save(filename)

def showqr_argparse(args):
    text = pipeable.input(args.text, split_lines=False)
    image = qrcode.make(text).get_image()

    root = tkinter.Tk()
    root.withdraw()
    root.title("QR code")
    root.bind('<Escape>', lambda *args, **kwargs: root.quit())
    root.bind('<Control-s>', lambda *args, **kwargs: save_image(root, image))

    tk_image = PIL.ImageTk.PhotoImage(image)
    tkinter.Label(root, image=tk_image).grid(row=0, column=0)

    root.update()
    width = root.winfo_reqwidth()
    height = root.winfo_reqheight()
    x_offset = (root.winfo_screenwidth() - width) / 2
    y_offset = (root.winfo_screenheight() - height) / 2

    root.geometry('%dx%d+%d+%d' % (width, height, x_offset, y_offset-50))
    root.deiconify()
    root.mainloop()
    return 0

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('text')
    parser.set_defaults(func=showqr_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
