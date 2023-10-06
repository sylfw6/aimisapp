from profileRequestCorestrike import take_ss, path_to_tesseract
from shared_module import get_script_directory
from PIL import Image, ImageGrab
#5.3.1.20230401
from pytesseract import pytesseract
from pytesseract import Output
import cv2 as cv
import json
import os 
import pygetwindow as gw
import random
import numpy as np
import shutil
import string
import sys
import time

#take a screenshot when the game ends on the overview screen
#this ss has time elapsed, map, victory in top left
#top right has rank, above that increase or decrease in LP
#below rank name, new total lp

#take a screenshot when the stats screen is clicked
script_dir = get_script_directory()
overview = os.path.join(script_dir,"Captures/CaptureOverview.png")
stats = os.path.join(script_dir,"Captures/CaptureStats.png")
overview_template = os.path.join(script_dir,"assets/overview_template.png")
stats_template = os.path.join(script_dir,"assets/stats_template.png")
ENEMY_template = os.path.join(script_dir,"assets/ENEMY.png")
VICTORY_template = os.path.join(script_dir,"assets/VICTORY.png")
abs_matches = os.path.join(script_dir, "matches.txt")
abs_overview_photos = os.path.join(script_dir, "overviewPhotos.txt")
abs_stats_photos = os.path.join(script_dir, "statsPhotos.txt")

class Stack(list):
    def __init__(self=None):
        self = []

    def my_append(self, entry):
        self.append(entry)

    def push(self, entry):
        self.insert(0, entry)
    
    def check_stack(self):
        if len(self) > 20:
            tbd = self[20]
            self.pop()
            self.delete_file(tbd)
    
    def delete_file(self, file):
        if isinstance(file, str):
            os.remove(os.path.abspath(file))
            time.sleep(2)

    
#populate the stacks before we run any scripts so we can check length of stack and pop stuff later
overview_stack = Stack()
overview_photo_stack = Stack()
stats_stack = Stack()
#populate overview text
with open(abs_matches, "r") as file:
    for line in file:
        overview_stack.my_append(json.loads(line))
#populate overview file with reference to photo
with open(abs_overview_photos, "r") as file:
    for line in file:
        overview_photo_stack.my_append(json.loads(line))
#populate stats file with reference to photo
with open(abs_stats_photos, "r") as file:
    for line in file:
        stats_stack.my_append(json.loads(line))

ranks = [
    "Rookie",
    "Low Bronze",
    "Mid Bronze",
    "High Bronze",
    "Low Silver",
    "Mid Silver",
    "High Silver",
    "Low Gold",
    "Mid Gold",
    "High Gold",
    "Low Platinum",
    "Mid Platinum",
    "High Platinum",
    "Low Diamond",
    "Mid Diamond",
    "High Diamond",
    "Challenger",
    "Mid Challenger",
    "Omega",
    "Pro League"
]


def win_or_loss(img, template):
    src = img
    template = cv.imread(template,0)
    w, h = template.shape[::-1]

    res = cv.matchTemplate(src,template,cv.TM_CCOEFF_NORMED)
    threshold = 0.5
    #did we find what we were looking for?
    loc = np.where( res >= threshold)
    #if we did return image
    if len(loc[0]) > 0:
        for pt in zip(*loc[::-1]):
            cv.rectangle(src, pt, (pt[0] + w, pt[1] + h), (255,255,255), -1)
    #else we must have not found it - run it with other template to verify
    else:
        win_or_loss(img, VICTORY_template)
    return src

def process_image(img):
    grey_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    (thresh,final_img) = cv.threshold(grey_img, 127, 255, cv.THRESH_BINARY)
    final_img = cv.resize(final_img, None, fx=2, fy=2)
    final_img = cv.medianBlur(final_img, 5)
    return final_img

def img_to_str(img):
    pytesseract.tesseract_cmd = path_to_tesseract
    text = pytesseract.image_to_string(img)
    #filter out empty list entries
    dirty_text = list(filter(lambda x: len(x) > 0, text.split('\n')))

    return dirty_text


#overview always happens before stats page
#if the flag is up we dont need to capture any pictures, just populate the stacks 
def get_overview(flag=None):
    if flag:
        #take the ss of the overview screen
        #automatically click stats and click back to overview?
        print("overview ss")
        img = take_ss(overview)
        fn = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        #folder increases
        dest_folder = os.path.join(script_dir, "Captures/postgame/overview/")
        dest = shutil.copyfile(overview, os.path.join(dest_folder, fn + ".png"))

        #add photo to our stack
        overview_photo_stack.push(os.path.join(dest_folder, fn + ".png"))
        #if our stack is over 20 items long after that push, pop 21st
        overview_photo_stack.check_stack()

        y=int((float(img.shape[0]) * .15)//1)
        x=int((float(img.shape[1]) * .05)//1)
        h=int((float(img.shape[0]) * .5)//1)
        w=int((float(img.shape[1]) * .91)//1)
        left_half = img[y:h, x:int((float(img.shape[1]) * .255)//1)]
        right_half = img[y:h, int((float(img.shape[1]) * .83)//1):x+w]

        match_info = process_image(left_half)
        rank_info = process_image(right_half)

        match_info = win_or_loss(match_info, ENEMY_template)

        dirty_text = img_to_str(match_info)
        dirty_rank = img_to_str(rank_info)
        
        #this may not always work
        #clean up dirty_text to acquire match duration, map name, score
        temp = dirty_text[0]
        duration = temp[:7]
        map_name = temp[7:]
        score = dirty_text[1]

        map_name = [x for x in map_name if x.isalpha() or x == "'" or x.isspace()]
        score = [x for x in score if x.isdigit() or x == "-"]
        map_name = ''.join(map_name).strip()
        score = ''.join(score).strip()

        map_info = [duration, map_name, score]

        #this may not always work
        #clean up dirty_rank to get rank name, lp total

        clean_rank = []

        for entry in dirty_rank:
            if any(rank in entry or '/' in entry for rank in ranks):
                clean_rank.append(entry)

        if not clean_rank:
            clean_rank = ["Normal", ""]

        overview_info = map_info + clean_rank
            
        #add to stack
        overview_stack.push(overview_info)
        #if its too long pop last entry to make room for the newest one
        overview_stack.check_stack()
        with open(abs_matches, "w") as file:
            for game in overview_stack:
                file.write(json.dumps(game, separators=(',', ':')) + '\n')
        #save photo here
        with open(abs_overview_photos, "w") as file:
            for game in overview_photo_stack:
                file.write(json.dumps(game, separators=(',', ':')) + '\n')

        #need overview_info for button
        #we already have the screenshot of the current games info
    return overview_stack, overview_photo_stack
    

def get_stats(flag=None):
    if flag:
        #pull stats eventaully to avg out for metrics later
        print("stats ss")
        img = take_ss(stats)

        fn = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
        dest_folder = os.path.join(script_dir, "Captures/postgame/stats/")
        dest = shutil.copyfile(stats, os.path.join(dest_folder, fn + ".png"))

        #add photo to our stack
        stats_stack.push(os.path.join(dest_folder, fn + ".png"))
        #if we go over the limit pop the oldest one
        stats_stack.check_stack()

        y=int((float(img.shape[0]) * .23)//1)
        x=int((float(img.shape[1]) * .305)//1)
        h=int((float(img.shape[0]) * .76)//1)
        w=int((float(img.shape[1]) * .93)//1)
        crop_img = img[y:h, x:w]

        with open(abs_stats_photos, "w") as file:
            for game in stats_stack:
                file.write(json.dumps(game, separators=(',', ':')) + '\n')

        #returning screenshot of stats screen to attach to a button press
    return stats_stack

if __name__=="__main__":
    get_overview()
    get_stats()