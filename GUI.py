"""
 Main script for sorting images in a folder into subfolders. This script launches a GUI which displays
 one image after the other and lets the user vote for different given labels from a list given as input to the
 script.
 USAGE:
 python sort_folder.py --folder <INPUT-FOLDER> --labels <INPUT-LABEL1> <INPUT-LABEL2> ...
 Author: Christian Baumgartner (c.baumgartner@imperial.ac.uk)
 Date: 31. Jan 2016
"""

import argparse
import tkinter as tk
import os
import time
from shutil import copyfile, move
from tkinter import messagebox
import tkinter.font as font
from PIL import ImageTk, Image
categ = {
    "0": 0,
    "cây đổ": 1,
    "hỏa hoạn": 2,
    "ngập lụt": 3,
    "đường xấu": 4,
    "kẹt xe": 5,
    "rác thải": 6,
    "tai nạn": 7
}
class ImageGui:
    """
    GUI for iFind1 image sorting. This draws the GUI and handles all the events.
    Useful, for sorting views into sub views or for removing outliers from the data.
    """

    def __init__(self, master, labels, paths, res_file):
        """
        Initialise GUI
        :param master: The parent window
        :param labels: A list of labels that are associated with the images
        :param paths: A list of file paths to images
        :return:
        """

        # So we can quit the window from within the functions
        self.master = master
        #master.geometry("800x600")
        # Extract the frame so we can draw stuff on it
        frame = tk.Frame(master)

        # Initialise grid
        frame.grid()


        # Start at the first file name
        self.index = 0
        self.paths = paths
        self.labels = labels
        self.res_file = res_file

        # Number of labels and paths
        self.n_labels = len(labels)
        self.n_paths = len(paths)

        # Set empty image container
        self.image_raw = None
        self.image = None
        self.image_panel = tk.Label(frame)

        # set image container to first image
        self.set_image(paths[self.index])

        # Make buttons
        self.buttons = []
        for label in labels:
            self.buttons.append(
                    tk.Button(frame, text=label, width=10, height=5, command=lambda l=label: self.vote(l), bg="green", font=font.Font(weight="bold"))
            )

        # Add progress label
        progress_string = "%d/%d" % (self.index, self.n_paths)
        self.progress_label = tk.Label(frame, text=progress_string, width=10)

        # Place buttons in grid
        for ll, button in enumerate(self.buttons):
            button.grid(row=3, column=ll, padx=5, pady=20)
            #frame.grid_columnconfigure(ll, weight=1)

        # Place progress label in grid
        self.progress_label.grid(row=3, column=self.n_labels, sticky='we')

        # Place the image in grid
        self.image_panel.grid(row=1, column=0, columnspan=self.n_labels+11, sticky='we')

        # key bindings (so number pad can be used as shortcut)
        for key in range(self.n_labels):
            master.bind(str(key+1), self.vote_key)

    def show_next_image(self):
        """
        Displays the next image in the paths list and updates the progress display
        """
        self.index += 1
        progress_string = "%d/%d" % (self.index, self.n_paths)
        self.progress_label.configure(text=progress_string)

        if self.index < self.n_paths:
            self.set_image(self.paths[self.index])
        else:
            self.master.quit()

    def set_image(self, path):
        """
        Helper function which sets a new image in the image view
        :param path: path to that image
        """
        image = self._load_image(path)
        self.image_raw = image
        self.image = ImageTk.PhotoImage(image)
        self.image_panel.configure(image=self.image)

    def vote(self, label):
        """
        Processes a vote for a label: Initiates the file copying and shows the next image
        :param label: The label that the user voted for
        """
        input_path = self.paths[self.index]
        # self._copy_image(input_path, label)
        self._write_result(input_path, label, res_file)
        self.show_next_image()

    def vote_key(self, event):
        """
        Processes voting via the number key bindings.
        :param event: The event contains information about which key was pressed
        """
        pressed_key = int(event.char)
        label = self.labels[pressed_key-1]
        self.vote(label)

    @staticmethod
    def _load_image(path, size=(600,400)):
        """
        Loads and resizes an image from a given path using the Pillow library
        :param path: Path to image
        :param size: Size of display image
        :return: Resized image
        """
        image = Image.open(path)
        image = image.resize(size, Image.ANTIALIAS)
        return image

    @staticmethod
    def _copy_image(input_path, label):
        """
        Copies a file to a new label folder using the shutil library. The file will be copied into a
        subdirectory called label in the input folder.
        :param input_path: Path of the original image
        :param label: The label
        """
        root, file_name = os.path.split(input_path)
        output_path = os.path.join(root, label, file_name)
        # print " %s --> %s" % (file_name, label)
        copyfile(input_path, output_path)
    
    @staticmethod
    def _write_result(input_path, label, res_path):
        """
        Copies a file to a new label folder using the shutil library. The file will be copied into a
        subdirectory called label in the input folder.
        :param input_path: Path of the original image
        :param label: The label
        """
        
        f = open(res_path, "a")
        
        f.write("{}\t{}\n".format(input_path.split("/")[-1], categ[label]))
        f.close()

    @staticmethod
    def _move_image(input_path, label):
        """
        Moves a file to a new label folder using the shutil library. The file will be moved into a
        subdirectory called label in the input folder. This is an alternative to _copy_image, which is not
        yet used, function would need to be replaced above.
        :param input_path: Path of the original image
        :param label: The label
        """
        root, file_name = os.path.split(input_path)
        output_path = os.path.join(root, label, file_name)
        # print " %s --> %s" % (file_name, label)
        move(input_path, output_path)


def make_folder(directory):
    """
    Make folder if it doesn't already exist
    :param directory: The folder destination path
    """
    if not os.path.exists(directory):
        os.makedirs(directory)


# The main bit of the script only gets exectured if it is directly called
if __name__ == "__main__":

    # Make input arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--image_folder', help='test images', required=True)
    parser.add_argument('-p', '--predicted', help='text file contain predicted result', required=True)
    # parser.add_argument('-l', '--labels', nargs='+', help='Possible labels in the images', required=True)
    parser.add_argument('-r', '--result', help='result file to write', required=True)
    args = parser.parse_args()

    # grab input arguments from args structure
    input_folder = args.image_folder
    predicted_file = args.predicted
    labels = ["0", "cây đổ", "hỏa hoạn", "ngập lụt", "đường xấu", "kẹt xe", "rác thải", "tai nạn"]
    res_file = args.result
    
    # Make folder for the new labels
    # for label in labels:
    #     make_folder(os.path.join(input_folder, label))

    # Put all image file paths into a list
    f = open(predicted_file, "r")
    paths = []
    for file in f.readlines():
        file = file.rstrip()
        name = file.split(".")[1]
        name = name.lower()
        if name == "jpg" or name == "jpeg" or name == "png":
            path = os.path.join(input_folder, file)
            paths.append(path)
    # print(paths)
    # aaaaa
    # Start the GUI
    root = tk.Tk()
    # label = tk.Label(root, width=30)
    # label.pack(padx=20, pady=20)
    app = ImageGui(root, labels, paths, res_file)
    # countdown(3)
    root.mainloop()
