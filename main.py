#!/bin/python3

import re
from shutil import copytree, copyfile, rmtree
from pathlib import Path
import markdown
from bs4 import BeautifulSoup
from works_css import tailwindcss_dict
from PIL import Image

NUMBER_OF_LATEST_BLOG = 3

SRC_DIR = Path("./src")
OUTPUT_DIR = Path("./dist")
TEMPLATE_DIR = Path("./templates")


def convert_jpeg_to_webp_with_low_quality(input_file_path: Path, output_file_path: Path, quality=10):
    # 画像を開く
    with Image.open(input_file_path) as img:
        # WebP形式に変換して保存
        img.save(output_file_path, 'webp', quality=quality)

def remove_top_dir(p: Path) -> Path:
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

        small_img_src = f"small-{Path(img_src).with_suffix('.webp')}"

        new_tag_str = f'''
        <figure class="m-4">
          <div class="flex items-center justify-center">
            <a href="{img_src}"><img class="w-auto rounded-lg" src="{small_img_src}"></a>
          </div>
          <figcaption class="text-center mt-2">図{index + 1} {alt_text}</figcaption>
        </figure>
        '''
        new_tag = BeautifulSoup(new_tag_str, 'lxml')
        img_tag.replace_with(new_tag)
    
    return soup.prettify()

def add_table_centering(input_html):
    soup = BeautifulSoup(input_html, 'lxml')
    table_tags = soup.find_all('table')

    for table_tag in table_tags:
        div = soup.new_tag('div', attrs={'class': 'flex items-center justify-center'})
        table_tag.wrap(div)
    
    return soup.prettify()

def convert_md(category_name: Path):
    markdown_obj = markdown.Markdown(extensions=['fenced_code', 'tables', 'nl2br'])

    # ls blog html files
    src_file_pattern = category_name / "*" / "*.md"
    md_files = sorted(SRC_DIR.glob(str(src_file_pattern)), reverse=True)

    for index, md_file_path in enumerate(md_files):
        with open(md_file_path) as file:
            md_text = file.read()
            html = markdown_obj.convert(md_text)

            md_file_path = remove_top_dir(md_file_path)
            
            template_file_name = Path(f"{category_name}-template.html")
            with open(TEMPLATE_DIR/template_file_name, mode="r") as template:
                html_template = template.read()

                html = replace_img_to_figure(html)
                html = add_table_centering(html)
                html = add_tailwind_class(html)

                html = html_template.replace("<!--ContentTag-->", html)

                if category_name == Path("blog"):
                    html = html.replace("<!--DateTag-->", md_file_path.parts[-2])

            output_path = OUTPUT_DIR / md_file_path.parent / "index.html"
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, mode="w") as file:
                if (OUTPUT_DIR / md_file_path).exists():
                    (OUTPUT_DIR / md_file_path).unlink()
                file.write(html)

def put_blog_index_file():
    url_paths = sorted([p for p in OUTPUT_DIR.glob("blog/*") if p.is_dir()], reverse=True)

    links_for_index_html ='<ul class="list-disc m-4">\n'
    links_for_archive_list = '<ul class="list-disc m-4">\n'
    first = True
    
    for index, url in enumerate(url_paths):
        with open(url / "index.html") as file:
            url = remove_top_dir(url)
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
    target_file_pattern = "works/*/*.md"
    url_paths = sorted([p for p in SRC_DIR.glob(target_file_pattern)], key=lambda x: x.name, reverse=True)
    url_paths = [remove_top_dir(path) for path in url_paths]

    html = ''

    for index, url in enumerate(url_paths):
        url = url.parent
        with open(OUTPUT_DIR/url/"index.html") as file:
            target_index_html = file.read()

            thumbnail_paths = list(OUTPUT_DIR.glob(str(url/"small-thumbnail.webp")))
            thumbnail_path = url/"small-thumbnail.webp" if thumbnail_paths else ""

            soup = BeautifulSoup(target_index_html, 'lxml')
            h1_tags = soup.find_all('h1')

            for h1_tag in h1_tags:
                pagename = h1_tag.get_text(strip=True)

            page_description = re.sub("description-->.*", "",re.sub(".*<!--description","",target_index_html.replace('\n',' ')))

            html += f'''
            <div class="w-96 m-4">
              <a href="./{url}">
                <img src="./{thumbnail_path}" alt="サムネイル" class="w-full aspect-[4/3] object-cover rounded-lg">
              </a>
              <h3 class="mt-2 text-xl font-bold text-center text-cyan-600">{pagename}</h3>
              <p class="p-2">{page_description}</p>
            </div>
            '''

    with open(TEMPLATE_DIR/"works-index-template.html") as file:
        old_index_html_file = file.read()
        new_index_html_file = re.sub('<!--ContentLink-->',html, old_index_html_file,flags=re.DOTALL)

    with open(OUTPUT_DIR/"index.html", mode="w+") as file:
        file.write(new_index_html_file)

def edit_url_and_title(category_name: Path):
    target_file_pattern = category_name / "*" / "*.html"
    files = OUTPUT_DIR.glob(str(target_file_pattern))
    
    for url in files:
        with open(url) as file:
            nakami = file.read()

            soup = BeautifulSoup(nakami, 'lxml')
            h1_tags = soup.find_all('h1')

            for h1_tag in h1_tags:
                pagename = h1_tag.get_text(strip=True)

            if url.name == "index.html":
                shorturl = url.parent
            else:
                shorturl = url

            metatag = "\n    <meta property=\"og:url\" content=\"https://lnln.dev/" + str(shorturl.relative_to(OUTPUT_DIR)) \
                + "\">\n    <meta property=\"og:title\" content=\"" + pagename + "\">\n"\
                + "    <title>" + pagename + "</title>\n"

            if (url.parent/"thumbnail.jpg").exists():
                metatag += '''
                <meta name="twitter:card" content="summary_large_image">
                <meta name="twitter:site" content="@lnln_ch">
                <meta property="og:description" content="趣味の工作の記録">
                <meta property="og:image" content="https://lnln.dev/{remove_top_dir(url.parent)}/small-thumbnail.webp">
                '''
            else:
                metatag += '''
                <meta name="twitter:card" content="summary">
                <meta name="twitter:site" content="@lnln_ch">
                <meta property="og:description" content="趣味の工作の記録">
                <meta property="og:image" content="https://lnln.dev/img/title.png">
                '''

            onew = re.sub("<!--MetaTag-->",metatag,nakami,flags=re.DOTALL)

        with open(url, mode="w") as file:
            file.write(onew)

if __name__ == "__main__":
    if OUTPUT_DIR.exists():
        rmtree(OUTPUT_DIR)
    
    OUTPUT_DIR.mkdir()
    
    for category in ["css", "works", "blog", "img"]:
        copytree(SRC_DIR/category, OUTPUT_DIR/category)

    for category in ["works", "blog"]:
        convert_md(Path(category))
        edit_url_and_title(Path(category))

        for path in (OUTPUT_DIR/category).glob("**/*.jpg"):
            if path.is_file():
                output_file_path = path.parent / f"small-{path.stem}.webp"
                convert_jpeg_to_webp_with_low_quality(path, output_file_path, 10) 

        for path in (OUTPUT_DIR/category).glob("**/*.png"):
            if path.is_file():
                output_file_path = path.parent / f"small-{path.stem}.webp"
                convert_jpeg_to_webp_with_low_quality(path, output_file_path, 10) 

    put_blog_index_file()
    put_works_index_file()

    for file in ["404.html", "profile.html", "lnln_ch_icon.jpg", "CNAME"]:
        copyfile(SRC_DIR/file, OUTPUT_DIR/file)