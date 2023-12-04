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


def convert_md(category_name:Path):
    markdown_obj = markdown.Markdown(extensions=['fenced_code', 'tables'])

    # ls blog html files
    src_file_name = Path(category_name + "/*/*.md")

    md_files = glob.glob( str(SRC_DIR/src_file_name) )
    md_files.sort(reverse=True) #key=os.path.getmtime, 

    for index, md_file_path in enumerate(md_files):

        with open(md_file_path) as file:
            md_text = file.read()
            html = markdown_obj.convert(md_text)

            md_file_path = remove_top_dir( Path(md_file_path) )
            
            template_file_name = Path(category_name + "-template.html")
            with open(TEMPLATE_DIR/template_file_name, mode="r") as template:
                html_template = template.read()
                html = html_template.replace("<!--ContentTag-->",html)

                if category_name == "blog":
                    html = html.replace("<!--DateTag-->",md_file_path.parts[-2])

            with open(OUTPUT_DIR/md_file_path.parent/"index.html", mode="w") as file:
                #print(OUTPUT_DIR/md_file_path/md_file_name.with_suffix('.html'))
                os.remove(OUTPUT_DIR/md_file_path.with_suffix('.md'))
                file.write(html)


def put_blog_index_file():
    # ls blog html files
    url_paths = glob.glob( str(OUTPUT_DIR/"blog/*") )
    url_paths.sort(reverse=True)

    url_paths = [path for path in url_paths if not os.path.isfile(path)]

    links_for_index_html ='<ul class="url-list">\n'
    links_for_archive_list = '<ul class="archive">\n'
    first = True
    
    for index, url in enumerate(url_paths):
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


def put_works_index_file():
    target_file_path = Path(SRC_DIR/"works/*")
    url_paths = glob.glob( str(target_file_path) )
    url_paths.sort(key=os.path.getmtime, reverse=True)

    url_paths = [path for path in url_paths if not os.path.isfile(path)]

    url_paths = [remove_top_dir(Path(path)) for path in url_paths]

    html = ''

    for index, url in enumerate(url_paths):
        #ファイルを開いて
        with open(OUTPUT_DIR/url/"index.html") as file:
            target_index_html = file.read()

            # get title
            pagename = re.sub("</h1>.*", "",re.sub(".*<h1>","",target_index_html.replace('\n',' ')))
            page_description = re.sub("description-->.*", "",re.sub(".*<!--description","",target_index_html.replace('\n',' ')))

            html += '<div class="item">\n'
            html += f'  <a href="./{url}"><img src="./{url}/small-thumbnail.jpg" alt="サムネイル"><br>'
            html += '\n'
            html += f'    {pagename}'
            html += '\n'
            html += '  </a>\n'
            html += f'  <p>{page_description}</p>'
            html += '</div>\n\n'

    #print(html)
    with open(TEMPLATE_DIR/"works-index-template.html") as file:
        old_index_html_file = file.read()

        new_index_html_file = re.sub('<!--ContentLink-->',html, old_index_html_file,flags=re.DOTALL)

        #print(new_index_html_file)

    with open(OUTPUT_DIR/"index.html", mode="w+") as file:
        file.write(new_index_html_file)

def edit_url_and_title(category_name:Path):
    target_file_path = Path(category_name + "/*/*.html")
    files = glob.glob( str(OUTPUT_DIR/target_file_path) )
    
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
                + "    <title>" + pagename + "</title>\n"

            if os.path.exists(Path(url).parent/"small-thumbnail.jpg"):
                metatag += '    <meta name="twitter:card" content="summary_large_image">\n'
                metatag += '    <meta name="twitter:site" content="@lnln_ch">\n'
                metatag += '    <meta property="og:description" content="趣味の工作の記録">\n'
                metatag += f'    <meta property="og:image" content="https://lnln.dev/{remove_top_dir( Path(url).parent )}/small-thumbnail.jpg">\n'
            elif os.path.exists(Path(url).parent/"thumbnail.jpg"):
                metatag += '    <meta name="twitter:card" content="summary_large_image">\n'
                metatag += '    <meta name="twitter:site" content="@lnln_ch">\n'
                metatag += '    <meta property="og:description" content="趣味の工作の記録">\n'
                metatag += f'    <meta property="og:image" content="https://lnln.dev/{remove_top_dir( Path(url).parent )}/thumbnail.jpg">\n'
            else:
                metatag += '    <meta name="twitter:card" content="summary">\n'
                metatag += '    <meta name="twitter:site" content="@lnln_ch">\n'
                metatag += '    <meta property="og:description" content="趣味の工作の記録">\n'
                metatag += '    <meta property="og:image" content="https://lnln.dev/img/title.png">\n'


            onew = re.sub("<!--MetaTag-->",metatag,nakami,flags=re.DOTALL)

        
        with open( url, mode="w" ) as file:
            file.write(onew)


if __name__ == "__main__":
    #   mkdir dist
    if not os.path.exists(OUTPUT_DIR):
        os.mkdir(OUTPUT_DIR)
    
    for category in ["css", "works", "blog", "img"]:
        files = glob.glob( str(SRC_DIR/category) )
        for url in files:
            url = Path(url)
            url = remove_top_dir(url)
            copytree(SRC_DIR/url, OUTPUT_DIR/url )

    for category in ["works", "blog"]:
        convert_md(category)
        #put_index_file()
        edit_url_and_title(category)
    

    put_blog_index_file()
    put_works_index_file()

    #edit_url_and_title(category)

    for file in ["404.html", "CNAME"]:
        copyfile( SRC_DIR/file, OUTPUT_DIR/file )