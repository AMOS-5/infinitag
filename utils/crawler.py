# InfiniTag Copyright © 2020 AMOS-5
# Permission is hereby granted,
# free of charge, to any person obtaining a copy of this software and
# associated documentation files (the "Software"), to deal in the Software
# without restriction, including without limitation the rights to use, copy,
# modify, merge, publish, distribute, sublicense, and/or sell copies of the
# Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions: The above copyright notice and this
# permission notice shall be included in all copies or substantial portions
# of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN
# NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE
# USE OR OTHER DEALINGS IN THE SOFTWARE.

import requests
import atoma
from argparse import ArgumentParser
from typing import List
from tqdm.auto import tqdm
import os
from time import sleep
import xml.etree.ElementTree as ET
import json
from utils.crawler_dict import categories


def crawl_arxiv(categories: List[str], max_results: int = 1000,
                sleep_time: int = 5,
                fetch_size: int = 100, output: str = '.'):
    docs = []
    base_url = 'http://export.arxiv.org/api/query?'
    base_oai = 'http://export.arxiv.org/oai2?verb=GetRecord&identifier=oai:arXiv.org:{}&metadataPrefix=arXiv'
    oai_tag = '{http://www.openarchives.org/OAI/2.0/}'
    meta_list = []
    for category in categories:
        print('Looking up papers in {}'.format(category))
        url = "{}search_query=cat:{}&max_results={}&sortBy=lastUpdatedDate&sortOrder=descending".format(
            base_url, category, max_results)
        response = requests.get(url)
        feed = atoma.parse_atom_bytes(response.content)
        entries = feed.entries

        for entry in tqdm(entries):
            entry_link = entry.id_
            entry_index = entry_link.rfind('/')
            entry_id = entry_link[entry_index + 1:]
            version_marker = entry_id.rfind('v')
            entry_id = entry_id[:version_marker]
            oai_url = base_oai.format(entry_id)

            metadata_response = requests.get(oai_url)
            if metadata_response.status_code == 200:
                metadata = metadata_response.text
                root = ET.fromstring(metadata)
                record = root.find('{}GetRecord'.format(oai_tag))
                if record is not None:
                    license_link = find_license(record)
                    if is_cc_license(license_link):
                        setattr(entry, 'license', license_link)
                        meta = download_document(entry, output)
                        docs.append(entry)

                        meta_list.append(meta)
                        if len(docs) >= fetch_size:
                            break

            sleep(sleep_time)

        if len(docs) >= fetch_size:
            print("I found what I was looking for. We can stop searching.")
            break
    print('Found {} documents'.format(len(docs)))
    with open('{}/meta.json'.format(output), 'w') as fout:
        json.dump(meta_list, fout)

    return docs, meta_list


def is_cc_license(link_url):
    cc_license_link = 'http://creativecommons.org/licenses/'
    return cc_license_link in link_url


def download_document(entry, output):
    entry_link = entry.id_
    entry_index = entry_link.rfind('/')
    entry_id = entry_link[entry_index + 1:]
    links = entry.links
    categories = []
    for category in entry.categories:
        categories.append(category.term)
    for link in links:
        if link.title == 'pdf':
            file = requests.get(link.href)
            with open('{}/{}.pdf'.format(output, entry_id), 'wb') as pdf:
                pdf.write(file.content)
    meta = {
        'id': entry_id,
        'published': entry.published.strftime("%d-%m-%Y::%H:%M:%S"),
        'categories': categories,
        'link': entry.id_,
        'title': entry.title.value,
        'license': entry.license

    }
    sleep(5)
    return meta


def find_license(record):
    open_archives_tag = '{http://www.openarchives.org/OAI/2.0/}'
    arxiv_tag = '{http://arxiv.org/OAI/arXiv/}'
    try:
        record = record.find('{}record'.format(open_archives_tag))
        metadata = record.find('{}metadata'.format(open_archives_tag))
        arxiv = metadata.find('{}arXiv'.format(arxiv_tag))
        license_tag = arxiv.find('{}license'.format(arxiv_tag))
        return license_tag.text

    except:
        return ""


def category_crawler(output_dir):
    for category_key, category_name in categories:
        dir = os.path.join(output_dir, category_name)
        if not os.path.isdir(dir):
            os.makedirs(dir)

        crawl_arxiv([category_key], max_results=200, fetch_size=100, output=dir)


def crawl_gov(type: str, count: int, output: str = '.'):
    base_url = 'http://catalog.data.gov/api/3/action/package_search?q=res_format:{}&rows={}'.format(
        type, count)
    response = requests.get(base_url).json()

    result_dict = response['result']
    results = result_dict['results']
    for result in results:
        license_title = result['license_title']
        if license_title is not None and 'Creative Commons' in license_title:
            resources = result['resources']
            for resource in resources:
                if resource['format'] == type:
                    url = resource['url']
                    try:
                        file = requests.get(url)
                        path = os.path.join(output, resource['name'])
                        with open(path, 'wb') as f:
                            f.write(file.content)
                        sleep(5)
                    except Exception:
                        pass


if __name__ == "__main__":
    parser = ArgumentParser(description="Document Finder")
    parser.add_argument("--all", type=bool, default=False)
    parser.add_argument("--categories", type=str, default='cs.CR')
    parser.add_argument("--max_results", type=int, default=1000)
    parser.add_argument("--source", type=str, default="arxiv")
    parser.add_argument("--sleep_time", type=int, default=5)
    parser.add_argument("--fetch_size", type=int, default=100)
    parser.add_argument("--document_output", type=str, default="output")
    parser.add_argument("--document_type", type=str, default="pdf")
    args = parser.parse_args()

    if not os.path.isdir(args.document_output):
        os.makedirs(args.document_output)


    if args.all:
        category_crawler(args.document_output)
    elif args.source == "arxiv":
        crawl_arxiv(categories=args.categories.split(),
                    max_results=args.max_results,
                    sleep_time=max(5, args.sleep_time),
                    fetch_size=args.fetch_size,
                    output=args.document_output)
    elif args.source == "gov":
        crawl_gov(type=args.document_type,
                  count=args.max_results,
                  output=args.document_output)

    else:
        print("Only arxiv and gov are supported as sources at the moment")
