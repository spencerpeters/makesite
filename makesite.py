#!/usr/bin/env python

# The MIT License (MIT)
#
# Copyright (c) 2018-2022 Sunaina Pai
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""Make static website/blog with Python."""

# spencer: to deploy, connect to Cornell network, and run
# rsync -ave 'ssh' _site/* sp2473@linux.coecis.cornell.edu:/cs/people/sp2473

import os
import shutil
import re
import glob
import sys
import json
import datetime

serve_locally = False

def fread(filename):
    """Read file and close the file."""
    with open(filename, 'r') as f:
        return f.read()


def fwrite(filename, text):
    """Write content to file and close the file."""
    basedir = os.path.dirname(filename)
    if not os.path.isdir(basedir):
        os.makedirs(basedir)

    with open(filename, 'w') as f:
        f.write(text)


def log(msg, *args):
    """Log message with specified arguments."""
    sys.stderr.write(msg.format(*args) + '\n')


def truncate(text, words_to_keep=25):
    """Remove tags and truncate text to the specified number of words."""
    return ' '.join(re.sub('(?s)<.*?>', ' ', text).split()[:words_to_keep])


def read_headers(text):
    """Parse headers in text and yield (key, value, end-index) tuples."""
    for match in re.finditer(r'\s*<!--\s*(.+?)\s*:\s*(.+?)\s*-->\s*|.+', text):
        if not match.group(1):
            break
        yield match.group(1), match.group(2), match.end()


def rfc_2822_format(date_str):
    """Convert yyyy-mm-dd date string to RFC 2822 format date string."""
    d = datetime.datetime.strptime(date_str, '%Y-%m-%d')
    return d.strftime('%a, %d %b %Y %H:%M:%S +0000')


def read_content(filename):
    """Read content and metadata from file into a dictionary."""
    # Read file content.
    text = fread(filename)

    # Read metadata and save it in a dictionary.
    date_slug = os.path.basename(filename).split('.')[0]
    match = re.search(r'^(?:(\d\d\d\d-\d\d-\d\d)-)?(.+)$', date_slug)
    content = {
        'date': match.group(1) or '1970-01-01',
        'slug': match.group(2),
    }

    # Read headers.
    end = 0
    for key, val, end in read_headers(text):
        content[key] = val

    # Separate content from headers.
    text = text[end:]

    # Convert Markdown content to HTML.
    if filename.endswith(('.md', '.mkd', '.mkdn', '.mdown', '.markdown')):
        try:
            if _test == 'ImportError':
                raise ImportError('Error forced by test')
            import commonmark
            text = commonmark.commonmark(text)
        except ImportError as e:
            log('WARNING: Cannot render Markdown in {}: {}', filename, str(e))

    # Update the dictionary with content and RFC 2822 date.
    content.update({
        'content': text,
        'rfc_2822_date': rfc_2822_format(content['date'])
    })

    return content


def render(template, **params):
    """Replace placeholders in template with values from params."""
    return re.sub(
        r'{{\s*([^}\s]+)\s*}}',
        lambda match: str(params.get(match.group(1), match.group(0))),
        template)


def make_pages(src, dst, layout, **params):
    """Generate pages from page content."""
    items = []

    for src_path in glob.glob(src):
        content = read_content(src_path)

        page_params = dict(params, **content)

        # Populate placeholders in content if content-rendering is enabled.
        if page_params.get('render') == 'yes':
            rendered_content = render(page_params['content'], **page_params)
            page_params['content'] = rendered_content
            content['content'] = rendered_content

        items.append(content)

        dst_path = render(dst, **page_params)
        output = render(layout, **page_params)

        log('Rendering {} => {} ...', src_path, dst_path)
        fwrite(dst_path, output)

    return sorted(items, key=lambda x: x['date'], reverse=True)


def make_list(posts, dst, list_layout, item_layout, **params):
    """Generate list page for a blog."""
    items = []
    for post in posts:
        # spencer: one-off to make this more private
        # print(post)
        if post["title"] != "Spencer's 27th Birthday":
            item_params = dict(params, **post)
            item_params['summary'] = truncate(post['content'])
            item = render(item_layout, **item_params)
            items.append(item)

    # pre_content = params['pre_content'] if 'pre_content' in params else ''
    # post_content = params['post_content'] if 'post_content' in params else ''

    # params['content'] = pre_content + ''.join(items) + post_content
    params['content'] = ''.join(items)
    dst_path = render(dst, **params)
    output = render(list_layout, **params)

    log('Rendering list => {} ...', dst_path)
    fwrite(dst_path, output)

def main():
    # Create a new _site directory from scratch.
    if os.path.isdir('_site'):
        shutil.rmtree('_site')
    shutil.copytree('static', '_site')

    # Default parameters.
    if serve_locally:
        base_path = ''
        site_url = 'http://localhost:8000'
    elif serve_cloudflare:
        base_path = ''
        site_url = 'https://8faecffb.makesite.pages.dev'
    else:
        base_path = '/~speters'
        site_url = 'https://www.cs.cornell.edu'
    params = {
        # 'base_path': '',
        # 'site_url': 'http://localhost:8000',
        # 'base_path': '/~speters',
        # 'site_url': 'https://www.cs.cornell.edu',
        'base_path': base_path,
        'site_url': site_url,
        'subtitle': 'Spencer Peters',
        'author': 'Spencer Peters',
        # Alright, this is a job for the weekend.
        # Note: rsync copies directory permissions, which on the new Mac are less permissive
        # so some files are not used by the department server. Changing all permissions to 777
        # fixed the problem, but maybe not for the new files?
        # A third problem is that markdown files aren't being rendered correctly into the blog and journal.
        # Links aren't rendering. Not sure why. Gotta check the rendering pipeline.
        'current_year': datetime.datetime.now().year
    }

    # If params.json exists, load it.
    if os.path.isfile('params.json'):
        params.update(json.loads(fread('params.json')))

    # Load layouts.
    page_layout = fread('layout/page.html')
    post_layout = fread('layout/post.html')
    list_layout = fread('layout/list.html')
    item_layout = fread('layout/item.html')
    preview_item_layout = fread('layout/preview_item.html')
    feed_xml = fread('layout/feed.xml')
    item_xml = fread('layout/item.xml')

    # Combine layouts to form final layouts.
    post_layout = render(page_layout, content=post_layout)
    list_layout = render(page_layout, content=list_layout)

    # Create blog and journal.
    blog_posts = make_pages('content/blog/*.md',
                            '_site/blog/{{ slug }}/index.html',
                            post_layout,
                            blog='blog',
                            **params)
    journal_posts = make_pages('content/journal/*.md',
                               '_site/journal/{{ slug }}/index.html',
                               post_layout,
                               blog='news',
                               **params)

    # Make most recent post preview for home page
    most_recent_blog_post = blog_posts[0] if blog_posts[0]["title"] != "Spencer's 27th Birthday" else blog_posts[1]
    post_params = dict(params, **most_recent_blog_post)
    post_params['summary'] = truncate(most_recent_blog_post['content'])
    item_for_post = render(preview_item_layout, **post_params)

    # Create site pages.
    make_pages('content/_index.html',
                      '_site/index.html',
                      page_layout,
                      most_recent_post=item_for_post,
                      render="yes",
                      **params)
    make_pages('content/[!_]*.html', '_site/{{ slug }}/index.html',
               page_layout, render="yes", **params)

    # Added for bookshelf.md
    make_pages('content/[!_]*.md', '_site/{{ slug }}/index.html',
               page_layout, render="yes", **params)

    # Create blog list pages.
    make_list(blog_posts,
              '_site/blog/index.html',
              list_layout,
              item_layout,
              blog='blog',
              title='Blog',
              **params)
    make_list(journal_posts,
              '_site/journal/index.html',
              list_layout,
              item_layout,
              blog='journal',
              title='Journal',
              **params)

    # Create RSS feeds.
    make_list(blog_posts,
              '_site/blog/rss.xml',
              feed_xml,
              item_xml,
              blog='blog',
              title='Blog',
              **params)
    make_list(journal_posts,
              '_site/news/rss.xml',
              feed_xml,
              item_xml,
              blog='journal',
              title='Journal',
              **params)


# Test parameter to be set temporarily by unit tests.
_test = None

if __name__ == '__main__':
    print(f"argv = {sys.argv}")
    if len(sys.argv) > 1:
        if sys.argv[1] == "local":
            print("local!")
            serve_locally = True
        elif sys.argv[1] == "cloudflare":
            print("cloudflare!")
            serve_cloudflare = True
    main()
