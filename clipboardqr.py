import pyperclip
import qrcode

qrcode.make(pyperclip.paste()).show()
