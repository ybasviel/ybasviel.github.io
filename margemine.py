import glob
import re

#ディレクトリを習得
categories = glob.glob("./*/")

#最終的に突っ込みたいリンクをこれらの変数に綴っていく
linksforhome ="<div class=\"cp_navi\">\n<ul>\n<li><a href=\"./home.html\">Home</a></li>\n"
links ="<div class=\"cp_navi\">\n<ul>\n<li><a href=\"../home.html\">Home</a></li>"

#各ディレクトリ内ごとの作業
for category in categories:

    #ディレクトリ内のhtmlファイルのリストを習得
    files = glob.glob(category + "*.html")
    #相対パスの中からディレクトリの名前を習得
    categoryname = re.sub('/','',re.sub('\./','',category))

    linksforhome += "<li>\n<a>" + categoryname + "<span class=\"caret\"></span></a>\n<div>\n<ul>\n"
    links += "<li>\n<a>" + categoryname + "<span class=\"caret\"></span></a>\n<div>\n<ul>\n"

    #各ファイルごとの作業
    for url in files:

        #ファイルを開いて
        with open(url) as file:
            nakami = file.read()

            #titleタグからページ名を習得，頭についてる「りんりん - 」は外す
            pagename = re.sub("りんりん - ","",re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' '))))

            linksforhome += "<li><a href=\"" + url + "\">" + pagename + "</a></li>\n"
            links += "<li><a href=\"" + url.replace("./","../") + "\">" + pagename + "</a></li>\n"
    
    linksforhome += "</ul>\n</div>\n</li>\n"
    links += "</ul>\n</div>\n</li>\n"

#後に書き換える際，別の</div>タグに引っかからないように</div class="cp_navi">としている
linksforhome += "</ul>\n</div class=\"cp_navi\">"
links += "</ul>\n</div class=\"cp_navi\">"

for category in categories:
    files = glob.glob(category + "*.html")

    for url in files:
        with open(url) as file:
            nakami = file.read()
            #ページ名を取得
            pagename = re.sub("りんりん - ","",re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' '))))
            
            #リンクを書き込む
            onew = re.sub("<div class=\"cp_navi\">.*</div class=\"cp_navi\">",links, nakami,flags=re.DOTALL)
            #cssの相対パスを書き込む(要らないかもしれないけど自分がミスったときのために念の為)
            onew = onew.replace("<link href=\"lnln.css\" rel=\"stylesheet\">","<link href=\"../lnln.css\" rel=\"stylesheet\">")
            #titleの頭に「りんりん - 」をつける
            onew = re.sub("<title>.*</title>","<title>りんりん - " + pagename + "</title>",onew)

        with open(url, mode="w") as file:
            file.write(onew)

#home.htmlだけは別の操作
with open("./home.html") as file:
    nakami = file.read()
    onew = re.sub("<div class=\"cp_navi\">.*</div class=\"cp_navi\">",linksforhome, nakami,flags=re.DOTALL)

with open("./home.html", mode="w") as file:
    file.write(onew)

print("Done!!\n")