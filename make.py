#!/bin/python3

import glob
import re
import os
from shutil import copytree, copyfile

NUMBER_OF_LATEST_BLOG = 3

links_for_index_html ='<ul class="url-list">\n'
links_for_archive_list = '<ul class="archive">\n'
first = True

# ls blog html files
html_files = glob.glob("./blog/*")
html_files.sort(reverse=True)

#latest3 = 0 #最新の3件のみ表示

for index, url in enumerate(html_files):
    if url[-10:] == "index.html":
        pass
    else:
        #ファイルを開いて
        with open(url + "/index.html") as file:
            nakami = file.read()

            # get title
            pagename = re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' ')))
            date = url[-10:]
            date = re.sub("-","/",date)

            if index <= NUMBER_OF_LATEST_BLOG:
                links_for_index_html += f'      <li><a href=".{url}">{pagename} - {date}</a></li>\n'

            if first:
                links_for_archive_list += f'      <details><summary>{date[:-3]}</summary>\n        <li><a href=".{url}">{pagename} - {date}</a></li>\n'
                first = False
            elif former != date[:-3]:
                links_for_archive_list += f'      </details>\n      <details><summary>{date[:-3]}</summary>\n        <li><a href=".{url}">{pagename} - {date}</a></li>\n'
            else:
                links_for_archive_list += f'        <li><a href=".{url}">{pagename} - {date}</a></li>\n'
            former = date[:-3]

links_for_index_html += '    </ul class="url-list">'
links_for_archive_list += '      </ul></li>\n    </ul class="archive">'

with open("./blog/index.html") as file:
    old_index_html_file = file.read()
    new_index_html_file = re.sub("<ul class=\"url-list\">.*</ul class=\"url-list\">",links_for_index_html, old_index_html_file,flags=re.DOTALL)
    new_index_html_file = re.sub("<ul class=\"archive\">.*</ul class=\"archive\">",links_for_archive_list, new_index_html_file,flags=re.DOTALL)
with open("./blog/index.html", mode="w") as file:
    file.write(new_index_html_file)


for category in ["./works/*/*.html","./blog/*/*.html"]:
    files = glob.glob(category)
    for url in files:
        with open(url) as file:
            nakami = file.read()
            #titleタグからページ名を習得、頭についてる「りんりん - 」は外す
            pagename = re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' ')))

            if url[-10:] == "index.html":
                shorturl = url[:-11]
            else:
                shorturl = url
            links_for_index_html += "      <li><a href=\"" + shorturl + "\">" + pagename + "</a></li>\n"
            metatag = "<!--置換用タグ1-->\n    <meta property=\"og:url\" content=\"https://lnln.dev/" + re.sub("\./","",shorturl) + "\">\n    <meta property=\"og:title\" content=\"" + pagename + "\">\n    <!--置換用タグ2-->"

            onew = re.sub("<!--置換用タグ1-->.*<!--置換用タグ2-->",metatag,nakami,flags=re.DOTALL)
        with open(url,mode="w") as file:
            file.write(onew)

#   mkdir dist
if not os.path.exists("./dist"):
    os.mkdir("./dist")


for category in ["css", "works", "blog"]:
    files = glob.glob(category)
    for url in files:
        copytree(url,"./dist/" + url)

copyfile("index.html","./dist/index.html")
copyfile("404.html","./dist/404.html")
copyfile("CNAME","./dist/CNAME")



print("Done!!")

    