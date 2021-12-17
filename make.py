#!/bin/python3

import glob
import re
import sys

#blogの分

linksforindex ="<ul class=\"url-list\">\n"
linksforarchive = "<ul class=\"archive\">\n"
first = True

htmlfiles = glob.glob("./blog/*")
htmlfiles.sort(reverse=True)

latest3 = 0 #最新の3件のみ表示

for url in htmlfiles:
    if url[-10:] == "index.html":
        pass
    else:
        #ファイルを開いて
        with open(url + "/index.html") as file:
            nakami = file.read()
            #titleタグからページ名を習得、頭についてる「りんりん - 」は外す
            pagename = re.sub("りんりん - ","",re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' '))))
            date = url[-10:] #re.sub("</div class=\"date\">.*", "",re.sub(".*<div class=\"date\">","",nakami.replace('\n',' ')))
            date = re.sub("-","/",date)

            if latest3 < 3:
                linksforindex += "      <li><a href=\"." + url + "\">" + pagename + " - " + date + "</a></li>\n"
                latest3 = latest3 + 1

            if first:
                linksforarchive += "      <details><summary>" + date[:-3] + "</summary>\n        <li><a href=\"." + url + "\">" + pagename + " - " + date + "</a>" + "</li>\n"
                first = False
            elif former != date[:-3]:
                linksforarchive += "      </details>\n      <details><summary>" + date[:-3] + "</summary>\n        <li><a href=\"." + url + "\">" + pagename + " - " + date + "</a>" + "</li>\n"
            else:
                linksforarchive += "        <li><a href=\"." + url + "\">" + pagename + " - " + date + "</a>" + "</li>\n"
            former = date[:-3]

linksforindex += "    </ul class=\"url-list\">"
linksforarchive += "      </ul></li>\n    </ul class=\"archive\">"

with open("./blog/index.html") as file:
    nakami = file.read()
    onew = re.sub("<ul class=\"url-list\">.*</ul class=\"url-list\">",linksforindex, nakami,flags=re.DOTALL)
    onew = re.sub("<ul class=\"archive\">.*</ul class=\"archive\">",linksforarchive, onew,flags=re.DOTALL)
with open("./blog/index.html", mode="w") as file:
    file.write(onew)


for category in ["./works/*/*.html","./blog/*/*.html"]:
    files = glob.glob(category)
    for url in files:
        with open(url) as file:
            nakami = file.read()
            #titleタグからページ名を習得、頭についてる「りんりん - 」は外す
            pagename = re.sub("りんりん - ","",re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' '))))

            if url[-10:] == "index.html":
                shorturl = url[:-11]
            else:
                shorturl = url
            linksforindex += "      <li><a href=\"" + shorturl + "\">" + pagename + "</a></li>\n"
            metatag = "<!--置換用タグ1-->\n    <meta property=\"og:url\" content=\"https://lnln.dev/" + re.sub("\./","",shorturl) + "\">\n    <meta property=\"og:title\" content=\"りんりん - " + pagename + "\">\n    <!--置換用タグ2-->"

            onew = re.sub("<!--置換用タグ1-->.*<!--置換用タグ2-->",metatag,nakami,flags=re.DOTALL)
        with open(url,mode="w") as file:
            file.write(onew)

print("Done!!")