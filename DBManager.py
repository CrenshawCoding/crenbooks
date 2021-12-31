import os
import csv
from tempfile import NamedTemporaryFile
import shutil


class DBManager:
    dev_mode = True

    def __init__(self):
        if not os.path.exists('./db/'):
            os.mkdir('./db/')
        if DBManager.dev_mode:
            self.library_path = './db/library_dev.csv'
            self.currently_active_book_directory = './db/current_book_dev.txt'
        else:
            self.library_path = './db/library.csv'
            self.currently_active_book_directory = './db/current_book.txt'
        self.currently_active_book_path = None
        self.fieldnames = ['ID', 'Path', 'Progress']
        if not os.path.exists(self.library_path):
            f = open(self.library_path, 'w', newline='')
            csv.DictWriter(f, fieldnames=self.fieldnames).writeheader()
        if os.path.exists(self.currently_active_book_directory):
            f = open(self.currently_active_book_directory, 'r')
            self.currently_active_book_path = f.read()
        else:
            f = open(self.currently_active_book_directory, 'w', newline='')

    def save_progress(self, book_id, progress):
        templib = NamedTemporaryFile(mode='w', delete=False, newline='')
        with open(self.library_path, 'r', encoding='utf8', newline='') as library, templib:
            reader = csv.DictReader(library, fieldnames=self.fieldnames)
            writer = csv.DictWriter(templib, fieldnames=self.fieldnames)
            for row in reader:
                if row['Path'] == str(book_id):
                    row['Progress'] = str(progress)
                writer.writerow(row)
            templib.close()
            library.close()
            shutil.move(templib.name, library.name)

    def load_book(self, path):
        if not self.book_exists(path):
            with open(self.library_path, 'a', encoding='utf8', newline='') as library:
                writer = csv.DictWriter(library, fieldnames=self.fieldnames)
                row = {'ID': ' '.join(os.path.basename(path).split('.')[:-1]), 'Path': path, 'Progress': '0'}
                writer.writerow(row)
        with open(self.currently_active_book_directory, 'w') as current_book:
            current_book.write(path)

    def book_exists(self, path):
        with open(self.library_path, 'r', encoding='utf8') as library:
            reader = csv.DictReader(library, delimiter=',', quotechar='|')
            for row in reader:
                if row['Path'] == str(path):
                    return True
        return False

    def get_progress(self, path):
        with open(self.library_path, 'r', encoding='utf8') as library:
            reader = csv.DictReader(library, delimiter=',', quotechar='|')
            for row in reader:
                if row['Path'] == str(path):
                    return row['Progress']

    @staticmethod
    def get_book_id_from_path(path):
        return ' '.join(os.path.basename(path).split('.')[:-1])
