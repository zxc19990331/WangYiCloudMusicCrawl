# -*- coding:utf-8 -*-
import requests
import os
import json
import re
import time
from CloudMusicCrawl.proxy import *
from CloudMusicCrawl.wordanalyse import *

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'music.163.com',
    'Referer': 'http://music.163.com',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36'
}

cookies = {'appver': '2.0.2'}


def ShowList(list):
    for each in list:
        print(each)


#返回作品名称的字符串
def GetSongName(songID):
    url = 'http://music.163.com/api/song/detail/?id={}&ids=%5B{}%5D'.format(songID,songID)
    detail = GetResponse(url,headers,cookies)
    detail_json = json.loads(detail.text)
    name = detail_json['songs'][0]['name']
    #因为仅考虑歌词，去掉了所有 歌名（live版） 歌名（至尊版）的字段
    pattern = re.compile(r'\s*[\(（].*[）\)]')
    name = re.sub(pattern,'',name)
    return validateTitle(name)

#返回作品作者的字符串
def GetSongAuthor(songID):
    url = 'http://music.163.com/api/song/detail/?id={}&ids=%5B{}%5D'.format(songID, songID)
    detail = GetResponse(url, headers, cookies)
    detail_json = json.loads(detail.text)
    artistlist = detail_json['songs'][0]['artists']
    artist = ''
    for each in artistlist:
        artist += each['name'] + ' '
    return artist.strip()


#从songID返回歌词字符串，API不稳定有可能会返回NULL
def GetLyric(songID, titledel = True, artistdel=True, timedel=True ,ends = '\n'):
    songname = GetSongName(songID)
    songartist = GetSongAuthor(songID)
    title = ''
    lyric_url = 'http://music.163.com/api/song/lyric?id=' + str(songID) + '&lv=1&kv=1&tv=-1'  # 歌词的api
    lyr = GetResponse(lyric_url,headers,cookies)
    lyr_json = json.loads(lyr.text)
    try:
        if('lrc' in lyr_json):#假如有歌词
            lyric = lyr_json['lrc']['lyric']  # 导入歌词文本
        else:
            print('songID:{} {} artist: {} has no lyric '.format(songID, songname, songartist), end=ends)
            return ''
    except Exception as e:
        print('songID {} has something wrong'.format(songID))
        print('Error Information:', e)
    if(not titledel):
        title = songname + '\n' + '歌手：' + GetSongAuthor(songID) + '\n'
    if (timedel):
        pattern = re.compile(r'\[\S*\]')  # 去除[]的时间标识
        lyric = re.sub(pattern, '', lyric)
    if (artistdel):
        pattern = re.compile(r'.+[:：].+')  # 去除艺术家
        lyric = re.sub(pattern, '', lyric)
    print('get lyric from songID:{} {} artist: {} successfully'.format(songID,songname,songartist),end = ends)
    return title + lyric.strip()


def GetAlbumName(albumID):
    album_url = 'http://music.163.com/api/album/' + str(albumID)
    album = GetResponse(album_url, headers, cookies)
    # print('Response done')
    s = album.text
    album_json = json.loads(s)
    return validateTitle(album_json['album']['name'])


#从albumID返回songID列表
def GetAlbumSongID(albumID,ends = '\n'):
    album_url = 'http://music.163.com/api/album/' + str(albumID)
    album = GetResponse(album_url, headers, cookies)
   # print('Response done')
    s = album.text
    album_json = json.loads(s)
    songIDlist = []
    for index, each in enumerate(album_json['album']['songs']):
        songIDlist.append(each['id'])
    print('get songID from albumID:{} successfully'.format(albumID),end = ends)
    return songIDlist


#从歌单ID返回songID列表
def GetListSongID(ListID):
    url = 'http://music.163.com/api/playlist/detail?id=' + str(ListID)
    songlist = GetResponse(url,headers,cookies)
    s = songlist.text
    list_json = json.loads(s)
    songIDlist = []
    listname = list_json['result']['name']
    for each in list_json['result']['tracks']:
        songIDlist.append(each['id'])
    print('get songID from songlistID:{} {} successfully'.format(ListID,listname))
    return songIDlist


def GetListName(ListID):
    url = 'http://music.163.com/api/playlist/detail?id=' + str(ListID)
    songlist = GetResponse(url, headers, cookies)
    s = songlist.text
    list_json = json.loads(s)
    return validateTitle(list_json['result']['name'])


#从歌手返回所有专辑idlist
def GetSingerAlbumID(singerID):
    url = 'http://music.163.com/api/artist/albums/{}?id={}&limit=1024'.format(singerID,singerID)
    res = GetResponse(url,headers,cookies)
    list_json = json.loads(res.text)
    albumIDlist = []
    listname = list_json['hotAlbums']
    for each in listname:
        albumIDlist.append(each['id'])
    return albumIDlist


def GetSingerName(singerID):
    url = 'http://music.163.com/api/artist/albums/{}?id={}&limit=1024'.format(singerID, singerID)
    res = GetResponse(url, headers, cookies)
    list_json = json.loads(res.text)
    return list_json['artist']['name']

def AddLyric(file,text):
    fpath = os.path.join(file+'.txt')
    f = open(fpath,'a', encoding="utf-8")
    f.write(text)
    f.close()


def validateTitle(title):
    rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/ \ : * ? " < > |'
    new_title = re.sub(rstr, "_", title)  # 替换为下划线
    new_title.strip()
    if(len(new_title)>200):
        return new_title[0:200].strip()
    else:
        return new_title


if __name__ == '__main__':
    songID = 185857
    print(GetSongName(songID))
