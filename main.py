import os
import PySimpleGUI as sg
import numpy as np
import pyrealsense2 as rs
import moviepy.editor as moviepy
import cv2

sg.theme("DarkTeal2")
layout = [[sg.T("")], [sg.Text("Choose a file: "), sg.Input(), sg.FileBrowse(key="-IN-")], [sg.Button("Submit")],
          [sg.Text(" ", size=(40, None), key="OUT")], ]

###Building Window
window = sg.Window('My File Browser', layout, size=(600, 150))

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == "Exit":
        break
    elif event == "Submit":
        string = values["-IN-"]
        window['OUT'].update("Processing...")
        window.refresh()

        fps = 30
        fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        vout = cv2.VideoWriter()

        try:

            config = rs.config()
            rs.config.enable_device_from_file(config, string, repeat_playback=False)
            pipeline = rs.pipeline()
            profile = pipeline.start(config)
            playback = profile.get_device().as_playback()  # get playback device
            playback.set_real_time(False)  # disable real-time playback
            frames = pipeline.wait_for_frames()
            frame = frames.get_color_frame()
            image = np.asanyarray(frame.get_data())

            vout.open('output.avi', fourcc, fps, (image.shape[1], image.shape[0]), True)

            while True:

                frame = frames.get_color_frame()
                image = np.asanyarray(frame.get_data())
                im_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                vout.write(im_rgb)
                try:
                    frames = pipeline.wait_for_frames()
                except:
                    break
        finally:
            pass
        vout.release()
        clip = moviepy.VideoFileClip("output.avi")
        s = string.split('.')
        clip.write_videofile("%s.mp4" % s[0])
        os.remove('output.avi')
        window['OUT'].update("Done")
