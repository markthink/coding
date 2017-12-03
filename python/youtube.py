import ssl
from pytube import YouTube
# pprint-pretty print 不必要，仅仅为了让输出更好看，每个视频文件占一行
from pprint import pprint

# 证书问题解决
# https://stackoverflow.com/questions/27835619/urllib-and-ssl-certificate-verify-failed-error
# http://bookshadow.com/weblog/2015/04/22/sae-python-weibo-sdk-certificate-verify-failed/
ssl._create_default_https_context = ssl._create_unverified_context

yt = YouTube('https://www.youtube.com/watch?v=Prls3rtFXv8')

# pprint(yt.get_videos())
# print(yt.filename)
print(yt.filter('mp4')[-1])

video = yt.get('mp4', '720p')
print(video.url)
# video.download('./')