from enum import Enum

DEFAULT_PROMPTS = {"Viking":
                       "art by artgerm and greg rutkowski and charlie bowater and magali villeneuve and alphonse mucha",
                   "Paladin":
                       "art by wlop, greg rutkowski, thierry doizon, charlie bowater, alphonse mucha",
                   "Hobbit":
                       "art by John Howe, Alan Lee, and Weta Workshop",
                   "Harry Potter":
                       "art by jim kay, charlie bowater, alphonse mucha, ronald brenzell",
                   "Elf":
                       "art by wlop, Greg Rutkowski",
                   "Soccer":
                       "art by ross tran, charlie bowater, ignacio fernandez rios, kai carpenter, leesha hannigan, thierry doizon",
                   "Aikido":
                       "art by ross tran, charlie bowater, ignacio fernandez rios, kai carpenter, leesha hannigan, thierry doizon",
                   "Clown":
                       "art by wlop, greg rutkowski, charlie bowater, magali villeneuve, alphonse mucha",
                   "Jedi":
                       "art by marko djurdjevic, greg rutkowski, wlop, fredperry, rossdraws",
                   "Wizard":
                       "art by wlop, greg rutkowski, charlie bowater, magali villeneuve, alphonse mucha, surreal",
                   "Cyberpunk":
                       "art by wlop, greg rutkowski, and charlie bowater",
                   "Astronaut":
                       "art by alphonse mucha, ryan kittleson, greg rutkowski, leesha hannigan, stephan martiniere, stanley artgerm lau",
                   "Samurai":
                       "art by hinata matsumura, alphonse mucha, mike mignola, kazu kibuishi, and rev.matsuoka",
                   "Ninja":
                       "art by kazuya yamashita, yuya kanzaki, yang zhizhuo",
                   "Pirate":
                       "art by alphonse mucha, kai carpenter, ignacio fernandez rios, charlie bowater",
                   "Superhero":
                       "art by alphonse mucha, greg rutkowski, ross tran, leesha hannigan, ignacio fernandez rios, kai carpenter",
                   "Knight":
                       "art by wlop, greg rutkowski, and charlie bowater",
                   "Cyborg":
                       "art by artgerm and greg rutkowski and charlie bowater and magali villeneuve and alphonse mucha",
                   "Monster":
                       "art by yahoo kim, max grecke, james white, viktor hulík, fabrizio bortolussi",
                   "Vampire":
                       "art by leesha hannigan, thierry doizon, alphonse mucha, kai carpenter",
                   "Zombie":
                       "art by greg rutkowski, charlie bowater, and magali villeneuve",
                   "Witch":
                       "art by yuumei, greg rutkowski, eddie hong, and charlie bowater",
                   }



class ArtStyle(list, Enum):
    NOUVEAU = [
        "Alphonse Mucha",
        "Ryan Kittleson",
        "Kai Carpenter"
    ]
    FANTASY = [
        "Greg Rutkowski",
        "John Howe",
        "Alan Lee",
        "Weta Workshop",
        "Stephan Martiniere"
    ]
    ETHERAL = [
        "Charlie Bowater",
        "WLOP",
        "Leesha Hannigan",
        "Magali Villeneuve"
    ]
    WHIMSICAL = [
        "Jim Kay",
        "Ronald Brenzell",
        "Kazu Kibuishi",
        "Hinata Matsumura",
        "Rev. Matsuoka"
    ],
    VIBRANT = [
        "RossDraws",
        "Yahoo Kim",
        "Max Grecke",
        "James White"
    ]
    ANIME = [
        "Kazuya Yamashita",
        "Yuya Kanzaki"
    ]
    GRITTY = [
        "Marko Djurdjevic",
        "Mike Mignola"
    ]
    SCIFY = [
        "Yuumei",
        "Eddie Hong",
        "BARONTiER"
    ]
    ORIENTAL = [
        "Yang Zhizhuo"
    ]
    ABSTRACT = [
        "Viktor Hulík"
    ]
    SURREAL = [
        "Fabrizio Bortolussi"
    ]
    COMIC = [
        "Fred Perry"
    ]