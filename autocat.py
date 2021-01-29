import glob
import os
import sys
import tempfile

if len(sys.argv) < 3:
    raise ValueError()

output_filename = sys.argv.pop(-1)
patterns = sys.argv[1:]

names = [name for pattern in patterns for name in glob.glob(pattern)]
names = [os.path.abspath(x) for x in names]
cat_lines = [f'file \'{x}\'' for x in names]
cat_text = '\n'.join(cat_lines)
cat_file = tempfile.TemporaryFile('w', encoding='utf-8', delete=False)
cat_file.write(cat_text)
cat_file.close()

cmd = f'ffmpeg -f concat -safe 0 -i {cat_file.name} -map 0:v? -map 0:a? -map 0:s? -c copy "{output_filename}"'
os.system(cmd)

os.remove(cat_file.name)
