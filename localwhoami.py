import base64
import qrcode
import argparse
import flask; from flask import request
import socket
import sys
import io

def localwhoami(port):
    site = flask.Flask(__name__)
    my_ip = socket.gethostbyname(socket.gethostname())
    print(my_ip)
    my_url = f'http://{my_ip}:{port}'
    url_qr = qrcode.make(my_url, border=0)
    png_bytes = io.BytesIO()
    url_qr.save(png_bytes, format='png')
    png_bytes.seek(0)
    png_bytes = png_bytes.read()
    png_base64 = base64.b64encode(png_bytes).decode('ascii')

    @site.route('/')
    def root():
        ip = request.remote_addr
        if ip == '127.0.0.1':
            ip = my_ip
        return f'''
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
        <style>
        html{{height: 100vh;box-sizing: border-box;}}
        *, *:before, *:after{{box-sizing: inherit;}}
        body{{display:grid;grid-auto-flow:row;grid-gap:16px;justify-content:center;background-color:grey}}
        div{{background-color: white; padding: 16px; border-radius: 16px;}}
        </style>
        <div>
        <center>You are</center>
        <center style="font-size:32pt; font-weight:bold">{ip}</center>
        </div>
        <div>
        <div><img src="data:image/png;base64,{png_base64}"/></div>
        <center>{my_url}</center>
        </div>
        '''
    site.run(host='0.0.0.0', port=port)

def localwhoami_argparse(args):
    return localwhoami(port=args.port)

def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('port')
    parser.set_defaults(func=localwhoami_argparse)

    args = parser.parse_args(argv)
    return args.func(args)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
