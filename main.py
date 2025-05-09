import os
import sqlite3
from typing import TextIO
import re
import argparse


def create_db(name: str) -> sqlite3.Connection:
    conn = sqlite3.connect(name+".db")
    conn.execute("""
                 CREATE TABLE "playlist" (
	             "tvg-id"	TEXT NOT NULL,
	             "name"	TEXT NOT NULL,
	             "country"	TEXT NOT NULL,
	             "language"	TEXT NOT NULL,
	             "logo"	TEXT,
	             "group-title"	TEXT,
	             "resource"	TEXT NOT NULL,
	             "additional-info"	TEXT,
	             "useragent"	TEXT,
	             "referrer"	TEXT
                 )""")
    conn.commit()
    return conn


def get_dict():
    return {"tvg-id": "",
            "tvg-name": "",
            "tvg-country": "",
            "tvg-logo": "",
            "group-title": "",
            "http-user-agent": "",
            "http-referrer": "",
            "resource": "",
            "name": "",
            "tvg-language": ""
            }


def parse(file: TextIO):
    channels = []
    current_channel = get_dict()
    for line in file:
        line = line.rstrip("\n")
        if line.startswith("#EXTM3U"):
            continue
        elif line.startswith("\n"):
            continue
        elif line.startswith("#EXTINF:-1"):
            for tag in TAGS:
                current_channel[tag] = re.findall(tag+'="(.*?)"', line)[0] if re.findall(tag+'="(.*?)"', line) else ""
                current_channel["name"] = line.split('",')[-1]
        elif line.startswith("#EXTVLCOPT:http-referrer"):
            current_channel["http-referrer"] = re.findall(
                "#EXTVLCOPT:http-referrer=(.*?)", line)[0]
        elif line.startswith("#EXTVLCOPT:http-user-agent"):
            current_channel["http-user-agent"] = re.findall(
                "#EXTVLCOPT:http-user-agent=(.*?)", line)[0]
        else:
            current_channel["resource"] = line
            channels.append(current_channel)
            current_channel = get_dict()
    return channels


def write_to_db(data: list, conn: sqlite3.Connection):
    for entry in data:
        conn.execute("""
        INSERT INTO playlist 
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
                     (entry["tvg-id"], entry["tvg-name"],
                      entry["tvg-country"], entry["tvg-language"],
                      entry["tvg-logo"], entry["group-title"],
                      entry["resource"], entry["name"],
                      entry["http-user-agent"], entry["http-referrer"]))
    conn.commit()


TAGS = ('tvg-id', 'tvg-name', 'tvg-country',
        'tvg-logo', 'group-title', "tvg-language")
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="name of database")
    parser.add_argument("path", help="path to read playlists")
    args = parser.parse_args()
    file_names = os.listdir(args.path)
    conn = create_db(args.name)
    for name in file_names:
        if name.endswith(".m3u"):
            with open(args.path +"/"+name, mode="r", encoding='utf-8') as file:
                write_to_db(parse(file), conn)
