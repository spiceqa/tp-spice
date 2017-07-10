#!/usr/bin/env python

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See LICENSE for more details.

"""Helper to performs actions on X clipboard.

    http://www.pygtk.org/pygtk2reference/class-gtkclipboard.html
    http://www.pygtk.org/pygtk2reference/class-gdkpixbuf.html
    https://github.com/gdw2/zim/blob/master/zim/gui/clipboard.py

"""


import sys
import os
import logging
import argparse
# Unable to import pygtk and gtk in virtualenv,
# nevertheless deps scripts wont be run in virtualenv.
#pylint: disable=F0401
import pygtk
pygtk.require('2.0')
import gtk

from PIL import Image, ImageDraw


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser(
    description='Helper to operate on X clipboard.')

group = parser.add_mutually_exclusive_group(required=True)

group.add_argument("-c", "--clear", help="Clear clipboard.",
                   action='store_true')
group.add_argument("-t", "--txt2cb", metavar='TEXT',
                   help="Put text to clipboard.")
group.add_argument("-i", "--img2cb", metavar='FILE',
                   help="Put image to clipboard.")
group.add_argument("-f", "--txtf2cb", metavar='FILE',
                   help="Put text from file to clipboard.")
group.add_argument("-k", "--kbytes2cb", metavar="KBYTES",
                   help="Put kbytes of text in clipboard.")
group.add_argument("-s", "--cb2img", metavar='FILE',
                   help="Dump image from clipboard to file.")
group.add_argument("-q", "--query", action='store_true',
                   help="Dump information about clipboard.")
group.add_argument("-d", "--cb2txtf", metavar='FILE',
                   help="Dump text from clipboard to file.")
group.add_argument("-o", "--cb2stdout", action='store_true',
                   help="Dump clipboard to stdout.")
group.add_argument("-g", "--genimg", metavar='INT', nargs='?', type=int,
                   help="Generate an image of side size INT pixels.")
parser.add_argument("file_n", nargs='?', metavar='FILE', default="test.png",
                    help="Specify file name.")


args = parser.parse_args()

clipboard = gtk.clipboard_get()

if args.clear:
    # We can clear only owned clipboard. Before clear clipboard we must own
    # it. .clear() method can be called only on owned clipboard.
    clipboard.set_text("Anything.")  # Grab clipboard. Become owner of it.
    clipboard.store()                # Apply
    clipboard.clear()                # Now we can clear it.
    logger.info("Clear clipboard.")
elif args.genimg:
    size_img = args.genimg
    img = Image.new('RGB', size=(size_img, size_img), color='yellow')
    draw = ImageDraw.Draw(img)
    for i in range(0, size_img, 3):
        draw.line([(i, 0), (size_img, size_img)], fill='green')
        draw.line([(0, i), (size_img, size_img)], fill='red')
        draw.line([(size_img, 0), (0, i)], fill='blue')
    draw.ellipse((0.6*size_img, 0.15*size_img, 0.8*size_img, 0.3*size_img),
                 fill='red')
    with open(args.file_n, 'w') as fd:
        img.save(fd, args.file_n.split(".")[-1])
elif args.txt2cb:
    clipboard.clear()
    clipboard.set_text(args.txt2cb)
    clipboard.store()
    logger.info("Put text into the clipboard. %s characters.",
                len(args.txt2cb))
elif args.img2cb:
    pixbuf = gtk.gdk.pixbuf_new_from_file(args.img2cb)
    clipboard.clear()
    clipboard.set_image(pixbuf)
    clipboard.store()
    w = pixbuf.get_width()
    h = pixbuf.get_height()
    logger.info('Put image to clipboard %sx%s.', w, h)
elif args.txtf2cb:
    with open(args.txtf2cb) as fd:
        contents = fd.read()
    clipboard.clear()
    clipboard.set_text(contents)
    clipboard.store()
    logger.info('Put text from %s to clipboard.', args.txtf2cb)
elif args.kbytes2cb:
    pattern = "Hello my dear friend.\n"
    pattern_len = len(pattern)
    req_len = int(args.kbytes2cb) * 1024
    repeat = req_len / pattern_len + 1
    string = pattern * repeat
    string = string[:req_len-1]
    clipboard.clear()
    clipboard.set_text(string)
    clipboard.store()
    logger.info("Put in clipboard text %s kbytes.", args.kbytes2cb)
elif args.cb2img:
    if clipboard.wait_is_image_available():
        image = clipboard.wait_for_image()
        _, extension = os.path.splitext(args.cb2img)
        ftype = extension.lower().lstrip('.')
        image.save(args.cb2img, ftype)
        logger.info("Store image to %s.", args.cb2img)
    else:
        raise Exception("Clipboard doesn't have an image.")
elif args.cb2txtf:
    text = clipboard.wait_for_text()
    assert isinstance(text, str)
    with open(args.cb2txtf, 'w') as fd:
        fd.write(text)
    logger.info("Dump clipboard text to file %s.", args.cb2txtf)
elif args.cb2stdout:
    targets = clipboard.wait_for_targets()
    if not targets:
        raise Exception("Clipboard is empty.")
    elif 'image/png' in targets:
        selectiondata = clipboard.wait_for_contents('image/png')
        pixbuf = selectiondata.get_pixbuf()
        if pixbuf:
            def pixbuf_save_func(buf):
                sys.stdout.write(buf)
            pixbuf.save_to_callback(pixbuf_save_func, "png")
    elif 'STRING' in targets:
        selectiondata = clipboard.wait_for_contents('STRING')
        print selectiondata.get_text()
elif args.query:
    targets = clipboard.wait_for_targets()
    logger.info(targets)
