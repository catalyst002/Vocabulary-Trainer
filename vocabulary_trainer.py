import pygame
import random
import requests
from lxml import html
import sqlite3
import os
import shutil
import dearpygui.dearpygui as dpg

# Improved code structure using classes and functions

class VocabularyTrainer:
    def __init__(self):
        self.conn = sqlite3.connect("database_copy.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.session_obj = requests.Session()
        self.word_now = ''
        self.translate_now = ''
        self.api_keys = ['a2a73e7b926c924fad7001ca3111acd55af2ffabf50eb4ae5', '0c21877a7d7e15ea2000c0f4ba50526e963b48813e952074d', '48dd829661f515d5abc0d03197a00582e888cc7da2484d5c7', 'a37e73a4bd8433196700600b3bc02651387e831fa6001426b', 'ac6099e63826b8650f05e22c4cc08baa2f21668e3f16176fd', 'tbg4mgdq7yh7hlnfnaz9odor7vecv30wrsdw4aas54fejyqnu', '2efe06dd56a60633b30010e4d970da03b55279db9896d7127', 'u1m1rcn6yqik1ti4wt0mb7ltqcz2gtp0xnbnacly5l05mgiis', 'c23b746d074135dc9500c0a61300a3cb7647e53ec2b9b658e', 'd92d8109432f0ead8000707303d0c6849e23be119a18df853',
             '1d3baf57f57254b5c430200e729037e9dea9d87493f3a16b4', '7rzrusqms9ysbvd11ihq7idgk3slkzghxnqc6k6rmn3520mq9', '9426b5f9c67e03853f5410a188e06bc4136900201e3fd92eb', '557bea420b5c3daf4d0030a71cc0817242db37d2bc14774a3', 'qxf7w45ra2s5xsmydv2j14hizdxvjattwuqygwye72nrw2l4z', 'f0c54bfe816e1c9cb917306c542021034d976d6be0d159c3c', 's6y8a8kihz6fvot3ai9eu0xajutwkmbttdax6cypgwsozo1nm', '279392f7343e9e50a825f216c6601ebab11ab52315dd5c600', 'xbqzmyi4pzgvhmmgqy9dy8ij3bhgcttk5hi6q88mu64ml2mhj', '13sbuiermi5tg6yuci6gdrza80r8bzr1kndgf29b142efkril']
        self.setup_ui()

    def setup_ui(self):
        dpg.create_context()

        with dpg.font_registry():
            with dpg.font("Monocraft.otf", 20, default_font=True, id="Default font"):
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)

        dpg.create_viewport()
        dpg.setup_dearpygui()
        dpg.bind_font("Default font")

        with dpg.window(tag="Primary Window"):
            with dpg.tab_bar():
                self.setup_new_words_tab()
                self.setup_repeat_words_tab()

        dpg.set_primary_window("Primary Window", True)

    def setup_new_words_tab(self):
        with dpg.tab(label="New Words"):
            dpg.add_text(default_value="", tag="word_now")
            dpg.add_text(default_value="", tag="word_translate")
            dpg.add_text(default_value="Word in context:")
            dpg.add_text(default_value="", tag="word_context1")
            dpg.add_text(default_value="", tag="word_context2")
            dpg.add_button(label="Next Word", callback=retrieve_callback, user_data=1,
                           width=140, height=111)
            dpg.add_same_line()
            dpg.add_button(label="Show Translate", callback=show_translate,
                           width=190, height=111)
            dpg.add_same_line()
            dpg.add_button(label="Play Sound",
                           callback=play_sound, width=140, height=111)
            dpg.add_same_line()
            dpg.add_button(label="Save Word", callback=save_word,
                           width=140, height=111)

    def setup_repeat_words_tab(self):
        with dpg.tab(label="Repeat Words"):
            dpg.add_text(default_value="", tag="word_now2")
            dpg.add_text(default_value="", tag="word_translate2")
            dpg.add_text(default_value="Word in context:")
            dpg.add_text(default_value="", tag="word_context12")
            dpg.add_text(default_value="", tag="word_context22")
            dpg.add_button(label="Next Word", callback=retrieve_callback, user_data=2,
                           width=140, height=111)
            dpg.add_same_line()
            dpg.add_button(label="Show Translate", callback=show_translate2,
                           width=190, height=111)
            dpg.add_same_line()
            dpg.add_button(label="Play Sound",
                           callback=play_sound, width=140, height=111)

    def show_translate(self, is_new_word=True):
        tag = 'word_translate' if is_new_word else 'word_translate2'
        dpg.set_value(tag, self.translate_now)

    def play_sound(self):
        # Select a random API key to use for the request.
        api_key = random.choice(self.api_keys)
        sound_file_url = f"https://api.wordnik.com/v4/word.json/{self.word_now}/audio?useCanonical=false&limit=50&api_key={api_key}"

        try:
            response = self.session_obj.get(sound_file_url)
            sound_data = response.json()
            if sound_data:
                sound_file_url = sound_data[0]['fileUrl']
                
                sound_response = self.session_obj.get(sound_file_url)
                sound_file_path = "file.mp3"
                
                with open(sound_file_path, "wb") as sound_file:
                    sound_file.write(sound_response.content)
                
                pygame.mixer.init()
                pygame.mixer.music.load(sound_file_path)
                pygame.mixer.music.play()
                
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                
                pygame.mixer.music.stop()
                pygame.mixer.quit()
                
                os.remove(sound_file_path)

        except Exception as e:
            print(f"Error playing sound: {e}")

    def fetch_word(self, is_new_word=True):

        table_name = "new_words" if is_new_word else "repeat_words"

        try:

            query = f"SELECT id, word, translate FROM {table_name} ORDER BY RANDOM() LIMIT 1"
            result = self.conn.execute(query).fetchone()

            if result:

                self.word_now, self.translate_now = result[1], result[2]

                delete_query = f"DELETE FROM {table_name} WHERE id = ?"
                self.conn.execute(delete_query, (result[0],))
                self.conn.commit()

                if is_new_word:
                    dpg.set_value('word_now', self.word_now)
                    dpg.set_value('word_translate', "")
                else:
                    dpg.set_value('word_now2', self.word_now)
                    dpg.set_value('word_translate2', "")

                self.fetch_context()

        except Exception as e:
            print(f"Error fetching word: {e}")

    

    def save_word(self):

        if not self.word_now:
            print("No word to save")
            return

        try:
            insert_query = "INSERT INTO repeat_words (word, translate) VALUES (?, ?)"
            self.conn.execute(insert_query, (self.word_now, self.translate_now))
            self.conn.commit()
            print(f"Word '{self.word_now}' saved for repetition.")
            self.word_now, self.translate_now = '', ''

        except Exception as e:
            print(f"Error saving word: {e}")


    def run(self):
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        self.conn.close()


def setup_database():
    shutil.copyfile("database.db", "database_copy.db")

if __name__ == "__main__":
    setup_database()
    app = VocabularyTrainer()
    app.run()
