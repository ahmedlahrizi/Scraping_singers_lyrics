# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#          A module to get counters of, must used words #
#          or nouns used by an Artist                   #
#          By:                                          #
#      Works with web scrapping from genius lyrics      #
#   Open-Source, but please use my name when using it   #
# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
"""
A self th an Artist class to get a counter for the must used words by the singer
"""

import requests
from collections import Counter
from pprint import pprint
import logging

from bs4 import BeautifulSoup
import spacy
from collections import Counter

# The code basically works in this shcheme : the only public method is get_most_used_words
# So when we call it it
# Ill do this and documentation later on


class Artist:

    def __init__(self, artist_id: int = 1128641, artist_name: str = "ICO", spacy_module: str = "en_core_news_sm"):
        """
        Initialisating the class
        Args:
            artist_id: An integer with the artist id on genius
            artist_name: The artist name, Just for logs
            spacy_module: The module that would be used with spacy.load()
        """
        # ASSIGNIATION OF INSTANCE ATTRIBUTES
        self.url = 'https://genius.com/api/artists/{artist_id}/songs?page={page_number}&sort=popularity' \
            .format(artist_id=artist_id, page_number="{page_number}")
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.spacy_module = spacy_module
        self.fetched_urls = Counter()
        # fetched_urls: A counter with every url and how much times we fetched lyrics on it (for debug)
        self.most_used_words = {}

    def __request_json(self, page_number: int = 1) -> dict:
        """
        Private method that returns the json dict using the self.url
        and the page_number
        Returns:
            object: A dict that has been got from the request.json
        """
        request = requests.get(self.url.format(page_number=page_number))
        request_json = request.json()
        safety_exit = 15
        while (request_json is None or request.status_code != 200) and safety_exit:
            # If The request.json returns None or the request failed whe do it again the safety_exit
            # We have a sefety exit that rescues us from an "INFINITE LOOP"
            request = requests.get(self.url.format(page_number=page_number))
            request_json = request.json()
            safety_exit -= 1
        # pprint(request_json)
        # print("Succesfully searched json dict with a request for {artist_name}, page {page_number}".
        #                  format(artist_name=self.artist_name, page_number=page_number))
        return request_json

    def __get_artist_songs_urls(self) -> list:
        """
        Returns: A list with all the songs that have the given Artist as "Primary Artist"
        """
        # Vars that would be used
        page_number = 1
        valid_urls = []
        safety_exit = 10
        got_all_songs = False

        while (not got_all_songs) or (not safety_exit):
            # Getting the json object of the request to know if it worked or not
            response = self.__request_json(page_number).get("response")
            songs = response.get("songs", [])

            for song in songs:
                if song.get("_type") == "song" and \
                        song.get("primary_artist", {}).get("id") == self.artist_id:
                    # If the primary artist is the given one and it's a song
                    valid_urls.append(song.get("url"))
                    song_title = song.get("full_title", "")
                    print("got this url {valid_urls}, song name is \"{song_title}\".".
                          format(valid_urls=valid_urls[-1], song_title=song_title))
            # Decreasing the safety exit
            safety_exit -= 1
            next_page = response.get("next_page")
            page_number = next_page
            got_all_songs += not next_page
            # if there is no next page that means we got all the song !!

        return valid_urls

    def __request_page_content(self, url):
        """
        Get the content from a genius page
        Args:
            url: string with url that the request will use

        Returns:
            object: The request and the number of time that the url was fetched in a list

        """
        # DOING THE REQUEST TO GET THE CONTENT
        self.fetched_urls = Counter(self.fetched_urls + Counter([url]))
        # The only way that i found to add something to a counter
        request = requests.get(url)
        safety_exit = 10
        while request.status_code != 200 or None is request.content or not safety_exit:
            request = request.get(url)
            self.fetched_urls = Counter(self.fetched_urls + Counter([url]))
            safety_exit -= 1
        # self.fetched_urls[url] corresponds to the number of times that the url was fetched
        return [request, self.fetched_urls[url]]

    def __extract_lyrics_from_url(self):
        """
        Calls request_page_content to get the content of the page and extract lyrics using Beautiful Soup
        Returns: A string with the lyrics in lowercase
        """
        fetched_lyrics_urls = []
        for url in self.__get_artist_songs_urls():
            request = self.__request_page_content(url)
            soup = BeautifulSoup(request[0].content, "html.parser")
            lyrics = soup.find("div", class_="lyrics")
            # Doing the request and checking if the div with the class lyrics is here
            safety_exit = 10
            while lyrics is None or not safety_exit:
                request = self.__request_page_content(url)
                soup = BeautifulSoup(request[0].content, "html.parser")
                lyrics = soup.find("div", class_="lyrics")
                safety_exit -= 1
            # stripped strings is an iterable with all the text that will be in the html code
            fetched_lyrics_urls.extend([i for i in lyrics.stripped_strings if "[" not in i or "]" not in i])
            # print(request[1])
            print("fetched lyrics {number_of_fetches} time{s}, {url}".
                  format(number_of_fetches=request[1], s="s" if request[1] > 1 else "", url=url))
        return " ".join(fetched_lyrics_urls).lower()

    def get_most_used_words(self):
        nlp = spacy.load(self.spacy_module)
        # Loading the language
        print("loaded spacy")
        doc = nlp(self.__extract_lyrics_from_url())
        # Tokenizing the lyrics
        print("loaded text in spacy")
        for token in doc:
            # .pos_ is there type like verb, noun...
            if token.pos_ not in self.most_used_words:
                self.most_used_words[token.pos_] = []
                # if there is no key for this pos_ we create one with a value of an empty list
            self.most_used_words[token.pos_].append(token.text)
            # Then we append to our list the text
        self.most_used_words = {key: Counter(value) for key, value in self.most_used_words.items()}
        # And when we are done we will replace lists with counters
        return self.most_used_words


ICO = Artist(29743, artist_name="Patrick Bruel", spacy_module="fr_core_news_sm")
ico_lyrics = ICO.get_most_used_words()
pprint(ico_lyrics)
