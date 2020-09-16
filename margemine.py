import glob
import re

categories = glob.glob("./*/")

homeurl = "../home.html"

linksforhome ="<div class=\"cp_navi\">\n<ul>\n<li><a href=\"./home.html\">Home</a></li>\n"
links ="<div class=\"cp_navi\">\n<ul>\n<li><a href=\"../home.html\">Home</a></li>"

for category in categories:

    
    files = glob.glob(category + "*.html")
    categoryname = re.sub('/','',re.sub('\./','',category))

    linksforhome += "<li>\n<a>" + categoryname + "<span class=\"caret\"></span></a>\n<div>\n<ul>\n"
    links += "<li>\n<a>" + categoryname + "<span class=\"caret\"></span></a>\n<div>\n<ul>\n"

    for url in files:

        with open(url) as file:
            nakami = file.read()
            pagename = re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' ')))

            linksforhome += "<li><a href=\"" + url + "\">" + pagename + "</a></li>\n"
            links += "<li><a href=\"" + url.replace("./","../") + "\">" + pagename + "</a></li>\n"
    
    linksforhome += "</ul>\n</div>\n</li>\n"
    links += "</ul>\n</div>\n</li>\n"


linksforhome += "</ul>\n</div class=\"cp_navi\">"
links += "</ul>\n</div class=\"cp_navi\">"

for category in categories:
    files = glob.glob(category + "*.html")

    for url in files:
        with open(url) as file:
            nakami = file.read()
            onew = re.sub("<div class=\"cp_navi\">.*</div class=\"cp_navi\">",links, nakami,flags=re.DOTALL)
            onew = onew.replace("<link href=\"lnln.css\" rel=\"stylesheet\">","<link href=\"../lnln.css\" rel=\"stylesheet\">")

        with open(url, mode="w") as file:
            file.write(onew)

with open("./home.html") as file:
    nakami = file.read()
    onew = re.sub("<div class=\"cp_navi\">.*</div class=\"cp_navi\">",linksforhome, nakami,flags=re.DOTALL)

with open("./home.html", mode="w") as file:
    file.write(onew)

print("Done!!\n")
#print(links)
#print(linksforhome)