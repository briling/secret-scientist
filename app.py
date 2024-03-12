import random
import numpy as np
import tkinter as tk
import tkinter.font as tkFont
from PIL import Image, ImageTk


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
    def __init__(self, master, data, SCORE,
                 label_text=None, data_dir='data', padding=(4,4)):
        self.frame = tk.Frame(master, bd=8, relief=tk.RIDGE)
        self.frame.pack(side=tk.TOP, padx=8*padding[0], pady=8*padding[1])
        if label_text is not None:
            self.label = tk.Label(self.frame, text=label_text, fg="black", font=tkFont.Font(size=16))
            self.label.pack()
        self.image_widgets = [ImageWidget(self.frame, f'{data_dir}/{path}', name.replace(' \\n ','\n'), SCORE)
                              for (name, path) in data]


class ImageWidget:
    def __init__(self, master, image_path, label_text, SCORE,
                 image_0_path='data/moon.png', image_size=(128,128), padding=(4,4)):

        self.photo_0 = ImageTk.PhotoImage(Image.open(image_0_path).resize(image_size))
        self.photo   = ImageTk.PhotoImage(image_resize(Image.open(image_path), image_size))
        self.label_text = label_text
        self.widget_state = 0
        self.score = SCORE
        self.image_size = image_size

        frame = tk.Frame(master)
        frame.pack(side=tk.LEFT, padx=padding[0], pady=padding[1])
        self.canvas = tk.Canvas(frame, width=image_size[0], height=image_size[1])
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_0)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.pack()
        self.label = tk.Label(frame, text="\n", fg="black", font=tkFont.Font(size=16))
        self.label.pack()


    def on_click(self, event):
        if self.widget_state<=1:
            if self.widget_state==0:
                redraw_canvas(self.canvas, self.photo)
            else:
                self.label.config(text=self.label_text)
            self.widget_state += 1
            new_score = self.score.get() - 1
            if new_score > 0:
                self.score.set(new_score)


class PeopleChoice:
    def __init__(self, master, image_paths, SCORE, CORRECT,
                 image_size=(128,128), padding=(4,4),
                 switch_pics=('data/switch_camera.png', 'data/switch_camera_red.png')):


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
    def __init__(self, master, SCORE, TOTAL, CORRECT, post_submit_hook, padding=(4,4)):
        self.score = SCORE
        self.total = TOTAL
        self.correct = CORRECT
        self.frame = tk.Frame(master)
        self.frame.pack(side=tk.TOP, padx=16*padding[0], pady=16*padding[1])
        label1 = tk.Label(self.frame, text='SCORE:', fg="black", font=tkFont.Font(size=28))
        self.label_score = tk.Label(self.frame, textvariable=SCORE, fg="black", font=tkFont.Font(size=32))
        label2 = tk.Label(self.frame, text='TOTAL:', fg="black", font=tkFont.Font(size=28))
        self.label_total = tk.Label(self.frame, textvariable=TOTAL, fg="black", font=tkFont.Font(size=32))
        label1.pack()
        self.label_score.pack()
        label2.pack()
        self.label_total.pack()

        self.post_submit_hook = post_submit_hook
        self.button = tk.Button(self.frame, text="SUBMIT", font=tkFont.Font(size=28), command=self.submit)
        self.button.pack()


    def submit(self):
        self.total.set(self.total.get() + (self.correct.get()*2-1)*self.score.get())
        self.label_total.config(fg=('green' if self.correct.get() else 'red'))
        self.post_submit_hook()


def load_data(data_path, randomize, people_dir='people'):

    raw_data = np.loadtxt(data_path, delimiter=',', dtype=str)

    by_presenter = {}
    for i, key in enumerate(raw_data[:,0]):
        if key not in by_presenter:
            by_presenter[key] = []
        by_presenter[key].append(raw_data[i,1:])
    for key, val in by_presenter.items():
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
        is_correct_order = random.choice([True, False])
        if not is_correct_order:
            p1, p2 = p2, p1
        return (presenters_pic[p1], presenters_pic[p2]), data_chunks, is_correct_order

    return next_problem


def main(datafile='data2.csv'):

    next_problem = load_data(datafile, randomize=True)

    root = tk.Tk()

    SCORE = tk.IntVar(value=0)
    TOTAL = tk.IntVar(value=0)
    CORRECT = tk.BooleanVar(value=False)

    frames_outer = [tk.Frame(root) for i in range(2)]
    [frame.pack() for frame in frames_outer]

    problem_idx = tk.IntVar(value=1)
    title = tk.Label(frames_outer[0], '', fg="black", font=tkFont.Font(size=28))
    title.pack()

    frames = [tk.Frame(frames_outer[1]) for i in range(3)]
    [frame.pack(side=tk.LEFT) for frame in frames]

    def reset_problem():
        root.title(f'Problem #{problem_idx.get()}')
        title.config(text=f'Problem #{problem_idx.get()}')
        (person1, person2), data_chunks, is_correct_order = next_problem()
        SCORE.set(sum(len(x) for x in data_chunks)*3)
        CORRECT.set(is_correct_order)
        for widgets in frames[0].winfo_children() + frames[1].winfo_children():
            widgets.destroy()
        PeopleChoice(frames[0], (person1, person2), SCORE, CORRECT)
        for i, chunk in enumerate(data_chunks):
            frame = ImageRow(frames[1], chunk, SCORE)
        problem_idx.set(problem_idx.get()+1)

    GameControls(frames[2], SCORE, TOTAL, CORRECT, reset_problem)
    reset_problem()
    root.mainloop()


if __name__ == "__main__":
    main()
