import argparse
import sys
import jinja2
import textwrap

from voussoirkit import betterhelp
from voussoirkit import pathclass
from voussoirkit import pipeable
from voussoirkit import vlogging

log = vlogging.getLogger(__name__, 'imagegallery')

TEMPLATE = jinja2.Template('''
<html>
<head>
{% if title %}
<title>{{title}}</title>
{% endif %}
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0"/>
<style>
:root
{
    --color_bodybg: #272822;
    --color_codebg: rgba(255, 255, 255, 0.05);
    --color_codeborder: rgba(255, 255, 255, 0.2);
    --color_h1bg: #284142;
    --color_htmlbg: #1b1c18;
    --color_blockquotebg: rgba(0, 0, 0, 0.2);
    --color_blockquoteedge: rgba(255, 255, 255, 0.2);
    --color_inlinecodebg: rgba(255, 255, 255, 0.1);
    --color_link: #ae81ff;
    --color_maintext: #ddd;
}

*, *:before, *:after
{
    box-sizing: inherit;
}

html
{
    height: 100vh;
    box-sizing: border-box;

    background-color: var(--color_htmlbg);
    color: var(--color_maintext);

    font-family: Verdana, sans-serif;
    font-size: 10pt;
    margin: 0;
}

body
{
    min-height: 100%;
    width: fit-content;
    margin-left: auto;
    margin-right: auto;
    margin-top: 0;
    margin-bottom: 0;
    padding: 8px;
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
    width: 100%;
    max-width: 120em;
    margin-left: auto;
    margin-right: auto;
    text-align: end;
}
header > *
{
    display: inline-block;
    padding: 16px;
    background-color: var(--color_bodybg);
}

.album,
.photograph
{
    position: relative;
    margin-left: auto;
    margin-right: auto;
    margin-top: 8vh;
    margin-bottom: 8vh;
}

.photograph
{
    padding: 2vh;
    background-color: var(--color_bodybg);
    border-radius: 16px;
}
article .photograph:first-of-type
{
    margin-top: 0;
}
article .photograph:last-of-type
{
    margin-bottom: 0;
}
.photograph img,
.photograph video
{
    max-height: 92vh;
    border-radius: 8px;
}
.photograph .download_link
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
article .morelink
{
    font-size: 2em;
    text-align: center;
    margin-top: 0;
}
@media not print
{
    .photograph
    {
        box-shadow: #000 0px 0px 40px -10px;
    }
}

@media screen and (min-width: 600px)
{
    article
    {
        width: fit-content;
    }
}

@media screen and (max-width: 600px)
{
    .photograph
    {
        box-shadow: none;
    }
}

@media not all and (pointer: fine)
{
    #keyboardhint,
    #scrollbartoggle
    {
        display: none;
    }
}

h1, h2, h3, h4, h5
{
    margin-bottom: 0;
}
h1:first-child, h2:first-child, h3:first-child, h4:first-child, h5:first-child
{
    margin-top: 0;
}
h2, h3, h4, h5
{
    border-bottom: 1px solid var(--color_maintext);
    /*background-color: var(--color_h1bg);*/
}
p:last-child
{
    margin-bottom: 0;
}
h1 {font-size: 2.00em;} h1 * {font-size: inherit;}
h2 {font-size: 1.75em;} h2 * {font-size: inherit;}
h3 {font-size: 1.50em;} h3 * {font-size: inherit;}
h4 {font-size: 1.25em;} h4 * {font-size: inherit;}
h5 {font-size: 1.00em;} h5 * {font-size: inherit;}

.header_anchor_link {display: none; font-size: 1.0em; text-decoration: none}
h1:hover > .header_anchor_link {display: initial;}
h2:hover > .header_anchor_link {display: initial;}
h3:hover > .header_anchor_link {display: initial;}
h4:hover > .header_anchor_link {display: initial;}
h5:hover > .header_anchor_link {display: initial;}

a
{
    color: var(--color_link);
    cursor: pointer;
}

article *
{
    max-width: 100%;
    word-wrap: break-word;
}

#table_of_contents
{
    border: 1px solid var(--color_blockquoteedge);
    padding-top: 8px;
    padding-bottom: 8px;
    border-radius: 8px;
}

blockquote
{
    background-color: var(--color_blockquotebg);
    margin-inline-start: 0;
    margin-inline-end: 0;
    border-left: 4px solid var(--color_blockquoteedge);

    padding: 8px;
    padding-inline-start: 20px;
    padding-inline-end: 20px;
}

table
{
    border-collapse: collapse;
    font-size: 1em;
}
table, table th, table td
{
    border: 1px solid var(--color_maintext);
}
table th, table td
{
    padding: 4px;
}

ol ol, ul ul, ol ul, ul ol
{
    padding-inline-start: 20px;
}

*:not(pre) > code
{
    background-color: var(--color_inlinecodebg);
    border-radius: 4px;
    line-height: 1.5;
    padding-left: 4px;
    padding-right: 4px;
}

pre
{
    padding: 8px;
    border: 1px solid var(--color_codeborder);
    background-color: var(--color_codebg);
    overflow-x: auto;
}

code,
pre,
.highlight *
{
    font-family: monospace;
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
    {% if file.extension == 'jpg' %}
    <article class="photograph">
        <a target="_blank" href="{{urlroot}}{{file.relative_to('.', simple=True)}}"><img loading="lazy" src="{{urlroot}}thumbs/small_{{file.relative_to('.', simple=True)}}"/></a>
        {% if with_download_links %}
        <a class="download_link" download="{{file.basename}}" href="{{urlroot}}{{file.relative_to('.', simple=True)}}">#{{loop.index}}/{{files|length}}</a>
        {% endif %}
    </article>
    {% elif file.extension in ['mp4', 'mov'] %}
    <article class="photograph">
        <p>{{file.replace_extension('').basename}}</p>
        <video controls preload="none" src="{{urlroot}}{{file.relative_to('.', simple=True)}}" poster="{{urlroot}}thumbs/small_{{file.replace_extension('jpg').relative_to('.', simple=True)}}"></video>
    </article>
    {% endif %}
    {% endfor %}
</body>

<script type="text/javascript">
let desired_scroll_position = null;

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

function get_center_img()
{
    let center_x = window.innerWidth / 2;
    let center_y = window.innerHeight / 2;
    while (true)
    {
        const element = document.elementFromPoint(center_x, center_y);
        console.log(element);
        if (element.tagName === "IMG" || element.tagName === "VIDEO")
        {
            return element;
        }
        center_y -= 20;
        if (center_y <= 0)
        {
            return null;
        }
    }
}
function next_img(img)
{
    const images = Array.from(document.querySelectorAll("img,video"));
    const this_index = images.indexOf(img);
    if (this_index === images.length-1)
    {
        return img;
    }
    return images[this_index + 1];
}
function previous_img(img)
{
    const images = Array.from(document.querySelectorAll("img,video"));
    const this_index = images.indexOf(img);
    if (this_index === 0)
    {
        return img;
    }
    return images[this_index - 1];
}
function scroll_step()
{
    const distance = desired_scroll_position - document.body.scrollTop;
    const jump = (distance * 0.25) + (document.body.scrollTop < desired_scroll_position ? 1 : -1);
    document.body.scrollTop = document.body.scrollTop + jump;
    console.log(`${document.body.scrollTop} ${desired_scroll_position}`);
    const new_distance = desired_scroll_position - document.body.scrollTop;
    if (Math.abs(new_distance / distance) < 0.97)
    {
        window.requestAnimationFrame(scroll_step);
    }
}
function scroll_to_img(img)
{
    const img_centerline = img.offsetParent.offsetTop + img.offsetTop + (img.offsetHeight / 2);
    // document.body.scrollTop = img_centerline - (window.innerHeight / 2);
    desired_scroll_position = Math.round(img_centerline - (window.innerHeight / 2));
    scroll_step();
}
function scroll_to_next_img()
{
    scroll_to_img(next_img(get_center_img()));
}
function scroll_to_previous_img()
{
    scroll_to_img(previous_img(get_center_img()));
}
function arrowkey_listener(event)
{
    if (event.keyCode === 37)
    {
        scroll_to_previous_img();
    }
    else if (event.keyCode === 39)
    {
        scroll_to_next_img();
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
    document.documentElement.addEventListener("keydown", arrowkey_listener);
    document.documentElement.addEventListener("mousemove", mousemove_handler);
    mousemove_handler();
    load_scrollbar_setting();
}
document.addEventListener("DOMContentLoaded", on_pageload);
</script>
</html>
''')

def imagegallery(files, title, urlroot, with_download_links):
    html = TEMPLATE.render(
        files=files,
        title=title,
        urlroot=urlroot,
        with_download_links=with_download_links,
    )
    return html

def imagegallery_argparse(args):
    patterns = pipeable.input_many(args.patterns)
    files = list(pathclass.glob_many_files(patterns))
    files.sort()

    html = imagegallery(
        files=files,
        title=args.title,
        urlroot=args.urlroot or '',
        with_download_links=True,
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
