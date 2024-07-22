#!/bin/python3

import glob
import re
import os
from shutil import copytree, copyfile, rmtree
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
from works_css import tailwindcss_dict

NUMBER_OF_LATEST_BLOG = 3

SRC_DIR = Path("./src")
OUTPUT_DIR = Path("./dist")
TEMPLATE_DIR = Path("./templates")


def remove_top_dir(p:Path):
    return p.relative_to(p.parts[0])

def add_tailwind_class(html):
    soup = BeautifulSoup(html, 'lxml')

    for key in tailwindcss_dict.keys():

        founded_tags = soup.find_all(key)
        for tag in founded_tags:

            if 'class' not in tag.attrs:
                tag['class'] = tailwindcss_dict[key]
            else:
                tag['class'].append(tailwindcss_dict[key])

    return soup.prettify()

def replace_img_to_figure(input_html):
    soup = BeautifulSoup(input_html, 'lxml')
    img_tags = soup.find_all('img')

    for index, img_tag in enumerate(img_tags):
        alt_text = img_tag.get('alt', '')
        img_src = img_tag.get('src', '')
        
        new_tag_str = f'<figure class="m-4"><div class="flex items-center justify-center"><a href="{img_src}"><img class="w-auto rounded-lg" src="{img_src}"></a></div><figcaption class="text-center mt-2">図{index + 1} {alt_text}</figcaption></figure>'

        new_tag = BeautifulSoup(new_tag_str, 'lxml')
        img_tag.replace_with(new_tag)
    
    # Return the new HTML as a string
    return soup.prettify()

def add_table_centering(input_html):
    soup = BeautifulSoup(input_html, 'lxml')
    table_tags = soup.find_all('table')

    for table_tag in table_tags:
        
        new_tag_str = f'<div class="flex items-center justify-center">{table_tag.prettify()}</div>'

        new_tag = BeautifulSoup(new_tag_str, 'lxml')
        table_tag.replace_with(new_tag)
    
    return soup.prettify()

def convert_md(category_name:Path):
    markdown_obj = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])

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

                html = replace_img_to_figure(html)
                html = add_table_centering(html)
                html = add_tailwind_class(html)

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

    links_for_index_html ='<ul class="list-disc m-4">\n'
    links_for_archive_list = '<ul class="list-disc m-4">\n'
    first = True
    
    for index, url in enumerate(url_paths):
        #ファイルを開いて
        with open(url + "/index.html") as file:
            url = remove_top_dir(Path(url))
            url = remove_top_dir(url)
            url = str(url)
            nakami = file.read()

            soup = BeautifulSoup(nakami, 'lxml')
            h1_tags = soup.find_all('h1')

            for h1_tag in h1_tags:
                pagename = h1_tag.get_text(strip=True) 

            date = url[-10:]
            date = re.sub("-","/",date)

            if index < NUMBER_OF_LATEST_BLOG:
                links_for_index_html += f'''
                <li><a class="text-cyan-600" href="./{url}">{pagename} - {date}</a></li>
                '''

            if first:
                links_for_archive_list += f'''
                <details class="cursor-pointer"><summary>{date[:-3]}</summary>
                  <li class="ml-6"><a class="text-cyan-600" href="./{url}">{pagename} - {date}</a></li>
                '''
                first = False
            elif former != date[:-3]:
                links_for_archive_list += f'''
                </details>
                <details class="cursor-pointer"><summary>{date[:-3]}</summary>
                  <li class="ml-6"><a class="text-cyan-600" href="./{url}">{pagename} - {date}</a></li>
                '''
            else:
                links_for_archive_list += f'''
                <li class="ml-6"><a class="text-cyan-600" href="./{url}">{pagename} - {date}</a></li>
                '''
            former = date[:-3]

    links_for_index_html += '    </ul>'
    links_for_archive_list += '      </ul></li>\n    </ul>'

    with open(TEMPLATE_DIR/"blog-index-template.html") as file:
        old_index_html_file = file.read()

        new_index_html_file = re.sub('<ul class="url-list">.*</ul class="url-list">',links_for_index_html, old_index_html_file,flags=re.DOTALL)
        new_index_html_file = re.sub('<ul class="archive">.*</ul class="archive">',links_for_archive_list, new_index_html_file,flags=re.DOTALL)

    with open(OUTPUT_DIR/"blog/index.html", mode="w") as file:
        file.write(new_index_html_file)


def put_works_index_file():
    target_file_path = Path(SRC_DIR/"works/*/*.md")
    url_paths_str:str = glob.glob( str(target_file_path) )

    url_paths = [Path(p) for p in url_paths_str]

    # url_paths.sort(reverse=True)
    url_paths = sorted(url_paths, key=lambda x: x.name, reverse=True)

    #url_paths = [path for path in url_paths if not os.path.isfile(path)]

    url_paths = [remove_top_dir(path) for path in url_paths]

    html = ''

    for index, url in enumerate(url_paths):
        url = url.parent
        #ファイルを開いて
        with open(OUTPUT_DIR/url/"index.html") as file:
            target_index_html = file.read()

            thumbnail_paths = glob.glob( str(OUTPUT_DIR/url/"*thumbnail.*") )
            if len(thumbnail_paths) == 0:
                thumbnail_path = ""
            else:
                thumbnail_path = str( remove_top_dir(Path(thumbnail_paths[0])) )


            # get title
            soup = BeautifulSoup(target_index_html, 'lxml')
            h1_tags = soup.find_all('h1')

            for h1_tag in h1_tags:
                pagename = h1_tag.get_text(strip=True)
                

            # get description
            page_description = re.sub("description-->.*", "",re.sub(".*<!--description","",target_index_html.replace('\n',' ')))

            html += '<div class="w-96 m-4">\n'
            html += f'  <a href="./{url}"><img src="./{thumbnail_path}" alt="サムネイル" class="w-full aspect-[4/3] object-cover rounded-lg">'
            html += '\n'
            html += f'    <h3 class="mt-2 text-xl font-bold text-center text-cyan-600">{pagename}</h3>'
            html += '\n'
            html += '  </a>\n'
            html += f'  <p class="p-2">{page_description}</p>'
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

            soup = BeautifulSoup(nakami, 'lxml')
            h1_tags = soup.find_all('h1')

            for h1_tag in h1_tags:
                pagename = h1_tag.get_text(strip=True)

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
    if os.path.exists(OUTPUT_DIR):
        rmtree(OUTPUT_DIR)
    
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