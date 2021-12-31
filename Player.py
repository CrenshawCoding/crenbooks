import subprocess
import time

import psutil
from threading import Thread
import DBManager
import re


class Player:
    def __init__(self, path=None):
        self.dbManager = DBManager.DBManager()
        self.playback_process = None
        self.audio_file = self.dbManager.currently_active_book_path
        if path:
            self.audio_file = path
        self.starttime = None
        self.initial_progress = 0
        self.current_progress = 0
        if self.audio_file:
            self.dbManager.load_book(self.audio_file)
            self.initial_progress = self.current_progress = self.dbManager.get_progress(self.audio_file)
        self.stopped = True
        self.file_duration = None
        self.updater = Thread(target=self.progress_updater).start()

    def play(self):
        if self.current_progress:
            self.playback_process = subprocess.Popen('ffplay -nodisp -v quiet -ss {0} {1}'.format(self.current_progress,
                                                                                                  self.audio_file))
        else:
            self.playback_process = subprocess.Popen('ffplay -nodisp -v quiet ' + self.audio_file)
        self.starttime = time.time()
        try:
            # WARNING: janky code to check if its actually playing
            time.sleep(0.06)
            psutil.Process(self.playback_process.pid)
        except psutil.NoSuchProcess:
            print('An error occured while trying to play the file: ' + self.audio_file + '\n' +
                  str(self.playback_process.stdout))
            return 1
        self.starttime = time.time()
        self.initial_progress = self.current_progress
        self.stopped = False
        return 0

    def stop(self):
        self.stopped = True
        self.playback_process.kill()
        self.dbManager.save_progress(self.audio_file, self.current_progress)

    # Updates the audiobook progress every <interval> seconds.
    def progress_updater(self, interval=1):
        while True:
            if not self.stopped:
                playtime = time.time() - self.starttime
                self.current_progress = playtime + float(self.initial_progress)
                self.dbManager.save_progress(self.audio_file, self.current_progress)
            time.sleep(interval)

    def update_file_duration(self):
        if self.audio_file:
            output = subprocess.run('ffprobe -i {0} -show_entries format=duration -v quiet -of csv="p=0"'
                                    .format(self.audio_file), capture_output=True).stdout
            m = re.search(r'(\d+)\.?', str(output))
            return float(m.group(1))

    def get_current_progress(self):
        if self.current_progress:
            return float(self.current_progress)
        else:
            return None

    def seek(self, seconds):
        if not self.stopped:
            self.stop()
        self.current_progress = seconds
        self.play()
