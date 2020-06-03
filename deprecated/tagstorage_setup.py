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

try:
    # uses the config from this folder for the general setup
    import config
except:
    # we run the testcase / other
    pass

import os
import shutil
import pysolr
from pathlib import Path
from urlpath import URL
import json

"""
This file is experimental and was used to setup a local Solr instance.
We have already changed that and setup a remote instance for everybody.
Still this file contains some useful informations on how a Solr core can be setup
remotely.
"""


def get_default_config_dir(solr_home: Path):
    return solr_home / "configsets" / "_default" / "conf"


def get_solr_home():
    try:
        solr_home = Path(os.environ["SOLR_HOME"])
    except:
        raise ValueError(
            "You have not set the SOLR_HOME environment variable!\n"
            "export SOLR_HOME='SOLR_ROOT/server/solr'"
        )

    return solr_home


def print_status(result: dict, corename: str):
    if result["responseHeader"]["status"] == 0:
        print(f"Core with name '{corename}' created.")
    else:  # we are maybe good (core exists), or error
        print(result["error"]["msg"])


def create_admin(url: URL):
    admin_url = url / "admin" / "cores"
    admin = pysolr.SolrCoreAdmin(admin_url)
    return admin


def create_core(config: dict):
    corename = config["corename"]
    solr_home = get_solr_home()
    default_dir = get_default_config_dir(solr_home)
    working_dir = solr_home / corename
    try:
        shutil.copytree(default_dir, working_dir)
    except FileExistsError:
        # the core has already been created once,
        # we don't bother and use the old config
        pass

    base_url = URL(config["url"])
    admin = create_admin(base_url)

    # create a core with default configuration
    res = admin.create(corename, working_dir)
    res = json.loads(res)

    print_status(res, corename)


if __name__ == "__main__":
    create_core(config.tag_storage)
