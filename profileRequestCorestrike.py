from shared_module import get_script_directory
from PIL import Image, ImageGrab
#5.3.1.20230401
from pytesseract import pytesseract
from pytesseract import Output
import aiohttp
import asyncio
import cv2 as cv
import os 
import pygetwindow as gw
import pyautogui
import numpy as np

script_dir = get_script_directory()
path_to_tesseract = os.path.join(script_dir, r"Tesseract-OCR/tesseract.exe")
rel_path = os.path.join(script_dir, "captures/Capture.png")
template_path = os.path.join(script_dir, "assets/template.png")
verified_path = os.path.join(script_dir, "assets/verified.png")

#make this not reliant on being tabbed in?
def is_target_image_present(target, num):
    #change confidence .8 for load screen
    #.3 for endgame
    if pyautogui.locateOnScreen(target, confidence=num):
        return True
    return False

def is_verified_present(img):
    #cover up the icon
    src = img
    template = cv.imread(verified_path,0)
    w, h = template.shape[::-1]

    res = cv.matchTemplate(src,template,cv.TM_CCOEFF_NORMED)
    threshold = 0.8
    loc = np.where( res >= threshold)
    for pt in zip(*loc[::-1]):
        cv.rectangle(src, pt, (pt[0] + w, pt[1] + h), (0,0,0), -1)

    return src
    
def process_img(img):
    #greyscale for readability
    grey_img = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    (thresh,final_img) = cv.threshold(grey_img, 127, 255, cv.THRESH_BINARY)
    final_img = cv.resize(final_img, None, fx=2, fy=2)
    final_img = cv.medianBlur(final_img, 5)
    final_img = is_verified_present(final_img)
    #show what ocr is seeing
    #cv.imshow('img', final_img)
    #cv.waitKey(0)
    return final_img

def take_ss(path):
    #print(gw.getAllTitles())

    window = gw.getWindowsWithTitle("OmegaStrikers  ")[0]
    left, top = window.topleft
    right, bottom = window.bottomright
    pyautogui.screenshot(path)
    im = Image.open(path)
    im = im.crop((left,top,right,bottom))
    im.save(path)

    img = cv.imread(path)

    return img

def get_info():
    #takes a picture automatically when the load screen is detected to be starting up
    img = take_ss(rel_path)

    #img.shape returns tuple of width and height (x, y, dimension)
    adjusted_height = float(img.shape[0]) * .08
    y=img.shape[0] - int(adjusted_height//1)
    x=0
    h=int((float(img.shape[0]) * .96)//1)
    w=int((float(img.shape[1]) * .99)//1)

    font = cv.FONT_HERSHEY_COMPLEX

    #this only works 2560 x 1440 atm
    #scale down template instead of doing this defining height and stuff?
    #print(img.shape[0], y, h)

    #0, 1.33%
    cv.rectangle(img,(0,y),(int((float(img.shape[1]) * .0133)//1),h),(0,0,0),-1)
    #.39%
    #cv.putText(img, '=', (int((float(img.shape[1]) * .004)//1),h - 20), font, 1, (255,255,255),3,cv.LINE_AA)
    #15.8%, 17.0%
    cv.rectangle(img,(int((float(img.shape[1]) * .158)//1),y),(int((float(img.shape[1]) * .17)//1),h),(0,0,0),-1)
    #15.8%
    #cv.putText(img, '=', (int((float(img.shape[1]) * .158)//1),h - 20), font, 1, (255,255,255),3,cv.LINE_AA)
    #31.6%, 33.0%
    cv.rectangle(img,(int((float(img.shape[1]) * .316)//1),y),(int((float(img.shape[1]) * .33)//1),h),(0,0,0),-1)
    #31.6%
    #cv.putText(img, '=', (int((float(img.shape[1]) * .316)//1),h - 20), font, 1, (255,255,255),3,cv.LINE_AA)
    #47.5%, 52.5%
    cv.rectangle(img,(int((float(img.shape[1]) * .475)//1),y),(int((float(img.shape[1]) * .525)//1),h),(0,0,0),-1)
    #47.5%
    #cv.putText(img, '=', (int((float(img.shape[1]) * .475)//1),h - 20), font, 1, (255,255,255),3,cv.LINE_AA)
    #67.0%, 68.4%
    cv.rectangle(img,(int((float(img.shape[1]) * .67)//1),y),(int((float(img.shape[1]) * .684)//1),h),(0,0,0),-1)
    #67.0%
    #cv.putText(img, '=', (int((float(img.shape[1]) * .67)//1),h - 20), font, 1, (255,255,255),3,cv.LINE_AA)
    #83.0%, 84.2%
    cv.rectangle(img,(int((float(img.shape[1]) * .83)//1),y),(int((float(img.shape[1]) * .842)//1),h),(0,0,0),-1)
    #83.0%
    #cv.putText(img, '=', (int((float(img.shape[1]) * .83)//1),h - 20), font, 1, (255,255,255),3,cv.LINE_AA)
    crop_img = img[y:h, x:x+w]
    #cv.imshow('a', crop_img)
    #k = cv.waitKey(0)
    dirty_names = [
        process_img(crop_img[5:img.shape[0], 0:(int((float(img.shape[1]) * .17)//1))]),
        process_img(crop_img[5:img.shape[0], (int((float(img.shape[1]) * .158)//1)):(int((float(img.shape[1]) * .33)//1))]),
        process_img(crop_img[5:img.shape[0], (int((float(img.shape[1]) * .316)//1)):(int((float(img.shape[1]) * .525)//1))]),
        process_img(crop_img[5:img.shape[0], (int((float(img.shape[1]) * .475)//1)):(int((float(img.shape[1]) * .684)//1))]),
        process_img(crop_img[5:img.shape[0], (int((float(img.shape[1]) * .67)//1)):(int((float(img.shape[1]) * .842)//1))]),
        process_img(crop_img[5:img.shape[0], (int((float(img.shape[1]) * .83)//1)):img.shape[1]])
    ]

    #use tesseract to read names
    pytesseract.tesseract_cmd = path_to_tesseract
    names = []
    for i in dirty_names:
        #lang = "noto" my trained data
        u = pytesseract.image_to_string(i, lang="Noto")
        #probably X?
        if u == "":
            u = "X"
        names.append(u.strip("\n"))
    """   
    #filter out empty list entries
    dirty_names = list(filter(lambda x: len(x) > 0, text.split('\n')))
    #print("dirty", dirty_names)
    names = dirty_names[0].split("=")

    valid_sp_chars = set([".", "-", "_", " "])

    for i in range(len(names)):
        for character in names[i]:
            if character not in valid_sp_chars and not character.isalnum():
                names[i] = character.replace(character, "")
            names[i] = names[i].strip()
    """
    print(names)
    return names

#if its a set of characters not covered by my language need to direct it to somewhere else 

#gets data of a specific player
async def get_corestrike_data(session, name):
    if name != "X":
        try:
            url = "https://corestrike.gg/lookup/" + name + "?region=Global&json=true"
            async with session.get(url) as response:
                return await response.json()
        except:
            print(f"An error occurred for name {name}")
            return None
    #x giving it to me even in code
    else:
        url = "https://corestrike.gg/lookup/Juno?region=Global&json=true"
        async with session.get(url) as response:
            return await response.json()
                    
    
#calls corestrike for all players in the match asynchronously
#fail condition if the profile doesnt exist
async def call_corestrike():
    names = get_info()
    user = {}
    async with aiohttp.ClientSession() as session:
        tasks = [get_corestrike_data(session, name) for name in names]
        result = await asyncio.gather(*tasks)
    #after we have all their data put it in our dict to be used by main
    for i in range(len(names)):
        try:
            if result[i]["rankedStats"]["is_ranked"]:
                user[names[i]] = result[i]["rankedStats"]
            else:
                #dummy data if not ranked
                print(names[i],"COULD NOT FIND PLAYER PROFILE - POSSIBLY NOT IN TOP 10k")
                user[names[i]] = {'createdAt': '0', 'rating': 0, 'wins': 0, 'losses': 0, 'games': 0}
        except:
            #profile url is invalid
            print(names[i],"COULD NOT FIND PLAYER PROFILE - POSSIBLY NOT IN TOP 10k")
            user[names[i]] = {'createdAt': '0', 'rating': 0, 'wins': 0, 'losses': 0, 'games': 0}
    print("done processing")
    return user, names

if __name__=="__main__":
    user = asyncio.run(call_corestrike())
    print(user)