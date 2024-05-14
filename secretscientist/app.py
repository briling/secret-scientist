import sys
import time
import os
import random
import argparse
import numpy as np
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk

DIR = os.path.dirname(__file__)+'/'

def pop_random(lst):
    return lst.pop(random.randrange(0, len(lst)))


def image_resize(img, image_size):
    h = image_size[1]
    w = h * img.width / img.height
    if w > image_size[0]:
        w = image_size[0]
        h = w * img.height / img.width
    return img.resize((int(w), int(h)))


def redraw_canvas(canvas, photo):
    canvas.delete('all')
    canvas.create_image(canvas.winfo_reqheight()//2,
                        canvas.winfo_reqwidth()//2,
                        anchor="center", image=photo)


class ImageRow:
    def __init__(self, master, data, SCORE, COST,
                 label_text=None, data_dir=f'{DIR}/scientists', padding=(4,4),
                 image_size=(128,128), fs=16):
        self.frame = tk.Frame(master, bd=8, relief=tk.RIDGE)
        self.frame.pack(side=tk.TOP, padx=8*padding[0], pady=8*padding[1])
        if label_text is not None:
            self.label = tk.Label(self.frame, text=label_text, fg="black", font=tkFont.Font(size=fs))
            self.label.pack()
        self.image_widgets = [ImageWidget(self.frame, f'{data_dir}/{path}', name.replace(' \\n ','\n'), SCORE, COST,
                                          image_size=image_size, fs=fs)
                              for (name, path) in data]


class ImageWidget:
    def __init__(self, master, image_path, label_text, SCORE, COST,
                 image_0_path=f'{DIR}/data/moon.png', image_size=(128,128), padding=(4,4), fs=16):

        self.photo_0 = ImageTk.PhotoImage(Image.open(image_0_path).resize(image_size))
        self.photo   = ImageTk.PhotoImage(image_resize(Image.open(image_path), image_size))
        self.label_text = label_text
        self.widget_state = 0
        self.score = SCORE
        self.cost = COST
        self.image_size = image_size

        frame = tk.Frame(master)
        frame.pack(side=tk.LEFT, padx=padding[0], pady=padding[1])
        self.canvas = tk.Canvas(frame, width=image_size[0], height=image_size[1])
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_0)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.pack()
        self.label = tk.Label(frame, text="\n", fg="black", font=tkFont.Font(size=fs), height=5, wraplength=image_size[0])
        self.label.pack()


    def on_click(self, event):
        if self.widget_state<=1:
            if self.widget_state==0:
                redraw_canvas(self.canvas, self.photo)
            else:
                self.label.config(text=self.label_text)
            self.widget_state += 1
            new_score = self.score.get() - self.cost.get()
            if new_score > 0:
                self.score.set(new_score)
            else:
                self.score.set(1)


class PeopleChoice:
    def __init__(self, master, image_paths, SCORE, CORRECT,
                 image_size=(128,128), padding=(4,4),
                 switch_pics=(f'{DIR}/data/switch_camera.png', f'{DIR}/data/switch_camera_red.png')):


        self.photos = [ImageTk.PhotoImage(image_resize(Image.open(path), image_size)) for path in image_paths]
        self.switch_pics = [ImageTk.PhotoImage(Image.open(path).resize(image_size)) for path in switch_pics]
        self.widget_state = 0
        self.first_switch = 1
        self.score = SCORE
        self.correct = CORRECT

        def put_photo(master, photo):
            frame = tk.Frame(master)
            frame.pack(side=tk.TOP, padx=padding[0], pady=padding[1])
            canvas = tk.Canvas(frame, width=image_size[0], height=image_size[1])
            canvas.create_image(image_size[0]//2, image_size[1]//2, anchor="center", image=photo)
            canvas.bind("<Button-1>", self.on_click)
            canvas.pack()
            return canvas

        self.frame = tk.Frame(master)
        self.frame.pack(side=tk.TOP, padx=16*padding[0], pady=16*padding[1])
        self.canvas1 = put_photo(self.frame, self.photos[0])
        self.canvas_switch = put_photo(self.frame, self.switch_pics[0])
        self.canvas2 = put_photo(self.frame, self.photos[1])


    def on_click(self, event):
        redraw_canvas(self.canvas1, self.photos[not self.widget_state])
        redraw_canvas(self.canvas2, self.photos[self.widget_state])
        self.widget_state = (self.widget_state+1)%2
        self.correct.set(not self.correct.get())
        if self.first_switch:
            self.first_switch = 0
            redraw_canvas(self.canvas_switch, self.switch_pics[1])
        else:
            new_score = self.score.get() - 1
            if new_score > 0:
                self.score.set(new_score)


class GameControls:
    def __init__(self, master, SCORE, TOTAL, CORRECT, post_submit_hook, padding=(4,4), fs=16):
        self.score = SCORE
        self.total = TOTAL
        self.correct = CORRECT
        self.image_rows = None
        self.frame = tk.Frame(master)
        self.frame.pack(side=tk.TOP, padx=16*padding[0], pady=16*padding[1])
        label1 = tk.Label(self.frame, text='SCORE:', fg="black", font=tkFont.Font(size=fs//16*28))
        self.label_score = tk.Label(self.frame, textvariable=SCORE, fg="black", font=tkFont.Font(size=fs*2))
        label2 = tk.Label(self.frame, text='TOTAL:', fg="black", font=tkFont.Font(size=fs//16*28))
        self.label_total = tk.Label(self.frame, textvariable=TOTAL, fg="black", font=tkFont.Font(size=fs*2))
        label1.pack()
        self.label_score.pack()
        label2.pack()
        self.label_total.pack()

        self.post_submit_hook = post_submit_hook
        self.button = tk.Button(self.frame, text="SUBMIT", font=tkFont.Font(size=fs//16*28), command=self.submit)
        self.button.pack()


    def submit(self):
        if self.correct.get():
            new_total = self.total.get() + self.score.get()
        else:
            new_total = self.total.get() + self.score.get() - 200

        self.total.set(new_total)
        self.label_total.config(fg=('green' if self.correct.get() else 'red'))
        self.image_rows, self.people_choice = self.post_submit_hook()


def load_data(data_path, randomize, people_dir=f'{DIR}/people'):

    raw_data = np.loadtxt(data_path, delimiter=',', dtype=str)

    by_presenter = {}
    for i, key in enumerate(raw_data[:,1]):
        if key not in by_presenter:
            by_presenter[key] = []
        by_presenter[key].append(raw_data[i,2:])
    for key, val in by_presenter.items():
        random.shuffle(val)
        by_presenter[key] = np.array(val)

    presenters = [key for key, val in by_presenter.items() if len(val)>1]
    presenters_pic = {key: f'{people_dir}/{key.lower()}.jpg' for key in presenters}

    if randomize:
        presenter_pairs = ((pop_random(presenters), pop_random(presenters)) for _ in range(len(presenters)//2)) # generator since we yeild it later
    else:
        raise NotImplementedError

    def next_problem():
        p1, p2 = next(presenter_pairs)
        data_chunks = (by_presenter[p1], by_presenter[p2])
        min_len = min(len(x) for x in data_chunks)
        data_chunks = (data_chunks[0][:min_len], data_chunks[1][:min_len])
        is_correct_order = random.choice([True, False])
        if not is_correct_order:
            p1, p2 = p2, p1
        return (presenters_pic[p1], presenters_pic[p2]), data_chunks, is_correct_order

    return next_problem


def main(argv):

    parser = argparse.ArgumentParser()
    parser.add_argument('--demo',    action='store_true',   help='show a demo')
    parser.add_argument('--timeout', type=int, default=5,   help='timeout in seconds')
    parser.add_argument('--fs',      type=int, default=16,  help='font size')
    parser.add_argument('--size',    type=int, default=128, help='image size')
    args = parser.parse_args()

    if args.demo:
        datafile = f'{DIR}/data/demo.csv'
    else:
        datafile = f'{DIR}/data/data.csv'
    next_problem = load_data(datafile, randomize=True)

    root = tk.Tk()

    SCORE = tk.IntVar(value=0)
    TOTAL = tk.IntVar(value=0)
    COST = tk.IntVar(value=0)
    CORRECT = tk.BooleanVar(value=False)

    frames_outer = [tk.Frame(root) for i in range(2)]
    [frame.pack() for frame in frames_outer]

    problem_idx = tk.IntVar(value=0)
    title = tk.Label(frames_outer[0], '', fg="black", font=tkFont.Font(size=args.fs//16*28))
    title.pack()

    frames = [tk.Frame(frames_outer[1]) for i in range(3)]
    [frame.pack(side=tk.LEFT) for frame in frames]

    def reset_problem():

        if game_controls.image_rows is not None:
            score = SCORE.get()
            for row in game_controls.image_rows:
                for widget in row.image_widgets:
                    widget.on_click(None)
                    widget.on_click(None)
            if not game_controls.people_choice.correct.get():
                game_controls.people_choice.on_click(None)
            SCORE.set(score)
            var = tk.IntVar()
            root.after(args.timeout*1000, var.set, 1)
            root.wait_variable(var)

        try:
            (person1, person2), data_chunks, is_correct_order = next_problem()
            SCORE.set(100)
            COST.set(100/(sum(len(x) for x in data_chunks)*2))
            CORRECT.set(is_correct_order)
            for widgets in frames[0].winfo_children() + frames[1].winfo_children():
                widgets.destroy()
            people_choice = PeopleChoice(frames[0], (person1, person2), SCORE, CORRECT, image_size=(args.size, args.size))
            image_rows = [ImageRow(frames[1], chunk, SCORE, COST,
                                   image_size=(args.size, args.size), fs=args.fs) for chunk in data_chunks]
            problem_idx.set(problem_idx.get()+1)
            title_text = f'Problem #{problem_idx.get()}'
        except Exception as e:
            print(e)
            for widgets in frames_outer[1].winfo_children():
                widgets.destroy()
            title_text = f'Results: {TOTAL.get()} points'
            image_rows = None
        root.title(title_text)
        title.config(text=title_text)
        return image_rows, people_choice

    game_controls = GameControls(frames[2], SCORE, TOTAL, CORRECT, reset_problem, fs=args.fs)
    game_controls.image_rows, game_controls.people_choice = reset_problem()
    root.mainloop()


if __name__ == "__main__":
    main(sys.argv)
