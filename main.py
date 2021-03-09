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

logging.basicConfig(level=logging.DEBUG,
                    # format="%(asctime)s %(name)-30s %(levelname)-8s %(message)s",
                    filename="./logs.log",
                    filemode="w")


class Artist:
    fetched_urls = Counter()

    def __init__(self, artist_id: int = 1128641, artist_name: str = "ICO", spacy_module: str = "en_core_news_sm"):
        # ASSIGNIATION OF INSTANCE ATTRIBUTES
        self.link = 'https://genius.com/api/artists/{artist_id}/songs?page={page_number}&sort=popularity' \
            .format(artist_id=artist_id, page_number="{page_number}")
        self.artist_id = artist_id
        self.artist_name = artist_name
        self.spacy_module = spacy_module
        self.most_used_words = {}

    def __request_dict(self, page_number) -> dict:
        # DOING THE REQUEST
        request = requests.get(self.link.format(page_number=page_number))
        request_dict = request.json()
        safety_exit = 10
        while (request_dict is None or request.status_code != 200) and safety_exit:
            request = requests.get(self.link.format(page_number=page_number))
            request_dict = request.json()
            # If The request
            safety_exit -= 1
        # pprint(request_dict)
        print("Requete effectué pour l'artiste {artist_name}, page {page_number}".
                         format(artist_name=self.artist_name, page_number=page_number))
        return request_dict

    def __get_artist_songs_urls(self) -> list:
        # Vars that would be used
        page_number = 1
        valid_urls = []
        safety_exit = 10
        got_all_songs = False

        while (not got_all_songs) or (not safety_exit):
            response = self.__request_dict(page_number).get("response")
            songs = response.get("songs", [])

            for song in songs:
                if song.get("_type") == "song" and \
                        song.get("primary_artist", {}).get("id") == self.artist_id:
                    valid_urls.append(song.get("url"))
                    song_title = song.get("full_title", "")
                    print("got this url {valid_urls}, song name is \"{song_title}\".".
                                     format(valid_urls=valid_urls[-1], song_title=song_title))

            safety_exit -= 1
            next_page = response.get("next_page")
            page_number = next_page
            got_all_songs += not next_page

        return valid_urls

    @staticmethod
    def __request_lyrics(url):
        # DOING THE REQUEST TO GET THE CONTENT
        Artist.fetched_urls = Counter(Artist.fetched_urls + Counter([url]))
        request = requests.get(url)
        safety_exit = 10
        while request.status_code != 200 or None is request.content or not safety_exit:
            request = request.get(url)
            Artist.fetched_urls = Counter(Artist.fetched_urls + Counter([url]))
            safety_exit -= 1
        return [request, Artist.fetched_urls[url]]

    def __extract_lyrics_from_url(self):
        fetched_lyrics = []
        for url in self.__get_artist_songs_urls():
            request = self.__request_lyrics(url)
            soup = BeautifulSoup(request[0].content, "html.parser")
            lyrics = soup.find("div", class_="lyrics")
            safety_exit = 10
            while lyrics is None or not safety_exit:
                request = self.__request_lyrics(url)
                soup = BeautifulSoup(request[0].content, "html.parser")
                lyrics = soup.find("div", class_="lyrics")
                safety_exit -= 1
            fetched_lyrics.extend([i for i in lyrics.stripped_strings if "[" not in i or "]" not in i])
            # print(request[1])
            print("fetched lyrics {number_of_fetches} time{s}, {url}".
                             format(number_of_fetches=request[1], s="s" if request[1] > 1 else "", url=url))
        return " ".join(fetched_lyrics).lower()

    def __translate_with_spacy(self):
        nlp = spacy.load(self.spacy_module)
        print("loaded spacy")
        doc = nlp(self.__extract_lyrics_from_url())
        print("loaded text in spacy")
        for token in doc:
            if token.pos_ not in self.most_used_words:
                self.most_used_words[token.pos_] = []
            self.most_used_words[token.pos_].append(token.text)
        self.most_used_words = {key: Counter(value).most_common(20) for key, value in self.most_used_words.items()}
        return self.most_used_words


ICO = Artist(29743, artist_name="Patrick Bruel", spacy_module="fr_core_news_sm")
# noinspection PyProtectedMember
# ico_song_urls = ICO._Artist__get_artist_songs_urls()
# pprint(ico_song_urls)
# print(len(ico_song_urls))
ico_lyrics = ICO._Artist__translate_with_spacy()
pprint(ico_lyrics)
