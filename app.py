import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk


class ImageWidget:
    def __init__(self, master, image_path, label_text):
        image = Image.open(image_path)
        self.photo = ImageTk.PhotoImage(image)

        frame = tk.Frame(master)
        frame.pack(side=tk.LEFT, padx=5, pady=5)

        self.canvas = tk.Canvas(frame, width=image.width, height=image.height)
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.bind("<Button-1>", self.on_click)
        self.label = tk.Label(frame, text="\n", fg="black", font=tkFont.Font(size=16))
        self.label.pack()
        self.label_text = label_text

    def on_click(self, event):
        bbox = self.canvas.bbox(tk.ALL)
        if bbox[0] <= event.x <= bbox[2] and bbox[1] <= event.y <= bbox[3]:
            self.label.config(text=self.label_text)


def main():
    root = tk.Tk()
    image_widget1 = ImageWidget(root, "peppers.png", 'Scientist \n 1')
    image_widget2 = ImageWidget(root, "peppers.png", 'Scientist \n 2')
    image_widget3 = ImageWidget(root, "peppers.png", 'Scientist \n 3')
    root.mainloop()


if __name__ == "__main__":
    main()
