import time
import tkinter
from threading import Thread
from tkinter import filedialog

import DBManager
import Player


class Display:
    def __init__(self):
        self.root = tkinter.Tk()
        # self.root.geometry('500x200')
        self.root.title("Crenbooks")
        self.add_audiobook_button = tkinter.Button(self.root, text='Buch laden',
                                                   command=self.add_audiobook_button_callback)
        self.play_button = tkinter.Button(self.root, text='Play', command=self.play_button_callback)
        self.stop_button = tkinter.Button(self.root, text='Stop', command=self.stop_button_callback)
        self.current_book = tkinter.StringVar()
        self.current_book_label = tkinter.Label(self.root, textvariable=self.current_book)
        self.progress = tkinter.StringVar()
        self.progress_label = tkinter.Label(self.root, textvariable=self.progress)
        self.seek_entry = tkinter.Entry(self.root)
        self.seek_entry.bind('<Return>', self.seek_entry_callback)
        self.update_layout()
        self.player = Player.Player()
        if self.player.audio_file:
            self.current_book.set(DBManager.DBManager.get_book_id_from_path(self.player.audio_file))
        self.run_update_progress_thread()

    def play_button_callback(self):
        if self.player:
            self.player.play()

    def stop_button_callback(self):
        if self.player:
            self.player.stop()

    def add_audiobook_button_callback(self):
        book = filedialog.askopenfile(mode='r')
        if book:
            self.player = Player.Player(book.name)
            self.current_book.set(DBManager.DBManager.get_book_id_from_path(self.player.audio_file))

    def update_layout(self):
        self.add_audiobook_button.grid(column=0, row=2)
        self.play_button.grid(column=1, row=2)
        self.stop_button.grid(column=2, row=2)
        self.current_book_label.grid(column=1, row=0)
        self.progress_label.grid(column=1, row=1)
        self.seek_entry.grid(column=1, row=3)

    def run_update_progress_thread(self):
        t = Thread(target=self.update_progress, daemon=True)
        t.start()

    def update_progress(self):
        while True:
            time.sleep(1)
            self.progress.set(
                '{0}|{1}'.format(time.strftime('%H:%M:%S', time.gmtime(self.player.get_current_progress())),
                                 time.strftime('%H:%M:%S', time.gmtime(self.player.update_file_duration()))))

    def seek_entry_callback(self, args):
        print('jumping to', self.seek_entry.get())
        self.player.seek(int(self.seek_entry.get()))

    @staticmethod
    def run():
        tkinter.mainloop()
