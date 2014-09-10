#!/usr/bin/env python
# -*- coding: UTF-8 -*-
#
# (c) Roberto Gambuzzi
# Creato:          03/01/2014 18:22:58
# Ultima Modifica: 05/01/2014 13:06:28
#
# v 0.0.1.2
#
# file: C:\Dropbox\coding dojo\python_preview\__main__.py
# auth: Roberto Gambuzzi <gambuzzi@gmail.com>
# desc:
#
# $Id: __main__.py 05/01/2014 13:06:28 Roberto $
# --------------

from __future__ import division
from Tkinter import *
from PIL import Image, ImageTk, ImageSequence
from time import sleep
import glob
import itertools
import os


def multiple_file_types(*patterns):
    return list(itertools.chain.from_iterable([glob.glob(pattern) for pattern in patterns]))


def time_compare(x, y):
    if os.path.getmtime(x) > os.path.getmtime(y):
        return 1
    else:
        return -1


def subimage(src, l, t, r, b):
    dst = PhotoImage()
    dst.tk.call(dst, 'copy', src, '-from', l, t, r, b, '-to', 0, 0)
    return dst


class MyLabel(Label):
    def __init__(self, master, title, files):
        Label.__init__(self, master)
        self.cancel = None
        self.master = master
        self.files = files
        self.files.sort(time_compare)
        self.title = title
        self.idx_file = 0
        self.zoom = False
        self.realsize = False
        self.do_thumbnail = False
        self.from_top = 0
        self.frames = []
        if self.files:
            self.process_image(master, self.files[0])

    def delay90(self, e):
        self.delay = 90
        print 'self.delay', self.delay
        return "break"

    def notzoom(self, e):
        self.zoom = not self.zoom
        print 'self.zoom', self.zoom
        self.after(1, self.start_process_image)
        return "break"

    def notrealsize(self, e):
        self.realsize = not self.realsize
        print 'self.realsize', self.realsize
        self.after(1, self.start_process_image)
        return "break"

    def scroll_down(self, e):
        self.from_top += 100
        return self._scroll()

    def scroll_up(self, e):
        self.from_top -= 100
        return self._scroll()

    def _scroll(self):
        w, h = self.pil_current_image.size
        if self.from_top < 0:
            self.from_top = 0
        elif self.from_top > h - self._size[1]:
            self.from_top = h - self._size[1]
        if self.realsize:
            #self.keep_a_reference = ImageTk.PhotoImage(self.pil_current_image.crop((0,self.from_top,w,h)))
            self.keep_a_reference = subimage(self.current_photo_image, 0, self.from_top, w, self._size[1]+self.from_top)
            self.config(image=self.keep_a_reference)
        return "break"

    def next_image(self, e):
        self.idx_file += 1
        return self._image()

    def prev_image(self, e):
        self.idx_file -= 1
        return self._image()

    def _image(self):
        self.from_top = 0
        if self.idx_file == len(self.files):
            self.idx_file = 0
        if self.idx_file < 0:
            self.idx_file = len(self.files) - 1
        self.title['text'] = "Loading..."
        self.after(1, self.start_process_image)
        return "break"

    def start_process_image(self):
        self.process_image(self.master, self.files[self.idx_file])

    def process_image(self, master, filename):
        if self.cancel:
            self.after_cancel(self.cancel)
            sleep(self.delay / 1000.0)

        root.update()
        self._size = root.winfo_width(), root.winfo_height() - self.title.winfo_height() - 4

        try:
            self.pil_current_image = im = Image.open(filename)
        except:
            return

        if self.zoom:
            resize_size = list(self._size)
            a1 = resize_size[0] / resize_size[1]
            a2 = im.size[0] / im.size[1]
            if a1 < a2:
                resize_size[1] = int(resize_size[0] / a2)
            else:
                resize_size[0] = int(resize_size[1] * a2)
            self.resize_size = resize_size

        self.oversize = im.size[0] > self._size[0] or im.size[1] > self._size[1]
        self.do_thumbnail = not self.realsize and self.oversize

        try:
            self.delay = im.info['duration']
        except KeyError:
            self.delay = 100
        if self.delay == 0:
            self.delay = 90

        self.frames = []
        pal = im.getpalette()
        prev = im.convert('RGBA')
        self.add_frame(prev)
        self.title['text'] = filename + " --- delay = %i --- realsize %i --- zoom %i --- oversize %i" % (
        self.delay, self.realsize, self.zoom, self.oversize)
        self.config(image=self.frames[0])
        self.current_photo_image = self.frames[0]
        if self.oversize and self.realsize:
            self.config(anchor=N)
        else:
            self.config(anchor=CENTER)
        self.update()
        prev_dispose = True
        for i, frame in enumerate(ImageSequence.Iterator(im)):
            try:
                dispose = frame.dispose
            except:
                break

            if frame.tile:
                x0, y0, x1, y1 = frame.tile[0][1]
                if not frame.palette.dirty:
                    frame.putpalette(pal)
                frame = frame.crop((x0, y0, x1, y1))
                bbox = (x0, y0, x1, y1)
            else:
                bbox = None

            if dispose is None:
                prev.paste(frame, bbox, frame.convert('RGBA'))
                #                 prev.save(r'c:\temp\png\%04i.png' % i )
                self.add_frame(prev)
                prev_dispose = False
            else:
                if prev_dispose:
                    prev = Image.new('RGBA', img.size, (0, 0, 0, 0))
                out = prev.copy()
                out.paste(frame, bbox, frame.convert('RGBA'))
                #                 out.save(r'c:\temp\png\%04i.png' % i )
                self.add_frame(out)

        self.idx = 0
        if len(self.frames) > 1:
            del self.frames[1]
            self.cancel = self.after(self.delay, self.play)

    def play(self):
        self.config(image=self.frames[self.idx])
        self.idx += 1
        if self.idx == len(self.frames):
            self.idx = 0
        self.cancel = self.after(self.delay, self.play)

    def add_frame(self, image):
        if self.do_thumbnail:
            temp = image.copy()
            temp.thumbnail(self._size, Image.ANTIALIAS)
            self.frames.append(ImageTk.PhotoImage(temp))
        elif self.zoom:
            temp = image.resize(self.resize_size, Image.ANTIALIAS)
            self.frames.append(ImageTk.PhotoImage(temp))
        else:
            self.frames.append(ImageTk.PhotoImage(image))


class App(Frame):
    def kill(self, event=None):
        if self.image.cancel:
            self.image.after_cancel(self.image.cancel)
            sleep(self.image.delay / 1000.0)
        self.quit()

    def __init__(self, master):
        Frame.__init__(self, master)
        self.grid(row=0, sticky=N + E + S + W)
        self.rowconfigure(1, weight=2)
        self.columnconfigure(0, weight=1)
        self.title = Label(self, text='Loading...')
        self.title.grid(row=0, sticky=E + W)
        self.image = MyLabel(self, self.title, multiple_file_types('*.jpg', '*.gif', '*.png'))
        self.image.grid(row=1, sticky=N + E + S + W)

        root.protocol("WM_DELETE_WINDOW", self.kill)


def on_form_event(event):
    w, h = root.winfo_width(), root.winfo_height()
    if event.type == '22' and (root.pre_w, root.pre_h) != (w, h) and app.image.do_thumbnail: #resize
        if root.after_cancel_id:
            root.after_cancel(root.after_cancel_id)
        root.after_cancel_id = root.after(200, app.image.start_process_image)
    root.pre_w, root.pre_h = root.winfo_width(), root.winfo_height()


if __name__ == "__main__":
    root = Tk()
    #w, h = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry("640x480")
    root.update()
    root.pre_w, root.pre_h = root.winfo_width(), root.winfo_height()
    if os.name == 'nt':
        root.wm_state('zoomed')
    root.rowconfigure(0, weight=1)
    root.columnconfigure(0, weight=1)

    app = App(root)
    root.after_cancel_id = None
    root.bind('<Right>', app.image.next_image)
    root.bind('<Left>', app.image.prev_image)
    root.bind('<Down>', app.image.scroll_down)
    root.bind('<Up>', app.image.scroll_up)
    root.bind('1', app.image.notrealsize)
    root.bind('d', app.image.delay90)
    root.bind('z', app.image.notzoom)
    root.bind('q', app.kill)
    root.bind('<Configure>', on_form_event)
    app.mainloop()

    try:
        root.destroy()
    except:
        pass
