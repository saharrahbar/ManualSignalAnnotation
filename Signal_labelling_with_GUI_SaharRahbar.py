import PySimpleGUI as sg
from tkinter import filedialog
from tkinter.filedialog import askdirectory
from tkinter.filedialog import asksaveasfile
import tkinter.messagebox
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.widgets import Cursor
import numpy as np
import pandas as pd
import os
import sys

fs = 2000 #sampling frequency


##function for liading data
def load_data():
    df = pd.read_csv(folder_name + '/' + fname)
    df_array = df.to_numpy()
    ppg = df_array[:, 1] #depends on data structure
    return [ppg]


##function for plotting the data and select a noisy part
def draw_plot(ppg, frame_length):
    time_idx = np.arange((i - 1) * frame_length * fs, i * frame_length * fs)
    value_frame = ppg[time_idx]
    time = np.array(time_idx) / fs
    y = value_frame
    x = time
    plt.rcParams["figure.figsize"] = [15.50, 7.50]
    plt.rcParams["figure.autolayout"] = True
    fig = plt.figure()
    ax = fig.subplots()
    ax.plot(x, y, color='b')
    ax.grid()
    cursor = Cursor(ax, horizOn=True, vertOn=True, useblit=True, color='r', linewidth=1)
    annot = ax.annotate("", xy=(0, 0), xytext=(-40, 40), textcoords="offset points",
                        bbox=dict(boxstyle='round4', fc='linen', ec='k', lw=1), arrowprops=dict(arrowstyle='-|>'))
    annot.set_visible(False)
    global coord
    coord = []
    def onclick(event):
        coord.append((event.xdata, event.ydata))
        x = event.xdata
        y = event.ydata
        annot.xy = (x, y)
        text = "({:.2g}, {:.2g})".format(x, y)
        annot.set_text(text)
        annot.set_visible(True)
        fig.canvas.draw()  # redraw the figure
        global x1
        [x1, y1] = zip(*coord) #in our case we don not need y1
        return [x1]

    fig.canvas.mpl_connect('button_press_event', onclick)
    plt.xlabel("time")
    plt.ylabel("amplitude")
    plt.show()
    plt.show(block=False)


#function for highlighting the selected part and create an output array (highlighted parts are unreliable)
def highlight(x1, Sig_label):
    f = 0
    plt.axvspan(x1[f], x1[f + 1], color='red', alpha=0.5)
    highlight_index = np.arange(fs * x1[f], fs * x1[f + 1], dtype=int)
    U = -1 * np.ones(len(highlight_index))
    for j in highlight_index:
        Sig_label[j] = -1
    return [U, Sig_label]


#function for saving the final array
def save(Sig_label, folder):
    np.savetxt(folder + '/' + fname, Sig_label, delimiter=',')
    return [Sig_label]


#getting the folder to save the result
sg.theme('LightGreen3') #change the color of window
root = tk.Tk()
root.withdraw()
folder_selected = filedialog.askdirectory()


##GUI loading data
if len(sys.argv) == 1:
    folder_name = sg.popup_get_folder('Select the folder of your data')
    filenames = os.listdir(folder_name + '/')
    sg.theme('LightGreen3')
    layout = [[sg.OptionMenu(filenames, default_value=filenames[2], key='number')], [sg.Button("Ok")]]

    # Create the Window
    window = sg.Window('Window Title', layout)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Cancel'):
            break
        if event == 'number':
            fname = print(event, values['number'])
        if event == 'Ok':
            if values['number']:
                sg.popup(f"The selected data is {values['number'][0]}")
                fname = values['number']
        window.close()
else:
    folder_name = sys.argv[1]


##Gui events
layout = [[sg.Button('Load Data'), sg.Button('Plot'), sg.Button('Highlight'),
           sg.Button('Next >', button_color=('white', 'springgreen4')),
           sg.Button('Previous <', button_color=('white', 'firebrick3')),
           sg.Button('Save'), sg.Button('Finish'), sg.Cancel()]]
window = sg.Window('PPG Matplotlib', layout)
while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Cancel'):
        break
    elif event == 'Load Data':
        [output] = load_data()
        Sig_label = np.ones(len(output))
        frame_len = 60 #the window lentgh of signal
    elif event == 'Plot':
        i = 1
        draw_plot(output, frame_len)
    elif event == 'Next >':
        plt.close()
        i = i + 1
        draw_plot(output, frame_len)
    elif event == 'Previous <':
        plt.close()
        i = i - 1
        draw_plot(output, frame_len)
    elif event == 'Save':
        save(Sig_label, folder_selected)
    elif event == 'Highlight':
        [U, Sig_label] = highlight(x1, Sig_label)
    elif event == 'Finish':
        break
window.close()


