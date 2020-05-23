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
