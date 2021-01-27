import pyautogui
import time
import pandas as pd
from datetime import datetime
import webbrowser
import os
import sys
import timeit
from datetime import datetime
import csv
import configparser
import psutil

def main():

    config = configparser.ConfigParser()
    config.read('config.ini')

    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    print("Current Time =", current_time)

    """
    See config.ini
    """
    JOIN_X,JOIN_Y = config['ZOOM']['JOIN_X'], config['ZOOM']['JOIN_Y']
    SIGN_IN_TO_JOIN_REGION = list(map(int, config['ZOOM']['SIGN_IN_TO_JOIN_REGION'].split(", ")))
    HOST_HAS_ANOTHER_MEETING_REGION = list(map(int, config['ZOOM']['HOST_HAS_ANOTHER_MEETING_REGION'].split(", ")))
    WAITING_FOR_THE_HOST_REGION = list(map(int, config['ZOOM']['WAITING_FOR_THE_HOST_REGION'].split(", ")))
    ENTER_MEETING_PASSWORD_REGION = list(map(int, config['ZOOM']['ENTER_MEETING_PASSWORD_REGION'].split(", ")))
    JOIN_WITH_VIDEO_REGION = list(map(int, config['ZOOM']['JOIN_WITH_VIDEO_REGION'].split(", ")))
    MEETING_ID_IS_NOT_VALID_REGION = list(map(int, config['ZOOM']['MEETING_ID_IS_NOT_VALID_REGION'].split(", ")))
    LEAVE_MEETING_REGION = list(map(int, config['ZOOM']['MEETING_ID_IS_NOT_VALID_REGION'].split(", ")))

    pyautogui.PAUSE = 1

    def get_meeting_status(password):

        if pyautogui.locateOnScreen('waiting_for_the_host_to_start_this_meeting.png',region=WAITING_FOR_THE_HOST_REGION):
            return 'Valid - meeting accessed'
        elif pyautogui.locateOnScreen('enter_meeting_password.png',region=ENTER_MEETING_PASSWORD_REGION):
            if password:
                time.sleep(2)
                pyautogui.typewrite(password+'\t')
                pyautogui.click(JOIN_X,JOIN_Y)
                if pyautogui.locateOnScreen('waiting_for_the_host_to_start_this_meeting.png',region=WAITING_FOR_THE_HOST_REGION):
                    return 'Valid - Password supplied and works'
                else:
                    return 'Invalid - Password supplied but is wrong'
            else:
                return 'Invalid - Password required but not provided'
        elif pyautogui.locateOnScreen('join_with_video.png',region=JOIN_WITH_VIDEO_REGION):
            return 'Valid - meeting accessed'
        elif pyautogui.locateOnScreen('the_host_has_another_meeting.png',region=HOST_HAS_ANOTHER_MEETING_REGION):
            return 'Valid - the host has another meeting running'
        elif pyautogui.locateOnScreen('sign_in_to_join.png',region=SIGN_IN_TO_JOIN_REGION):
            return 'Invalid - requires sign in to zoom'
        elif pyautogui.locateOnScreen('this_meeting_is_not_valid.png',region=MEETING_ID_IS_NOT_VALID_REGION):
            return 'Invalid - link not valid'
        elif pyautogui.locateOnScreen('leave.png',region=LEAVE_MEETING_REGION):
            return 'Valid - meeting opened'
        else:
            return 'Unknown status - needs a human eyeball'


    def open_meeting_and_return_status(id,title,day,link,email,password):
        browser = config['DEFAULT']['WebBrowserPath'] + " %s"
        webbrowser.get(browser).open(link)
        time.sleep(4)
        meeting_status = get_meeting_status(password)
        df.loc[df['id'] == id,'meeting_status'] = meeting_status
        for proc in psutil.process_iter():
            if proc.name == config['DEFAULT']['ZoomExecutableName']:
                proc.kill()
        return meeting_status


    start = timeit.default_timer()
    df = pd.read_csv(config['DEFAULT']['MeetingsToCheck'])
    df['password'] = df.description.str.extract(r'([Pp]assword: \w\S*\S)', expand=False)
    df['password'] = df['password'].str.replace('password: ', '')
    df['password'] = df['password'].str.replace('Password: ', '')
    df['meeting_status'] = 'Unknown'
    df = df.fillna('')


    with open('meetings_with_status.csv', 'w') as csvfile:
             writer = csv.writer(csvfile)
             writer.writerow(['id','title','day','link','time','description','email','password','status'])
             for index, row in df.iterrows():
                id, title, day, link, start_time, description, email,password = row[0], row[1], row[2],\
                    row[3], row[4], row[5], row[6],row[7]
                status=open_meeting_and_return_status(id,title,day,link,email,password)
                writer.writerow([id, title, day, link, start_time, description, email,password,status])
                if index%50==0 and index>0:
                    for proc in psutil.process_iter():
                        if proc.name == config['DEFAULT']['WebBrowserName']:
                            proc.kill()

    stop = timeit.default_timer()
    total_time = stop - start
    mins, secs = divmod(total_time, 60)
    hours, mins = divmod(mins, 60)

    print ("Total running time: %d:%d:%d.\n" % (hours, mins, secs))

if __name__ == "__main__":
    main()
