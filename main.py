from shared_module import get_script_directory
from profileRequestCorestrike import is_target_image_present, call_corestrike, template_path
from matchHistory import overview_template, stats_template, get_overview, get_stats
from populateMatchHistory import create_match
from itertools import count, cycle
from PIL import ImageTk
import asyncio
import math
import os
import PIL.Image
PIL.Image.CUBIC = PIL.Image.BICUBIC
import tkinter as tk
import ttkbootstrap as ttk
import threading
from ttkbootstrap.constants import *
#key: username
#value: dictionary with keys created at, rating, wins, losses, games
#from profileRequest import user, names 

script_dir = get_script_directory()
aimishock = os.path.join(script_dir, "assets/Shocked_Ai.Mi.png")
noted = os.path.join(script_dir, 'assets/Noted.gif')
gamercat = os.path.join(script_dir, 'assets/Sweaty_Gamer_Cat.gif')


#https://pythonprogramming.altervista.org/animate-gif-in-tkinter/?doing_wp_cron=1695952036.5726180076599121093750
class ImageLabel(tk.Label):
    """
    A Label that displays images, and plays them if they are gifs
    :im: A PIL Image instance or a string filename
    """
    def load(self, im):
        if isinstance(im, str):
            im = PIL.Image.open(im)
        frames = []
        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)
        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100
        if len(frames) == 1:
            self.config(image=next(self.frames))
        else:
            self.next_frame()
    def unload(self):
        self.config(image=None)
        self.frames = None
    def next_frame(self):
        if self.frames:
            self.config(image=next(self.frames))
            self.after(self.delay, self.next_frame)

def createMeter(user, window, name):
    #show ranked stats
    if name.strip() not in streamer_mode:
        try:
            wins = user["wins"]
            games = user["wins"] + user["losses"]
            wr = ttk.Meter(
            window,
            amountused=str(round(100*(wins/games), 1)),
            metersize=200,
            meterthickness=30,
            bootstyle=SUCCESS,
            textright="%",
            subtext="Winrate",
            )
        #if they are unranked show nothing
        except:
            wr = ttk.Meter(
            window,
            amountused=0,
            metersize=200,
            meterthickness=0,
            bootstyle=SUCCESS,
            subtext="Unranked/Not in top 10k",
            )
    else:
        wr = ttk.Label(window, text="User has streamer mode enabled", font=("Arial"))
    return wr

def round_down_to_nearest_100(num):
    res = math.floor(num / 100) * 100
    if res == 0:
        return 1000
    else:
        return res
    
#start button prompt
#scanning/loading screen
#info screen as a separate window
#reset scanning/loading screen to track next game

def title_screen():
    frame = ttk.Frame(root)
    subframe = ttk.Frame(frame)
    title = ttk.Label(frame, text="aimis app", font=("Arial Bold", 50))
    start = ttk.Button(subframe, text="scan for players", command = load_screen)
    scan_end = ttk.Button(subframe, text="scan for endgame", command = load_screen_endgame)
    history = ttk.Button(subframe, text="match history", command= lambda: create_match(root))
    
    ph = ImageTk.PhotoImage(PIL.Image.open(aimishock))
    label = ttk.Label(frame, image=ph)
    label.image=ph

    title.pack()
    start.grid(row=0, column=0, padx=1)
    scan_end.grid(row=0, column=1, padx=1)
    history.grid(row=0, column=2, padx=1)
    subframe.pack()
    label.pack()
    frame.place(relx=.5, rely=.5,anchor= CENTER)
    txt = ttk.Label(root, text="holy moly it was omega strikers companion", font=("Arial Bold", 40))
    txt.pack()

def load_screen_endgame():
    loading = tk.Toplevel(root)
    loading.title("scanning for end screen")
    waiting = ttk.Label(loading, text="scanning for end screen", font=("Arial Bold", 25))
    waiting.pack()
    load_gif = ImageLabel(loading)
    load_gif.pack()
    load_gif.load(noted)
    backend_thread = threading.Thread(target=scan_for_overview, args=(root, loading, waiting, load_gif))
    backend_thread.start()
    
def scan_for_overview(root, window, text, gif):
    if is_target_image_present(overview_template, .3):
        root.iconify()
        window.iconify()
        window.after(1000)
        btn, ov = get_overview(True)
        window.update()
        window.deiconify()
        window.wm_attributes("-topmost", True)
        text.config(text="Overview found - Searching for stats")
        gif.load(gamercat)
        scan_for_stats(root, window, text, gif, btn, ov)
    else:
        print("Searching for overview screen")
        window.after(1000, scan_for_overview(root, window, text, gif))
        root.update()

def scan_for_stats(root, window, text, gif, btn, ov):
    if is_target_image_present(stats_template, .3):
        root.iconify()
        window.iconify()
        window.after(1000)
        sts = get_stats(True)
        window.update()
        print("all stuff found")
        window.deiconify()
        window.wm_attributes("-topmost", True)
        text.config(text="Creating match history - Ai.Mi is working")
        root.deiconify()
        gif.load(gamercat)
        match_history(root, window, btn, ov, sts)
    else:
        print("Searching for stats screen")
        window.after(1000, scan_for_stats(root, window, text, gif, btn, ov))
        root.update()

#this gets done in another file its here for the sake of consistency
def match_history(root, old_window=None, btn=None, ov=None, sts=None):
    print("populating match window passively")
    create_match(root, old_window, btn, ov, sts)
    root.update_idletasks()
    root.update()
    print("done")

def load_screen():
    loading = ttk.Toplevel(root)
    loading.title("scanning for active match")
    waiting = ttk.Label(loading, text="scanning for active match", font=("Arial Bold", 50))
    waiting.pack()
    load_gif = ImageLabel(loading)
    load_gif.pack()
    load_gif.load(noted)
    backend_thread = threading.Thread(target=scan_for_loading, args=(loading,waiting, load_gif))
    backend_thread.daemon = True
    backend_thread.start()
    loading.mainloop()

def scan_for_loading(window, text, gif):
    if is_target_image_present(template_path, .8):
        text.config(text="Players found - Ai.Mi is working")
        window.wm_attributes("-topmost", True)
        window.wm_attributes("-topmost", False)
        gif.load(gamercat)
        window.update()
        match_found(window)
    else:
        print("Searching for loading screen")
        window.after(1000, scan_for_loading(window, text, gif))

def match_found(window):
    user, names = asyncio.run(call_corestrike())
    info_screen(user, names, window)

#holy shit spaghetti
def info_screen(user, names, old_window):
    old_window.destroy()
    match_stats = ttk.Toplevel(root)
    match_stats.title("Current match stats")
    #clear previous content on loading window and add new info
    p1name = ttk.Label(match_stats, text=names[0], font=("Arial", 25))
    p2name = ttk.Label(match_stats, text=names[1], font=("Arial", 25))
    p3name = ttk.Label(match_stats, text=names[2], font=("Arial", 25))
    p4name = ttk.Label(match_stats, text=names[3], font=("Arial", 25))
    p5name = ttk.Label(match_stats, text=names[4], font=("Arial", 25))
    p6name = ttk.Label(match_stats, text=names[5], font=("Arial", 25))
    title = ttk.Label(match_stats, text="holy moly its omega strikers", font=("Arial Bold", 50))

    match_stats.update()

    p1winrate = createMeter(user[names[0]], match_stats, names[0])
    p2winrate = createMeter(user[names[1]], match_stats, names[1])
    p3winrate = createMeter(user[names[2]], match_stats, names[2])
    p4winrate = createMeter(user[names[3]], match_stats, names[3])
    p5winrate = createMeter(user[names[4]], match_stats, names[4])
    p6winrate = createMeter(user[names[5]], match_stats, names[5])

    match_stats.update()

    p1wins = ttk.Label(match_stats, text="Wins: " + str(user[names[0]]["wins"]), font=("Arial", 25))
    p2wins = ttk.Label(match_stats, text="Wins: " + str(user[names[1]]["wins"]), font=("Arial", 25))
    p3wins = ttk.Label(match_stats, text="Wins: " + str(user[names[2]]["wins"]), font=("Arial", 25))
    p4wins = ttk.Label(match_stats, text="Wins: " + str(user[names[3]]["wins"]), font=("Arial", 25))
    p5wins = ttk.Label(match_stats, text="Wins: " + str(user[names[4]]["wins"]), font=("Arial", 25))
    p6wins = ttk.Label(match_stats, text="Wins: " + str(user[names[5]]["wins"]), font=("Arial", 25))

    match_stats.update()

    p1games = ttk.Label(match_stats, text="Games: " + str(user[names[0]]["wins"] + user[names[0]]["losses"]), font=("Arial", 25))
    p2games = ttk.Label(match_stats, text="Games: " + str(user[names[1]]["wins"] + user[names[1]]["losses"]), font=("Arial", 25))
    p3games = ttk.Label(match_stats, text="Games: " + str(user[names[2]]["wins"] + user[names[2]]["losses"]), font=("Arial", 25))
    p4games = ttk.Label(match_stats, text="Games: " + str(user[names[3]]["wins"] + user[names[3]]["losses"]), font=("Arial", 25))
    p5games = ttk.Label(match_stats, text="Games: " + str(user[names[4]]["wins"] + user[names[4]]["losses"]), font=("Arial", 25))
    p6games = ttk.Label(match_stats, text="Games: " + str(user[names[5]]["wins"] + user[names[5]]["losses"]), font=("Arial", 25))

    match_stats.update()

    p1rank = ttk.Label(match_stats, text="Rank: " + str(ranks[round_down_to_nearest_100(user[names[0]]["rating"])]), font=("Arial", 25))
    p2rank = ttk.Label(match_stats, text="Rank: " + str(ranks[round_down_to_nearest_100(user[names[1]]["rating"])]), font=("Arial", 25))
    p3rank = ttk.Label(match_stats, text="Rank: " + str(ranks[round_down_to_nearest_100(user[names[2]]["rating"])]), font=("Arial", 25))
    p4rank = ttk.Label(match_stats, text="Rank: " + str(ranks[round_down_to_nearest_100(user[names[3]]["rating"])]), font=("Arial", 25))
    p5rank = ttk.Label(match_stats, text="Rank: " + str(ranks[round_down_to_nearest_100(user[names[4]]["rating"])]), font=("Arial", 25))
    p6rank = ttk.Label(match_stats, text="Rank: " + str(ranks[round_down_to_nearest_100(user[names[5]]["rating"])]), font=("Arial", 25))

    match_stats.update()

    p1rating = ttk.Label(match_stats, text="Rating: " + str(user[names[0]]["rating"]), font=("Arial", 25))
    p2rating = ttk.Label(match_stats, text="Rating: " + str(user[names[1]]["rating"]), font=("Arial", 25))
    p3rating = ttk.Label(match_stats, text="Rating: " + str(user[names[2]]["rating"]), font=("Arial", 25))
    p4rating = ttk.Label(match_stats, text="Rating: " + str(user[names[3]]["rating"]), font=("Arial", 25))
    p5rating = ttk.Label(match_stats, text="Rating: " + str(user[names[4]]["rating"]), font=("Arial", 25))
    p6rating = ttk.Label(match_stats, text="Rating: " + str(user[names[5]]["rating"]), font=("Arial", 25))

    match_stats.update()

    title.grid(row=1,column=2,padx=10,pady=10,columnspan=4,sticky=tk.W+tk.E)
    p1name.grid(row=2,column=1,padx=10,pady=10)
    p2name.grid(row=2,column=2,padx=10,pady=10)
    p3name.grid(row=2,column=3,padx=10,pady=10)
    p4name.grid(row=2,column=4,padx=10,pady=10)
    p5name.grid(row=2,column=5,padx=10,pady=10)
    p6name.grid(row=2,column=6,padx=10,pady=10)
    match_stats.update()

    p1winrate.grid(row=3,column=1,padx=10,pady=5)
    p2winrate.grid(row=3,column=2,padx=10,pady=5)
    p3winrate.grid(row=3,column=3,padx=10,pady=5)
    p4winrate.grid(row=3,column=4,padx=10,pady=5)
    p5winrate.grid(row=3,column=5,padx=10,pady=5)
    p6winrate.grid(row=3,column=6,padx=10,pady=5)
    match_stats.update()

    p1wins.grid(row=4,column=1,padx=10,pady=5)
    p2wins.grid(row=4,column=2,padx=10,pady=5)
    p3wins.grid(row=4,column=3,padx=10,pady=5)
    p4wins.grid(row=4,column=4,padx=10,pady=5)
    p5wins.grid(row=4,column=5,padx=10,pady=5)
    p6wins.grid(row=4,column=6,padx=10,pady=5)
    match_stats.update()

    p1games.grid(row=5,column=1,padx=10,pady=5)
    p2games.grid(row=5,column=2,padx=10,pady=5)
    p3games.grid(row=5,column=3,padx=10,pady=5)
    p4games.grid(row=5,column=4,padx=10,pady=5)
    p5games.grid(row=5,column=5,padx=10,pady=5)
    p6games.grid(row=5,column=6,padx=10,pady=5)
    match_stats.update()

    p1rank.grid(row=6,column=1,padx=10,pady=5)
    p2rank.grid(row=6,column=2,padx=10,pady=5)
    p3rank.grid(row=6,column=3,padx=10,pady=5)
    p4rank.grid(row=6,column=4,padx=10,pady=5)
    p5rank.grid(row=6,column=5,padx=10,pady=5)
    p6rank.grid(row=6,column=6,padx=10,pady=5)
    match_stats.update()

    p1rating.grid(row=7,column=1,padx=10,pady=5)
    p2rating.grid(row=7,column=2,padx=10,pady=5)
    p3rating.grid(row=7,column=3,padx=10,pady=5)
    p4rating.grid(row=7,column=4,padx=10,pady=5)
    p5rating.grid(row=7,column=5,padx=10,pady=5)
    p6rating.grid(row=7,column=6,padx=10,pady=5)
    match_stats.update()

if __name__=="__main__":
    root = ttk.Window(title="aimis app", iconphoto=os.path.join(script_dir, "assets/aimiphone.png"))
    style = ttk.Style("vapor")
    root.geometry("1280x720")

    ranks = {
    1000: "Rookie",
    1100: "Low Bronze",
    1200: "Mid Bronze",
    1300: "High Bronze",
    1400: "Low Silver",
    1500: "Mid Silver",
    1600: "High Silver",
    1700: "Low Gold",
    1800: "Mid Gold",
    1900: "High Gold",
    2000: "Low Platinum",
    2100: "Mid Platinum",
    2200: "High Platinum",
    2300: "Low Diamond",
    2400: "Mid Diamond",
    2500: "High Diamond",
    2600: "Challenger",
    2700: "Mid Challenger",
    2800: "Omega",
    2800: "Pro League"
    }

    streamer_mode = [
        "Ai.Mi",
        "Asher",
        "Atlas",
        "Drek'ar",
        "Dubu",
        "Era",
        "Estelle",
        "Finii",
        "Juliette",
        "Juno",
        "Kai",
        "Kazan",
        "Luna",
        "Octavia",
        "Rasmus",
        "Rune",
        "Vyce",
        "X",
        "Zentaro"
    ]

    print("starting app")
    title_screen()
    root.mainloop()

