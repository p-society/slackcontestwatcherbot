import datetime
from dateutil import tz
import json
import requests
from os import environ

base_url = "https://clist.by/api/v1/contest/"
header = {"Authorization": environ["CLIST_API_TOKEN"]}


def convert_time(utc):
    return str(
        utc.replace(tzinfo=tz.gettz('UTC'))
        .astimezone(tz.gettz('Asia/Calcutta'))
        .replace(microsecond=0)
        .replace(tzinfo=None))


def convert_dt(string):
    return datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S')


def watchcontest(now):
    cur_time = now.replace(microsecond=0) + datetime.timedelta(hours=1)
    para = {"start": cur_time.isoformat()}
    resp = requests.get(base_url, params=para, headers=header)
    flag = False
    res = ""
    if(resp.status_code == 200):
        contests = json.loads(resp.content.decode("utf-8"))
        if(len(contests["objects"]) >= 1):
            flag = True
            for con in contests["objects"]:
                lcls = convert_time(convert_dt(con["start"]))
                lcle = convert_time(convert_dt(con["end"]))
                res += con["event"] + " will start in 1 hour!\n"
                res += con["href"] + "\n"
                res += "Start: " + lcls + "\n"
                res += "End: " + lcle + "\n"
                res += "Duration: " + str(
                    datetime.timedelta(seconds=con["duration"])) + "\n\n"
    return flag, res


def upcoming(site, now):
    now = now.replace(microsecond=0)
    then = now + datetime.timedelta(days=7)
    para = {
        "start__gte": now.isoformat(),
        "start__lte": then.isoformat(),
        "resource__name__contains": site,
        "order_by": "start"}
    resp = requests.get(base_url, params=para, headers=header)
    if(resp.status_code == 200):
        return (
            "Following are the upcoming contests within a week:\n\n" +
            build_string(json.loads(resp.content.decode("utf-8"))))
    else:
        return "Error " + str(resp.status_code)


def ongoing(site, now):
    now = now.replace(microsecond=0)
    para = {
        "start__lte": now.isoformat(),
        "end__gt": now.isoformat(),
        "resource__name__contains": site,
        "order_by": "start"}
    resp = requests.get(base_url, params=para, headers=header)
    if(resp.status_code == 200):
        return (
            "Following are the ongoing contests:\n\n" +
            build_string(json.loads(resp.content.decode("utf-8"))))
    else:
        return "Error " + str(resp.status_code)


def build_string(contests):
    res = ""
    con_ind = 1
    for con in contests["objects"]:
        res += str(con_ind) + ". " + con["event"] + "\n"
        res += con["href"] + "\n"
        res += "Start: " + convert_time(convert_dt(con["start"])) + "\n"
        res += "End: " + convert_time(convert_dt(con["end"])) + "\n"
        res += "Duration: " + str(datetime.timedelta(seconds=con["duration"]))
        res += "\n\n"
        con_ind += 1
    return res
