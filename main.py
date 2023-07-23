import sys
import re
import urllib.request
import http.cookiejar
import json
import datetime


#A custom decode base64 function that is used to get an API URL from the video_id
def decode_base64(string):
	base64_chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_'
	base64_table = {char: i for (i, char) in enumerate(base64_chars)}
	base = 64
	result = 0
	for char in string:
		result = result * base + base64_table[char]
	return result


def main():
	if len(sys.argv) < 2: 
		print("Argument missing: url")
		return
	url = sys.argv[1]

	#Ensures URL is in proper format and makes a group for the video_id
	re_match = re.compile('(?P<url>https?://(?:www\\.)?instagram\\.com(?:/[^/]+)?/(?:p|tv|reel)/(?P<id>[^/?#&]+))').match(url)
	if not re_match:
		print("Invalid Instagram URL: URL must be of format https://www.instagram.com/p|tv|reel/video_id")
		return
	url, video_id = re_match.groups()

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
	req = urllib.request.Request(api_url, None, headers)
	with urllib.request.urlopen(req) as res:
		res_data = res.read()
	content = res_data.decode("utf-8", "replace")
	general_info = json.loads(content)

	#Get media information from general_info
	media = general_info["data"]["shortcode_media"]
	video_url = media["video_url"]

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
		filename = f"Instagram video [{video_id}] {current_time}.mp4"
		with open(filename, "wb") as f: 
			f.write(res.read())

if __name__ == "__main__":
	main()
