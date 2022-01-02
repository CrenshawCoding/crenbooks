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

        header_frame = tkinter.Frame(self.root)
        header_frame.grid(column=0, row=0)
        progress_frame = tkinter.Frame(self.root)
        progress_frame.grid(column=0, row=1)
        control_frame = tkinter.Frame(self.root)
        control_frame.grid(column=0, row=2)

        self.add_audiobook_button = tkinter.Button(header_frame, text='Buch laden',
                                                   command=self.add_audiobook_button_callback)
        self.current_book = tkinter.StringVar()
        self.current_book_label = tkinter.Label(header_frame, textvariable=self.current_book)
        self.play_button = tkinter.Button(control_frame, text='Play', command=self.play_button_callback)
        self.stop_button = tkinter.Button(control_frame, text='Stop', command=self.stop_button_callback)
        self.progress = tkinter.StringVar()
        self.progress_label = tkinter.Label(progress_frame, textvariable=self.progress)
        self.seek_entry = tkinter.Entry(control_frame)
        self.seek_entry.bind('<Return>', self.seek_entry_callback)
        self.seek_text = tkinter.StringVar().set('Seek:')
        self.seek_text_label = tkinter.Label(control_frame, textvariable=self.seek_text)
        self.forward_one_sec_button = tkinter.Button(progress_frame, command=self.forward_one_sec_callback, text='+1')
        self.forward_sixty_sec_button = tkinter.Button(progress_frame, command=self.forward_sixty_sec_callback,
                                                       text='+60')
        self.back_one_sec_button = tkinter.Button(progress_frame, command=self.back_one_sec_callback, text='-1')
        self.back_sixty_sec_button = tkinter.Button(progress_frame, command=self.back_sixty_sec_callback, text='-60')

        self.update_layout()
        self.player = Player.Player()
        if self.player.audio_file:
            self.current_book.set(DBManager.DBManager.get_book_id_from_path(self.player.audio_file))
        self.progress_updater = self.run_update_progress_thread()

    def play_button_callback(self):
        if self.player:
            self.player.play()

    def stop_button_callback(self):
        if self.player:
            self.player.stop()

    def add_audiobook_button_callback(self):
        book = filedialog.askopenfile(mode='r')
        self.player = Player.Player(book.name)
        self.current_book.set(DBManager.DBManager.get_book_id_from_path(self.player.audio_file))

    def update_layout(self):
        # Header:
        self.add_audiobook_button.grid(column=0, row=0)
        self.current_book_label.grid(column=1, row=0)

        # Control:
        self.play_button.grid(column=0, row=0)
        self.stop_button.grid(column=1, row=0)
        self.seek_text_label.grid(column=2, row=0)
        self.seek_entry.grid(column=3, row=0)

        # Progress Widgets:
        self.progress_label.grid(column=2, row=1)
        self.back_sixty_sec_button.grid(column=0, row=1)
        self.back_one_sec_button.grid(column=1, row=1)
        self.forward_one_sec_button.grid(column=3, row=1)
        self.forward_sixty_sec_button.grid(column=4, row=1)

    def run_update_progress_thread(self):
        t = Thread(target=self.update_progress, daemon=True)
        t.start()
        return t

    def update_progress(self):
        while True:
            if not self.player.stopped:
                self.progress.set(
                    '{0} | {1}'.format(time.strftime('%H:%M:%S', time.gmtime(self.player.get_current_progress())),
                                       time.strftime('%H:%M:%S', time.gmtime(self.player.update_file_duration()))))
            time.sleep(1)

    def seek_entry_callback(self, args):
        print('jumping to', self.seek_entry.get())
        self.player.seek(int(self.seek_entry.get()))

    def forward_one_sec_callback(self):
        self.player.seek(self.player.get_current_progress() + 1)

    def forward_sixty_sec_callback(self):
        self.player.seek(self.player.get_current_progress() + 60)

    def back_one_sec_callback(self):
        self.player.seek(self.player.get_current_progress() - 1)

    def back_sixty_sec_callback(self):
        self.player.seek(self.player.get_current_progress() - 60)

    @staticmethod
    def run():
        tkinter.mainloop()
