# # # # # # # # # # # # # # # # # # # # # # # # # # # # #
#          A module to get counters of, must used words #
#          or nouns used by an Artist                   #
#          By: LAHRIZI Ahmed                            #
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


# The code basically works in this shcheme : the only public method is get_most_used_words
# So when we call it it
# Ill do this and documentation later on


class Artist:
    request_header = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like"
                      " Gecko) Chrome/83.0.4103.97 Safari/537.36"
    }

    def __init__(self, artist_id: int = 1128641, artist_name: str = "ICO", spacy_module: str = "en_core_news_sm"):
        """
        Initialisating the class
        Args:
            artist_id: An integer with the artist id on genius
            artist_name: The artist name, Just for logs
            spacy_module: The module that would be used with spacy.load()
        """
        # ASSIGNIATION OF INSTANCE ATTRIBUTES
        try:
            self.url = f'https://genius.com/api/artists/{artist_id}/songs?page={"{page_number}"}&sort=popularity' \
                .format(artist_id=artist_id, page_number="{page_number}")
            self.artist_id = artist_id
            self.artist_name = artist_name
            self.spacy_module = spacy_module
            self.fetched_urls = Counter()
            self.lyrics_nlp = self.__most_used_words_nlp
        except:
            pass
        # fetched_urls: A counter with every url and how much times we fetched lyrics on it (for debug)

    def __request_json(self, page_number: int = 1) -> dict:
        """
        Private method that returns the json dict using the self.url
        and the page_number
        Returns:
            object: A dict that has been got from the request.json
        """
        try:
            request = requests.get(self.url.format(page_number=page_number), headers=Artist.request_header)
            request_json = request.json()
            safety_exit = 15
            while (request_json is None or request.status_code != 200) and safety_exit:
                # If The request.json returns None or the request failed whe do it again the safety_exit
                # We have a sefety exit that rescues us from an "INFINITE LOOP"
                request = requests.get(self.url.format(page_number=page_number), headers=Artist.request_header)
                request_json = request.json()
                safety_exit -= 1
            # pprint(request_json)
            print(f"Succesfully searched json dict with a request for {self.artist_name}, page {str(page_number)}")
            return request_json
        except:
            return {}

    def __get_artist_songs_urls(self) -> list:
        """
        Returns: A list with all the songs that have the given Artist as "Primary Artist"
        """
        try:
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
            print(len(valid_urls))
            return valid_urls
        except:
            return []

    def __request_page_content(self, url):
        """
        Get the content from a genius page
        Args:
            url: string with url that the request will use

        Returns:
            object: The request and the number of time that the url was fetched in a list

        """
        # DOING THE REQUEST TO GET THE CONTENT
        try:
            self.fetched_urls = Counter(self.fetched_urls + Counter([url]))
            # The only way that i found to add something to a counter
            request = requests.get(url, headers=Artist.request_header)
            safety_exit = 10
            while request.status_code != 200 or None is request.content or not safety_exit:
                request = request.get(url)
                self.fetched_urls = Counter(self.fetched_urls + Counter([url]))
                safety_exit -= 1
            # self.fetched_urls[url] corresponds to the number of times that the url was fetched
            return [request, self.fetched_urls[url]]
        except:
            return ["", 0]

    def __extract_lyrics_from_url(self):
        """
        Calls request_page_content to get the content of the page and extract lyrics using Beautiful Soup
        Returns: A string with the lyrics in lowercase
        """
        try:
            fetched_lyrics_urls = []
            for url in self.__get_artist_songs_urls()[:5]:
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
        except:
            return ""

    @property
    def __most_used_words_nlp(self):
        try:
            nlp = spacy.load(self.spacy_module)
            # Loading the language
            print("loaded spacy module")
            return nlp(self.__extract_lyrics_from_url())  # Tokenizing the lyrics
        except:
            return {}

    @staticmethod
    def __str_from_token(token):  # Reduce token to its lowercase lemma form
        try:
            return token.lemma_.strip(" ,.()").lower()
        except:
            return "False"

    @staticmethod
    def __is_valid_token(token):
        return bool(
            token
            and __str_from_token(token)
            and not token.is_stop
            and not token.is_punct
            and not token.is_null
            and not token.is_space
        )

    def extract_lyrics(self, mode="l"):
        try:
            if mode == "l":
                return Counter([token for token in self.__most_used_words_nlp if Artist.__is_valid_token(token)])
            elif mode in ["c", "d"]:
                most_used_words = {}
                for token in self.lyrics_nlp:
                    if __is_valid_token(token):
                        if token in most_used_words:
                            most_used_words[token.pos_ if mode == "c" else token.tag] = Counter()
                        most_used_words[token.pos_ if mode == "c" else token.tag] += (Artist.__str_from_token(token))
                return most_used_words
            elif mode == "cd":
                pass
        except Exception as e:
            print(e)
            return ""

    @classmethod
    def patrick_bruel(cls, spacy_module: str = "fr_core_news_sm") -> tuple:
        return 29743, "Patrick Bruel", spacy_module


ICO = Artist(1128641, "Patrick Bruel", "fr_core_news_sm")
a = ICO.extract_lyrics("l")
pprint(a)
