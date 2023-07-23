# Instagram Downloader
The purpose of this project was to create a simple Instagram video downloader in Python that used only built-in libraries for me to understand how Instagram video downloaders work.

This code was derived by reverse engineering the yt-dlp Instagram extractor.

The program can be used by calling "python main.py <video_url>"

# Explanation
The program works by calling on Instagram's private API, graphQL, which is typically only accessed by the front-end of Instagram's website and is used to retrieve information from the back-end, including the downloadable video url<br>

The program starts by taking the URL from the argument provided.<br>
It then uses re library to both check if the URL provided is a valid format and to extract the video_id from the URL. The video_id is the 11 character code that identifies every Instagram video. After checking that the URL is valid, the program sets the URL to the formatted URL to remove any unnecessary parts in the provided URL.<br>
The next part of the program is responsible for making an HTTP GET request to a URL that both checks if the API is working, and also retrieves the csrf_token, which is used by Instagram to check if the requests are valid.<br>

We first define the headers that needs to be provided with the HTTP request. These headers are taken from the ones that the Instagram front-end code uses to make a request to the API. These can be found by going Developer Tools on a browser, opening the network tab, loading up a page with an Instagram video, and clicking on the URL that the website is making an API resquest to.<br>
The api_check_url uses a custom decoded base64 code from the video_id, and the program uses http.cookiejar library and a urllib.request.OpenerDirector object to make a a GET request and store the cookies given by the webpage.<br>
If it receives a response of 200 for "ok", then it takes the csrf_token from the cookies. <br>

Now that we know the api is working properly and we have the csrf_token, we are ready to make a request to the API URL responsible for retrieving the information from a video, which includes the downloadble video URL source.<br>
This url is stored in the code under the variable api_url, and it includes 3 critical pieces of information: the query_hash, the shortcode, and the comment paremeters. I will start by explaining the shortcode and the comment paremeters. The shortcode is just the video_id and the comment paremeters are information about how many comments and comment replies should be loaded. The query hash is a number that is pre_computed in the code, and it is based on the type of API request, which in this case is general information about the video, as well as the comment paremeters that are provided. Because those are always the same, the appropriate query hash is hard-coded onto the code.<br>
The headers like before are the ones used by the front-end of the website when making a request to this URL, and it needs the crsf_token from before. <br>
After that, we can now make a GET request to the URL, and if we read the response for the request, it should be json file containing the general information from the video. The code decodes it using 'utf-8' to put it in the proper formatting, and then it makes puts it into a dict<br>

In the general_info dict, we can retrieve specfically just the information from the media and store it in its own variable. In the media dict, we can now get the video_url, which is the url which contains the data from the video and we can download from directly. The media dict also contains many other useful information, some of which I left on a comment. <br>
Now that the code acquired the media_url, we are ready to make the final request to download the actual video. Like before, the header used is the same one that the website's front-end uses when loading up the video to the webpage.<br>
We then make a GET request to video_url, and we save it to an mp4 file by using open(filename, "wb"), which writes the bytes of the response onto the file created, thus creating a video file with the contents of the downloaded video. <br>
The filename is arbitrarily chosen based on the video url and the current time the video is downloaded.
