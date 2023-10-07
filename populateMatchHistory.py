from matchHistory import get_overview, get_stats
from shared_module import get_script_directory
from PIL import Image, ImageTk
import os
import tkinter as tk
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from ttkbootstrap.scrolled import ScrolledFrame

script_dir = get_script_directory()

class Match(tk.Button):
    def __init__(self, rank=None, lp=None, time=None, score=None, map=None, im1=None, im2=None):
        map_images = {
            "AHTEN CITY" : os.path.join(script_dir, "assets/maps/Ahten City.png"),
            "AIMI'S APP" : os.path.join(script_dir, "assets/maps/Ai.Mi_s App.png"),
            "ATLAS'S LAB" : os.path.join(script_dir,"assets/maps/Atlas_ Lab.png"),
            "DEMON DAIS" : os.path.join(script_dir, "assets/maps/Demon Dais.png"),
            "GATES OF OBSCURA" : os.path.join(script_dir, "assets/maps/Gates_of_Obscura.png"),
            "INKY'S SPLASH ZONE" : os.path.join(script_dir, "assets/maps/Inky_Splash_Zone.png"),
            "NIGHT MARKET" : os.path.join(script_dir, "assets/maps/Night Market.png"),
            "ONI VILLAGE" : os.path.join(script_dir, "assets/maps/Oni Village.png"),
        }
        if rank is None:
            self.rank = "Rookie"
            self.lp = "0"
            self.time = "0:00:00"
            self.score = "0-0"
            self.map = map_images["AHTEN CITY"]
            self.outcome = "Victory"
        else:
            self.rank = rank
            self.lp = lp
            self.time = time
            self.score = score
            self.map = map
            if score[0] > score[2]:
                self.outcome = "Victory"
            else:
                self.outcome = "Defeat"
            self.im1 = im1
            self.im2 = im2

    def on_enter(event, button, border):
        border.config(bg='white') 

    def on_leave(event, button, border):
        border.config(bg='#190831')  
    
    def photo(self):
        return ImageTk.PhotoImage(file = self.map)

    #TBD: add images of stuff
    def createButton(self, frame, x):
        s = ttk.Style()
        s.configure('my.TButton', background=s.colors.get("primary"), font=('Arial Bold', 25))
        button = tk.Button(frame, text=f"{self.outcome} | {self.time} | {self.map} | {self.score} | {self.rank} | {self.lp}", font=("Arial Bold", 25), command=lambda : open_images(self))
        button.grid(row=x, column=0, pady=5)
        frame.update()
        border = tk.Frame(frame, highlightbackground=s.colors.get("bg"),highlightthickness=2, width=button.winfo_width()+10,height=button.winfo_height()+10)
        border.grid(row=x, column=0, pady=5)
        button.lift()

        button.bind("<Enter>", lambda event: Match.on_enter(event, button, border))
        button.bind("<Leave>", lambda event: Match.on_leave(event, button, border))

def create_match(root, old=None, btntxt=None, ovlst=None, statslst=None):
    #if we click the match history button dont need to take screenshots
    #if old is none that means we are plugging in an old window to destroy - means we need to raise the flag to scan for stuff
    #else we dont need to look for any screenshots to take just display whatever is in the history rn
    if old != None:
        old.destroy()
        flag = True
    else:
        flag = False
    
    parent = ttk.Toplevel(root)
    parent.geometry("1280x720")
    parent.title("Match History")
    #add a label with some text to say match history
    text = ttk.Label(parent, text="Match History", font=("Arial Bold", 50))
    text.pack()
    #data has most recent match overview in it
    #parent contains the window w/ text packed at the top
    #needs frame below that holds buttons and frames packed in 
    
    container = ScrolledFrame(parent, autohide=False)
    container.pack(fill=BOTH, expand=YES, padx=10, pady=10)
    
    if btntxt == None:
        btntxt, ovlst = get_overview(flag)
        statslst = get_stats(flag)

    for i in range(len(btntxt)):
        button = Match(time=btntxt[i][0], map=btntxt[i][1], score=btntxt[i][2], rank=btntxt[i][3], lp=btntxt[i][4], im1=ovlst[i], im2=statslst[i])
        button.createButton(container, i)
    print("done creating buttons")
    return parent

def open_images(self):
    window = ttk.Toplevel()
    window.geometry("1280x720")
    window.title("Images")
    scroll = ScrolledFrame(window)
    scroll.pack(fill=BOTH, expand=YES, padx=10, pady=10)
    og1 = Image.open(self.im1)
    og2 = Image.open(self.im2)
    w1, h1 = og1.size
    w2, h2 = og2.size
    rsz1 = og1.resize((int(w1 * 0.4), int(h1 * 0.4)))
    rsz2 = og2.resize((int(w2 * 0.4), int(h2 * 0.4)))
    img1 = ImageTk.PhotoImage(rsz1)
    img2 = ImageTk.PhotoImage(rsz2)
    label1 = ttk.Label(scroll, image = img1)
    label1.image = img1
    label2 = ttk.Label(scroll, image = img2)
    label2.image = img2
    label1.pack()
    label2.pack()


if __name__=="__main__":
    main_root = ttk.Window()
    style = ttk.Style("vapor")
    main_root.geometry("1280x720")
    frame = create_match(main_root)
    main_root.mainloop()