import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk
import numpy as np


SCORE = 100


class ImageRow:
    def __init__(self, master, data, label_text=None, data_dir='data'):
        self.frame = tk.Frame(master, bd=8, relief=tk.RIDGE)
        self.frame.pack(side=tk.TOP)
        if label_text is not None:
            self.label = tk.Label(self.frame, text=label_text, fg="black", font=tkFont.Font(size=16))
            self.label.pack()
        self.image_widgets = [ImageWidget(self.frame, f'{data_dir}/{path}', name.replace(' \\n ','\n'))
                              for (name, path) in data]


class ImageWidget:
    def __init__(self, master, image_path, label_text,
                 image_0_path='data/moon.png',
                 image_size=(128,128),
                 padding=(4,4)):

        self.photo_0 = ImageTk.PhotoImage(Image.open(image_0_path).resize(image_size))
        self.photo   = ImageTk.PhotoImage(Image.open(image_path).resize(image_size))
        self.label_text = label_text
        self.widget_state = 0

        frame = tk.Frame(master)
        frame.pack(side=tk.LEFT, padx=padding[0], pady=padding[1])
        self.canvas = tk.Canvas(frame, width=image_size[0], height=image_size[1])
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_0)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.pack()
        self.label = tk.Label(frame, text="\n", fg="black", font=tkFont.Font(size=16))
        self.label.pack()


    def on_click(self, event):
        bbox = self.canvas.bbox(tk.ALL)
        if bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]: # true anyway since event is caught?
            if self.widget_state==0:
                self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
                self.widget_state += 1
            elif self.widget_state==1:
                self.label.config(text=self.label_text)
                self.widget_state += 1
                global SCORE
                SCORE -= 1
                print(f'{SCORE=}')


def main():

    data = np.loadtxt('data.dat', delimiter=',', dtype=str)
    data_chunks = (data[:3], data[3:])

    root = tk.Tk()

    for i, chunk in enumerate(data_chunks):
        frame = ImageRow(root, chunk, label_text=f'Set #{i+1}')

    root.mainloop()

    print(f'{SCORE=}')


if __name__ == "__main__":
    main()
