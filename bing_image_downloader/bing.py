from pathlib import Path
import os
import sys
import urllib.request
import urllib.parse
import urllib
import imghdr
import posixpath
import re

'''
Python api to download image form Bing.
Author: Guru Prasad (g.gaurav541@gmail.com)
'''


class Bing():

    def __init__(self):
        self.download_count = 0
        self.headers = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}

    def handle_non_ascii_url(self, url):
        u = urllib.parse.urlparse(url)
        new_url = u._replace(path=urllib.parse.quote(u.path, safe='/%')).geturl()
        print(f'[%] Non ascii replace {new_url}')
        return new_url

    def save_image(self, link, file_path):
        request = urllib.request.Request(self.handle_non_ascii_url(link), None, self.headers)
        image = urllib.request.urlopen(request).read()
        if not imghdr.what(None, image):
            print('[Error]Invalid image, not saving {}\n'.format(link))
            raise
        with open(file_path, 'wb') as f:
            f.write(image)

    def download_image(self, link, query, output_dir):
        self.download_count += 1

        # Get the image link
        try:
            path = urllib.parse.urlsplit(link).path
            filename = posixpath.basename(path).split('?')[0]
            file_type = filename.split(".")[-1]
            if file_type.lower() not in ["jpe", "jpeg", "jfif", "exif", "tiff", "gif", "bmp", "png", "webp", "jpg"]:
                file_type = "jpg"

            # Download the image
            print("[%] Downloading Image #{} from {}".format(self.download_count, link))

            self.save_image(link, "{}/{}/{}/".format(os.getcwd(), output_dir, query) + "Image_{}.{}".format(
                str(self.download_count), file_type))
            print("[%] File Downloaded !\n")
        except Exception as e:
            self.download_count -= 1
            print("[!] Issue getting: {}\n[!] Error:: {}".format(link, e))

    def bing(self, query, limit, output_dir, adlt='off', filters=''):

        limit = int(limit)
        page_counter = 0

        while self.download_count < limit:
            print('\n\n[!!]Indexing page: {}\n'.format(page_counter + 1))
            # Parse the page source and download pics
            request_url = 'https://www.bing.com/images/async?q=' + urllib.parse.quote_plus(query) + '&first=' + str(
                page_counter) + '&count=' + str(limit) + '&adlt=' + adlt + '&qft=' + filters
            request = urllib.request.Request(request_url, None, headers=self.headers)
            response = urllib.request.urlopen(request)
            html = response.read().decode('utf8')
            links = re.findall('murl&quot;:&quot;(.*?)&quot;', html)

            print("[%] Indexed {} Images on Page {}.".format(len(links), page_counter + 1))
            print("\n===============================================\n")

            for link in links:
                if self.download_count < limit:
                    self.download_image(link, query, output_dir)
                else:
                    print("\n\n[%] Done. Downloaded {} images.".format(self.download_count))
                    print("\n===============================================\n")
                    break

            page_counter += 1
