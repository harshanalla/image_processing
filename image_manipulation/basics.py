from scipy import misc
import matplotlib.pyplot as plt
import collections
import re
import os
from PIL import Image
im = Image.open('img\\mtn_dew_tweaked.png')


fill_color = (120, 8, 220)

# im = im.convert('RGBA')

if im.mode in ('RGBA', 'LA'):
    background = Image.new(im.mode[:-1], im.size, fill_color)
    background.paste(im, im.split()[-1])
    im = background


im.convert("RGB")
im.show()
while input()!='q':
    pass



