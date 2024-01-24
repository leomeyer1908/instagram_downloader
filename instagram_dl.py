#!/usr/bin/env python3
import sys
import re
import urllib.request
import http.cookiejar
import json
import datetime
import time
import argparse


#A custom decode base64 function that is used to get an API URL from the video_id
def decode_base64(string):
    base64_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
    base64_table = {char: i for (i, char) in enumerate(base64_chars)}
    base = 64
    result = 0
    for char in string:
        result = result * base + base64_table[char]
    return result

def get_video(url, video_id, csrf_token, sessionid=None, ds_user_id=None):
    #This api_url returns the general info of the video.  
    api_url = f"https://www.instagram.com/graphql/query/?query_hash=9f8827793ef34641b2fb195d4d41151c&variables=%7B%22shortcode%22%3A%22{video_id}%22%2C%22child_comment_count%22%3A3%2C%22fetch_comment_count%22%3A40%2C%22parent_comment_count%22%3A24%2C%22has_threaded_comments%22%3Atrue%7D"

    headers = {
        'X-IG-App-ID': '936619743392459',
        'X-ASBD-ID': '198387',
        'X-IG-WWW-Claim': '0',
        'Origin': 'https://www.instagram.com',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        'X-CSRFToken': csrf_token,
        'X-Requested-With': 'XMLHttpRequest',
        'Referer': url
    }

    
    if ds_user_id is None and sessionid is None:
        cookies = f'dpr=2; ig_nrcb=1; csrftoken={csrf_token};'
    else:
        if ds_user_id is None or sessionid is None:
            print("Either sessionid or ds_user_id is None")
            return None
        #cookies = f"dpr=2; ig_nrcb=1; csrftoken={csrf_token}; sessionid={sessionid}"
        cookies = f'dpr=2; ig_nrcb=1; csrftoken={csrf_token}; ds_user_id={ds_user_id}; sessionid={sessionid};'
    headers["Cookie"] = cookies

    req = urllib.request.Request(api_url, None, headers)
    with urllib.request.urlopen(req) as res:
        res_data = res.read()
    content = res_data.decode("utf-8", "replace")
    general_info = json.loads(content)

    #Get media information from general_info
    media = general_info["data"]["shortcode_media"]
    video_url = media["video_url"]

    username = media["owner"]["username"]
    description = media["edge_media_to_caption"]["edges"][0]["node"]["text"]

    """
    Some other useful information that can be retrieved from media:

    username = media["owner"]["username"]
    description = media["edge_media_to_caption"]["edges"][0]["node"]["text"]
    dimensions = media["dimensions"]
    comments = media["edge_media_to_parent_comment"]["edges"] 
    duration = media["video_duration"]
    view_count = media["video_view_count"]
    play_count = media["video_play_count"]
    like_count = media["edge_media_preview_like"]["count"]
    is_ad = media["is_ad"]
    """


    headers = {
        'Accept-Encoding': 'identity',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
        'Sec-Fetch-Mode': 'navigate',
        'Referer': 'https://www.instagram.com/'
    }
    #Downloads video from video_url and writes to mp4 file
    req = urllib.request.Request(video_url, None, headers)
    with urllib.request.urlopen(req) as res:
        current_time = datetime.datetime.now().strftime("%I:%M:%S %p").replace(":", ".")
        filename = f"ig_video.mp4"
        with open(filename, "wb") as f:
            f.write(res.read())
    #Currently returns username and description, but need to implement way to specify any info from the video user wants
    return (username, description)

def get_sessionid(referer_url, csrf_token, username, password):
    try:
        with open('sessionid.txt', 'r') as f:
            return f.read()
    except:
        print("Login failed, getting new sessionid")
        headers = {
            'X-IG-App-ID': '936619743392459',
            'X-ASBD-ID': '198387',
            'X-IG-WWW-Claim': '0',
            'Origin': 'https://www.instagram.com',
            'Accept': '*/*',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'X-CSRFToken': csrf_token,
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': referer_url
        }

        req = urllib.request.Request('https://www.instagram.com/accounts/login')
        with urllib.request.urlopen(req) as res:
            login_webpage = res.read().decode("utf-8", "replace")

        """
        mobj = re.search(r'<script>requireLazy\(\[\"JSScheduler\",\"ServerJS\"(.*?{("define":.*))\n', login_webpage)
        json_object = json.loads("{" + mobj.group(2)[:-17])
        #json_object2 = json.loads(json_object["define"][64][2]["raw"])

        object_list = str(json_object).split(" ")
        for i, elem in enumerate(object_list):
            if elem == "'rollout_hash':":
                headers["X-Instagram-Ajax"] = object_list[i+1]
                break
        """
        
        x_instagram_ajax = re.search(r'\"rollout_hash\"\s*:\s*\"(.*?)\"', login_webpage).group(1)
        if x_instagram_ajax:
            headers["X-Instagram-Ajax"] = x_instagram_ajax
        else:
            headers["X-Instagram-Ajax"] = 1010967096 #default value if layout of webpage changes, but this value might change too

        headers["Content-Type"] = "application/x-www-form-urlencoded"

        cookies = f"dpr=2; ig_nrcb=1; csrftoken={csrf_token}"

        headers["Cookie"] = cookies

        data = {
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{password}',
            'username': f"{username}",
            'queryParams': '{}',
            'optIntoOneTap': 'false',
            'stopDeletionNonce': '',
            'trustedDeviceRecords': '{}',
        }

        data = urllib.parse.urlencode(data).encode('utf-8')

        req = urllib.request.Request("https://www.instagram.com/api/v1/web/accounts/login/ajax/", headers=headers, data=data, method="POST")

        with urllib.request.urlopen(req) as res:
            res_cookies = res.headers.get_all("Set-Cookie")

        for cookie in res_cookies:
            if "sessionid" in cookie:
                cookie_elements = cookie.split("; ")
                for element in cookie_elements:
                    if element.startswith("sessionid="):
                        sessionid = element[len("sessionid="):]
        with open('sessionid.txt', 'w') as f:
            f.write(sessionid)
        return sessionid

#Gets csrf token while checking if api is working for video
def get_csrf_token(video_id):
    headers = {
        'X-IG-App-ID': '936619743392459',
        'X-ASBD-ID': '198387',
        'X-IG-WWW-Claim': '0',
        'Origin': 'https://www.instagram.com',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36'
    }

    #api_check_url is used to get csrf_token from cookies of the request.  
    api_check_url = f"https://i.instagram.com/api/v1/web/get_ruling_for_content/?content_type=MEDIA&target_id={decode_base64(video_id)}"
    cookie_jar = http.cookiejar.CookieJar()
    cookie_processor = urllib.request.HTTPCookieProcessor(cookie_jar)
    opener = urllib.request.build_opener(cookie_processor)
    req = urllib.request.Request(api_check_url, None, headers)
    with opener.open(req) as res:
        if res.status != 200:
            print("API not granting access")
            return
    csrf_token = cookie_jar._cookies[".instagram.com"]["/"]["csrftoken"].value
    return csrf_token

def get_ds_user_id(username):
    req = urllib.request.Request(f'https://www.instagram.com/{username}/')
    with urllib.request.urlopen(req) as res:
        login_webpage = res.read().decode("utf-8", "replace")
    
    ds_user_id = re.search(r'\"profile_id\"\s*:\s*\"(.*?)\"', login_webpage).group(1)
    return ds_user_id


def download_video(url, username, password):
    #Ensures URL is in proper format and makes a group for the video_id
    re_match = re.compile('(?P<url>https?://(?:www\\.)?instagram\\.com(?:/[^/]+)?/(?:p|tv|reel)/(?P<id>[^/?#&]+))').match(url)
    if not re_match:
        print("Invalid Instagram URL: URL must be of format https://www.instagram.com/p|tv|reel/video_id")
        return
    url, video_id = re_match.groups()

    csrf_token = get_csrf_token(video_id)
    
    if username is not None and password is not None:
        ds_user_id = get_ds_user_id(username)
        sessionid = get_sessionid(url, csrf_token, username, password)
        return get_video(url, video_id, csrf_token, sessionid=sessionid, ds_user_id=ds_user_id)
    return get_video(url, video_id, csrf_token)

def main():
    try:
        parser = argparse.ArgumentParser(description='Downloads Instagram Reels.')

        # Adding a positional argument for the URL
        parser.add_argument('url', help='Specify the URL')

        # Adding the --username and --password options
        parser.add_argument('--username', help='Specify the username', required=False)
        parser.add_argument('--password', help='Specify the password', required=False)

        args = parser.parse_args()

        if args.username is not None and args.password is None:
            raise argparse.ArgumentError(None, "If --username is provided, --password is also required.")
        elif args.password is not None and args.username is None:
            raise argparse.ArgumentError(None, "If --password is provided, --username is also required")

        # Accessing the values of URL, --username, and --password
        url = args.url
        username = args.username
        password = args.password

        # Your program logic using the URL, username, and password
        print(f'URL: {url}')
        print(f'Username: {username}')
        print(f'Password: {password}')

    except argparse.ArgumentError as e:
        print(f'Error: {e}')
        print('Please provide valid command line arguments.')
        parser.print_help()
        return
    except Exception as e:
        print(f'Error: {e}')
        return
    
    download_video(url, username, password)


if __name__ == "__main__":
    main()
