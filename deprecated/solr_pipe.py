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

class SolrPipe:
    """
    SolrPipe to use solr binaries
    Only works if you have set the SOLR_ROOT env variable pointing to your Solr
    installation path
    """

    def __init__(self, debug=False):
        self.debug = debug

        try:
            self._solr_root = Path(os.environ["SOLR_ROOT"])
        except:
            raise ValueError(
                "You have not set the SOLR_ROOT environment variable!\n"
                "export SOLR_ROOT='<PATH_TO_SOLR_INSTALLATION>'"
            )

    def post(self, url: URL, corename: str, *docs: str):
        docs = " ".join(docs)

        # prepare url for update
        url = url / "update"

        p = self._popen(f"{self._post_bin} -url {url} -c {corename} {docs}")

        if self.debug:
            print("STDOUT:", p.stdout.decode("utf-8"))
            if p.stderr:
                print("STDERR:", p.stderr.decode("utf-8"))

    def start(self):
        p = self._popen(f"{self._solr_bin} start")

    @property
    def _solr_bin(self) -> Path:
        return self._bin_dir / "solr"

    @property
    def _post_bin(self) -> Path:
        return self._bin_dir / "post"

    @property
    def _bin_dir(self) -> Path:
        return self._solr_root / "bin"

    def _popen(
        self, command: str, stdout: int = sp.PIPE, stderr: int = sp.PIPE
    ) -> sp.CompletedProcess:
        return sp.run(command, stdout=stdout, stderr=stderr, shell=True)
