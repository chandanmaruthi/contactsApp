import urllib

testfile = urllib.URLopener()
filePath ="https://video.xx.fbcdn.net/v/t42.3356-2/15963520_10154318908768108_2690950959751757824_n.mp4/video-1484081769.mp4?vabr=776668&oh=0c1153e1a3a945dc3c913ef2941977f9&oe=58772E70"

testfile.retrieve(filePath, "poke.mp4")
