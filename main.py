import os
import requests
from flask import Flask
from flask import render_template


ACCOUNT_ID = os.environ.get("ACCOUNT_ID", "6206459123001")
BCOV_POLICY = os.environ.get(
    "BCOV_POLICY",
    "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd",
)

bc_url = (
    f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos"
)

bc_hdr = {"BCOV-POLICY": BCOV_POLICY}

jw_url = "https://cdn.jwplayer.com/v2/media"

app = Flask(__name__)


@app.route("/<int(fixed_digits=13):video_id>/<int:vidid>/<string:email>/<string:password>")
def brightcove(video_id,vidid,email,password):
    video_response = requests.get(f"{bc_url}/{video_id}", headers=bc_hdr)
 
    if video_response.status_code != 200:
        return "<font color=red size=20>Wrong Video ID</font>"
    
    url = 'https://elearn.crwilladmin.com/api/v1/login-other'
    values = {'email': f"{email}",
          'password': f"{password}"}        
    r = requests.post(url, data=values)
    resp = json.loads(r.content)["data"]["token"]
    surl=requests.get(f"https://elearn.crwilladmin.com/api/v1/livestreamToken?type=brightcove&vid={vidid}&token={resp}")
    stoken = surl.json()["data"]["token"]
    video = video_response.json()

    video_name = video["name"]

    video_source = video["sources"][5]
    video_url = video_source["src"]+"&bcov_auth="+stoken
    widevine_url = ""
    microsoft_url = ""
    if "key_systems" in video_source:
        widevine_url = video_source["key_systems"]["com.widevine.alpha"][
            "license_url"
        ]
        widevine_url1 = str(widevine_url).replace('?','/master.m3u8?')+"&bcov_auth="+stoken
        
        microsoft_url = video_source["key_systems"]["com.microsoft.playready"][
            "license_url"
        ]
        microsoft_url1 = str(microsoft_url).replace('?','/master.m3u8?')+"&bcov_auth="+stoken
        

    track_url = video["text_tracks"][1]["src"]
    return render_template(
        "template.html",
        type="brightcove",
        video_name=video_name,
        video_url=video_url,
        track_url=track_url,
        
    )
