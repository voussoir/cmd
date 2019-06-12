set basename=%~n1
set newname="%basename%.mp4"
ffmpeg -i %1 -pix_fmt yuv420p -preset placebo -vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" %newname%
