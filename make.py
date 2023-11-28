#!/bin/python3

import glob
import re
import os
from shutil import copytree, copyfile
from pathlib import Path
import markdown


NUMBER_OF_LATEST_BLOG = 3

SRC_DIR = Path("./src")
OUTPUT_DIR = Path("./dist")
TEMPLATE_DIR = Path("./templates")


def remove_top_dir(p:Path):
    return p.relative_to(p.parts[0])

def convert_md():
    markdown_obj = markdown.Markdown(extensions=['fenced_code'])

    # ls blog html files
    md_files = glob.glob( str(SRC_DIR/"blog/*") )
    #md_files = [f for f in md_files if os.path.isfile(f)]
    md_files.sort(reverse=True)

    for category in ["css", "works", "blog", "img"]:
        files = glob.glob( str(SRC_DIR/category) )
        for url in files:
            url = Path(url)
            url = remove_top_dir(url)
            copytree(SRC_DIR/url, OUTPUT_DIR/url )


    for index, md_file_path in enumerate(md_files):
        md_file_name = md_file_path[-10:] + ".md"
        md_file_name = Path(md_file_name)

        with open(md_file_path/md_file_name) as file:
            md_text = file.read()
            html = markdown_obj.convert(md_text)

            md_file_path = remove_top_dir( Path(md_file_path) )
            
            # htmlいいかんじにrつくう
            with open(TEMPLATE_DIR/"blog-template.html", mode="r") as template:
                html_template = template.read()
                html = html_template.replace("<!--置換用タグ3-->",html)

            with open(OUTPUT_DIR/md_file_path/"index.html", mode="w") as file:
                #print(OUTPUT_DIR/md_file_path/md_file_name.with_suffix('.html'))
                os.remove(OUTPUT_DIR/md_file_path/md_file_name.with_suffix('.md'))
                file.write(html)


def put_index_file():
    # ls blog html files
    html_files = glob.glob( str(OUTPUT_DIR/"blog/*") )
    html_files.sort(reverse=True)

    links_for_index_html ='<ul class="url-list">\n'
    links_for_archive_list = '<ul class="archive">\n'
    first = True
    
    for index, url in enumerate(html_files):
        if url[-10:] == "index.html":
            pass
        else:
            #ファイルを開いて
            with open(url + "/index.html") as file:
                url = remove_top_dir(Path(url))
                url = remove_top_dir(url)
                url = str(url)
                nakami = file.read()

                # get title
                pagename = re.sub("</h1>.*", "",re.sub(".*<h1>","",nakami.replace('\n',' ')))
                date = url[-10:]
                date = re.sub("-","/",date)

                if index < NUMBER_OF_LATEST_BLOG:
                    links_for_index_html += f'      <li><a href="./{url}">{pagename} - {date}</a></li>\n'

                if first:
                    links_for_archive_list += f'      <details><summary>{date[:-3]}</summary>\n        <li><a href="./{url}">{pagename} - {date}</a></li>\n'
                    first = False
                elif former != date[:-3]:
                    links_for_archive_list += f'      </details>\n      <details><summary>{date[:-3]}</summary>\n        <li><a href="./{url}">{pagename} - {date}</a></li>\n'
                else:
                    links_for_archive_list += f'        <li><a href="./{url}">{pagename} - {date}</a></li>\n'
                former = date[:-3]

    links_for_index_html += '    </ul class="url-list">'
    links_for_archive_list += '      </ul></li>\n    </ul class="archive">'

    with open(TEMPLATE_DIR/"blog-index-template.html") as file:
        old_index_html_file = file.read()

        new_index_html_file = re.sub('<ul class="url-list">.*</ul class="url-list">',links_for_index_html, old_index_html_file,flags=re.DOTALL)
        new_index_html_file = re.sub('<ul class="archive">.*</ul class="archive">',links_for_archive_list, new_index_html_file,flags=re.DOTALL)

    with open(OUTPUT_DIR/"blog/index.html", mode="w") as file:
        file.write(new_index_html_file)


def edit_url_and_title():
    for category in ["./works/*/*.html","./blog/*/*.html"]:
        files = glob.glob( str(OUTPUT_DIR/category) )
        
        for url in files:
            with open(url) as file:
                nakami = file.read()

                pagename = re.sub("</h1>.*", "",re.sub(".*<h1>","",nakami.replace('\n',' ')))

                if url[-10:] == "index.html":
                    shorturl = url[:-11]
                else:
                    shorturl = url

                metatag = "\n    <meta property=\"og:url\" content=\"https://lnln.dev/" + re.sub("\./","",shorturl) \
                    + "\">\n    <meta property=\"og:title\" content=\"" + pagename + "\">\n"\
                    + "    <title>" + pagename + "</title>"

                onew = re.sub("<!--置換用タグ1-->.*<!--置換用タグ2-->",metatag,nakami,flags=re.DOTALL)

            
            with open( url, mode="w" ) as file:
                file.write(onew)


if __name__ == "__main__":
    #   mkdir dist
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    convert_md()
    put_index_file()

    edit_url_and_title()

    for file in ["404.html", "CNAME", "index.html"]:
        copyfile( SRC_DIR/file, OUTPUT_DIR/file )