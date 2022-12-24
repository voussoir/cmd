import argparse
import sys
import jinja2
import textwrap

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'imagegallery')

def imagegallery_argparse(args):
    patterns = pipeable.input_many(args.patterns)
    files = list(pathclass.glob_many_files(patterns))
    files.sort()

    html = jinja2.Template(textwrap.dedent('''
    <html>
    <head>
    {% if title %}
    <title>{{title}}</title>
    {% endif %}
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <style>
    html
    {
        background-color: black;
        color: white;
        font-family: sans-serif;
    }
    body,
    body h1
    {
        text-align: center;
    }
    body *
    {
        text-align: initial;
    }
    body.noscrollbar::-webkit-scrollbar
    {
        display: none;
    }
    body.noscrollbar
    {
        scrollbar-width: none;
    }
    header
    {
        text-align: end;
    }
    a
    {
        cursor: pointer;
        color: #ae81ff;
    }
    p
    {
        margin-left: auto;
        margin-right: auto;
        width: 100%;
        max-width: 1024px;
    }
    .photocell
    {
        display: block;
        position: relative;
        margin-left: auto;
        margin-right: auto;
        margin-top: 8px;
        margin-bottom: 8px;
        max-width: 1024px;
    }
    .photocell img
    {
        min-height: 100px;
        min-width: 100px;
        max-width: 100%;
    }
    .photocell .download_link
    {
        position: absolute;
        bottom: 8px;
        right: 8px;
        text-align: center;
        background-color: white;
        padding: 1px;
        color: black;
        text-decoration: none;
        font-family: sans-serif;
        border-radius: 4px;
        font-weight: bold;
        opacity: 80%;
    }
    @media not all and (pointer: fine)
    {
        #scrollbartoggle
        {
            display: none;
        }
    }

    </style>
    </head>
    <body>
        <header>
            <a id="scrollbartoggle" onclick="return toggle_scrollbar();">scrollbar on/off</a>
        </header>
        {% if title %}
        <h1>{{title}}</h1>
        {% endif %}

        <p>Click each photo to view its full resolution. Click the number to download it.</p>

        {% for file in files %}
        <div class="photocell">
            <a target="_blank" href="{{urlroot}}{{file.relative_to('.', simple=True)}}"><img loading="lazy" src="{{urlroot}}thumbs/small_{{file.relative_to('.', simple=True)}}"/></a>
            <a class="download_link" download="{{file.basename}}" href="{{urlroot}}{{file.relative_to('.', simple=True)}}">#{{loop.index}}/{{files|length}}</a>
        </div>
        {% endfor %}
    </body>

    <script type="text/javascript">
    function toggle_scrollbar()
    {
        if (document.body.classList.contains("noscrollbar"))
        {
            document.body.classList.remove("noscrollbar");
            localStorage.setItem("show_scrollbar", "yes");
        }
        else
        {
            document.body.classList.add("noscrollbar");
            localStorage.setItem("show_scrollbar", "no");
        }
    }

    function load_scrollbar_setting()
    {
        if (localStorage.getItem("show_scrollbar") === "no")
        {
            document.body.classList.add("noscrollbar");
        }
        else
        {
            document.body.classList.remove("noscrollbar");
        }
    }

    let hide_cursor_timeout = null;
    function hide_cursor()
    {
        document.documentElement.style.cursor = "none";
    }
    function show_cursor()
    {
        document.documentElement.style.cursor = "";
    }
    function mousemove_handler()
    {
        show_cursor();
        clearTimeout(hide_cursor_timeout);
        hide_cursor_timeout = setTimeout(hide_cursor, 3000);
    }
    function on_pageload()
    {
        document.documentElement.addEventListener("mousemove", mousemove_handler);
        mousemove_handler();
        load_scrollbar_setting();
    }
    document.addEventListener("DOMContentLoaded", on_pageload);
    </script>
    </html>
    ''')).render(
        files=files,
        title=args.title,
        urlroot=args.urlroot or '',
    )
    pathclass.Path('gallery.html').open('w', encoding='utf-8').write(html)
    return 0

@vlogging.main_decorator
def main(argv):
    parser = argparse.ArgumentParser(
        description='''
        ''',
    )
    parser.add_argument(
        'patterns',
        nargs='*',
        help='''
        ''',
    )
    parser.add_argument(
        '--title',
        default=None,
        help='''
        ''',
    )
    parser.add_argument(
        '--urlroot',
        default=None,
        help='''
        ''',
    )
    parser.set_defaults(func=imagegallery_argparse)

    return betterhelp.go(parser, argv)

if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
