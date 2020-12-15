import glob
import re
import sys

#ディレクトリを習得
categories = glob.glob("./*/")

categories.remove("./css/")

#最終的に突っ込みたいリンクをこれらの変数に綴っていく
linksforindex ="<ul class=\"url-list\">\n"
linksforhome = "<div class=\"cp_navi\">\n    <ul>\n      <li><a href=\"./\">Home</a></li>\n"
links ="<div class=\"cp_navi\">\n    <ul>\n      <li><a href=\"../\">Home</a></li>\n"

#各ディレクトリ内ごとの作業
for category in categories:

    #ディレクトリ内のhtmlファイルのリストを習得
    files = glob.glob(category + "*.html")
    #相対パスの中からディレクトリの名前を習得
    titlelist = glob.glob(category + "*.title")
    if len(titlelist) == 1:
        title = titlelist[0]
        categoryname = re.sub('\.title','',re.sub('\./.*/','',title))
    else:
        print("エラー タイトルを示すファイルが複数存在しています")
        sys.exit()

    #linksforindex += "<li>\n<a>" + categoryname + "<span class=\"caret\"></span></a>\n<div>\n<ul>\n"
    links += "      <li><a href=\"." + category + "index.html\">" + categoryname + "</a><li>\n"
    linksforhome += "      <li><a href=\"" + category + "index.html\">" + categoryname + "</a><li>\n"

    #各ファイルごとの作業
    for url in files:
        if url[-10:] == "index.html":
            pass
        else:
            #ファイルを開いて
            with open(url) as file:
                nakami = file.read()
                #titleタグからページ名を習得，頭についてる「りんりん - 」は外す
                pagename = re.sub("りんりん - ","",re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' '))))
                linksforindex += "      <li><a href=\"." + url + "\">" + pagename + "</a></li>\n"

    linksforindex += "    </ul class=\"url-list\">\n"


    #index.htmlだけは別の操作
    files = glob.glob(category+ "index.html")
    if len(files) == 1:
        for url in files:
            with open(url) as file:
                nakami = file.read()
                onew = re.sub("<ul class=\"url-list\">.*</ul class=\"url-list\">",linksforindex, nakami,flags=re.DOTALL)
            with open(url, mode="w") as file:
                file.write(onew)
    else:
        print("エラー index.htmlが複数存在しています")
        sys.exit()

    linksforindex ="<ul class=\"url-list\">\n"

#後に書き換える際，別の</div>タグに引っかからないように</div class="cp_navi">としている
linksforindex += "</ul class=\"url-list\">"
links += "    <ul>\n  </div class=\"cp_navi\">"
linksforhome += "    <ul>\n  </div class=\"cp_navi\">"

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
            #onew = onew.replace("<link href=\"lnln.css\" rel=\"stylesheet\">","<link href=\"../css/lnln.css\" rel=\"stylesheet\">")
            #titleの頭に「りんりん - 」をつける
            onew = re.sub("<title>.*</title>","<title>りんりん - " + pagename + "</title>",onew)

        with open(url, mode="w") as file:
            file.write(onew)

with open("./index.html") as file:
    nakami = file.read()
    onew = re.sub("<div class=\"cp_navi\">.*</div class=\"cp_navi\">",linksforhome, nakami,flags=re.DOTALL)
with open("./index.html", mode ="w") as file:
    file.write(onew)

for category in categories:
    files = glob.glob(category + "*.html")
    for url in files:
        with open(url) as file:
            nakami = file.read()
            #titleタグからページ名を習得，頭についてる「りんりん - 」は外す
            pagename = re.sub("りんりん - ","",re.sub("</title>.*", "",re.sub(".*<title>","",nakami.replace('\n',' '))))
            linksforindex += "      <li><a href=\"" + url + "\">" + pagename + "</a></li>\n"
            metatag = "<!--置換用タグ1-->\n    <meta property=\"og:url\" content=\"https://lnln4ch.netlify.app/" + re.sub("\./","",url) + "\">\n    <meta property=\"og:title\" content=\"りんりん - " + pagename + "\">\n    <!--置換用タグ2-->"

            onew = re.sub("<!--置換用タグ1-->.*<!--置換用タグ2-->",metatag,nakami,flags=re.DOTALL)
        with open(url,mode="w") as file:
            file.write(onew)

print("Done!!\n")