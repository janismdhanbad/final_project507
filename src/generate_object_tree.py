import sys

sys.path.append("../")
import json
import time
import urllib.parse
import xml.etree.ElementTree as ET
from typing import Dict

import numpy as np
import pandas as pd
import requests
from data.twitter_key import SemanticScholarCreds

import utils
from primitive_objects import ArxivID, ArxivPaper, Authors, SemSchPaper

SEMSCH_PAPER_KEYS = [
    "id",
    "paper_arxiv_id",
    "title",
    "authors",
    "abstract",
    "category",
    "year",
    "reference_count",
    "citation_count",
    "influential_paper_citations",
    "is_open_access",
]
SEMSCH_LINK = "https://api.semanticscholar.org/graph/v1"
ARXIV_KEYS = ["arxiv_id", "title", "authors", "abstract"]
ARXIV_LINK = "http://export.arxiv.org/api/query?search_query="
NAMESPACE = {"n": "http://www.w3.org/2005/Atom"}


class SemSchTree:
    def __init__(self, cache_pth: str):
        self.cache_pth = cache_pth
        self.papers_dict = {}
        self.read_cache()

    def read_cache(self):
        try:
            with open(self.cache_pth, "r") as f:
                data = json.load(f)
            if bool(data):
                for k, v in data.items():
                    self.papers_dict[k] = SemSchPaper(**v)
        except:
            pass

    def write_cache(self):
        data_save = {}
        for paper_id, val in self.papers_dict.items():
            temp_dict = vars(val)
            data_save[paper_id] = temp_dict

        with open(self.cache_pth, "w") as f:
            json.dump(data_save, f)
        return True

    def get_paper_list(self):
        return list(self.papers_dict.keys())

    def get_semschID_for_arxivID(self, arxiv_id):
        url = f"{SEMSCH_LINK}/paper/arXiv:{arxiv_id}"
        res = requests.get(url, headers={"x-api-key": SemanticScholarCreds.API_KEY})
        semsch_paperid = res.json()["paperId"]
        return semsch_paperid

    def update_paper_data(self, input_id):
        if isinstance(input_id, ArxivID):
            semsch_paperid = self.get_semschID_for_arxivID(input_id.id)
        else:
            semsch_paperid = input_id
        paper_list = self.get_paper_list()

        if semsch_paperid in paper_list:
            pass
        else:
            author_fields = (
                "authors.name,authors.hIndex,authors.paperCount,authors.citationCount"
            )
            citations_fields = "citations.title,citations.influentialCitationCount"
            req_fields = f"url,title,{author_fields},abstract,year,referenceCount,citationCount,influentialCitationCount,isOpenAccess,fieldsOfStudy,{citations_fields},references&limit=50"
            url_paper = f"{SEMSCH_LINK}/paper/{semsch_paperid}?fields={req_fields}"
            _results = requests.get(
                url_paper, headers={"x-api-key": SemanticScholarCreds.API_KEY}
            )
            results = _results.json()
            self.update_paper_info(results, input_id, semsch_paperid)
        return semsch_paperid

    def update_paper_info(self, results, arxiv_id, semsch_paperid):
        _initialize_dict = {}
        _initialize_dict["id"] = results["paperId"]
        if isinstance(arxiv_id, ArxivID):
            _initialize_dict["arxiv_id"] = arxiv_id.id
        else:
            _initialize_dict["arxiv_id"] = None
        _initialize_dict["title"] = results["title"]
        _initialize_dict["authors"] = results["authors"]
        _initialize_dict["abstract"] = results["abstract"]
        _initialize_dict["category"] = None
        _initialize_dict["year"] = results["year"]
        _initialize_dict["reference_count"] = results["referenceCount"]
        _initialize_dict["citation_count"] = results["citationCount"]
        _initialize_dict["influential_paper_citations"] = results[
            "influentialCitationCount"
        ]
        _initialize_dict["is_open_access"] = results["isOpenAccess"]
        _initialize_dict["url"] = results["url"]

        citations = [f for f in results["citations"] if f["paperId"] is not None]
        citations = [f for f in citations if f["influentialCitationCount"] is not None]
        citations = sorted(
            [f for f in citations],
            key=lambda x: x["influentialCitationCount"],
            reverse=True,
        )
        citations = [f["paperId"] for f in citations][:10]
        references = [f["paperId"] for f in results["references"]]
        citations = [f for f in citations if f is not None]
        references = [f for f in references if f is not None]

        _initialize_dict["citations"] = citations
        _initialize_dict["references"] = references
        paper = SemSchPaper(**_initialize_dict)
        self.papers_dict[results["paperId"]] = paper
        if semsch_paperid != results["paperId"]:
            self.papers_dict[semsch_paperid] = paper

    def update_papers(self, paper_ids):
        i = 1
        for ref_id in paper_ids:
            if self.papers_dict.get(ref_id):
                pass
            else:
                self.update_paper_data(ref_id)
                i = i + 1
                if i % 98 == 0:
                    time.sleep(1.0)

    def fetch_paper_data(self, input_id):
        semsch_paperid = self.update_paper_data(input_id)
        paper = self.papers_dict[semsch_paperid]
        references = paper.references
        citations = paper.citations
        references = [f for f in references if f is not None]
        citations = [f for f in citations if f is not None]
        self.update_papers(references)
        self.update_papers(citations)
        reference_list = []
        citation_list = []
        self.write_cache()

        for ref in references:
            reference_list.append(vars(self.papers_dict[ref]))

        for cit in citations:
            citation_list.append(vars(self.papers_dict[cit]))

        df = pd.read_csv("../data/prev_searches.csv")
        columns_csv = [
            "paper_id",
            "Title",
            "citation_count",
            "reference_count",
            "influencial_citations_count",
        ]
        temp_df = pd.DataFrame(index=range(1), columns=columns_csv)
        temp_df["paper_id"] = paper.id
        temp_df["Title"] = paper.title
        temp_df["citation_count"] = paper.citation_count
        temp_df["reference_count"] = paper.reference_count
        temp_df["influencial_citations_count"] = paper.influential_paper_citations
        df = pd.concat([df, temp_df])
        df.to_csv("../data/prev_searches.csv", index=False)

        return (
            paper.title,
            paper.authors,
            paper.abstract,
            paper.reference_count,
            paper.citation_count,
            paper.influential_paper_citations,
            paper.url,
            reference_list,
            citation_list,
        )


class ArxivTree:
    def __init__(self, cache_pth: str):
        self.cache_pth = cache_pth
        self.papers = []
        self.read_cache()

    def read_cache(self):
        try:
            with open(self.cache_pth, "r") as f:
                data = json.load(f)
            if bool(data):
                for v in data.values():
                    self.papers.append(ArxivPaper(**v))
        except:
            pass

    def write_cache(self):
        data_save = {}
        for paper in self.papers:
            temp_dict = vars(paper)
            data_save[temp_dict["arxiv_id"]] = temp_dict

        with open(self.cache_pth, "w") as f:
            json.dump(data_save, f)
        return True

    def get_paper_titles(self):
        return [[i, f.title] for i, f in enumerate(self.papers)]

    def get_paper_authors(self):
        authors_all = [[i, f.authors] for i, f in enumerate(self.papers)]
        return authors_all

    def get_paper_abstracts(self):
        abstract_all = [[i, f.abstract] for i, f in enumerate(self.papers)]
        return abstract_all

    def update_paper_list(self, paper_dict):
        self.papers.append(ArxivPaper(**paper_dict))

    def construct_arxiv_link(
        self, paper_title=None, author=None, abstract=None, start_idx=0, max_results=100
    ):
        param_dict = {
            "ti": paper_title,
            "au": author,
            "abs": abstract,
        }
        str_query = ""
        query_list = []
        for k, v in param_dict.items():
            if v is not None:
                value_str = " ".join(v.split(" "))
                value_str = f"%22{value_str}%22"
                query_list.append(f"{k}:{value_str}")
        str_query = "+AND+".join(query_list)
        str_query = urllib.parse.quote_plus(str_query)

        str_query += f"&sortBy=relevance&sortOrder=descending&start={start_idx}&max_results={max_results}"
        return ARXIV_LINK + str_query

    def request_arxiv_api_and_update(self, paper_title, author, abstract):
        self.local_paper_list = []
        link_arxiv = self.construct_arxiv_link(
            paper_title=paper_title, author=author, abstract=abstract, max_results=100
        )
        response = requests.get(link_arxiv)
        xmlstring = response.text
        tree = ET.ElementTree(ET.fromstring(xmlstring))
        tree_root = tree.getroot()
        all_papers = tree_root.findall("n:entry", namespaces=NAMESPACE)

        for paper in all_papers:
            temp_tile = paper.find("n:title", namespaces=NAMESPACE).text

            all_authors = list(paper.findall("n:author", namespaces=NAMESPACE))

            paper_id = paper.find("n:id", namespaces=NAMESPACE).text.replace(
                "http://arxiv.org/", ""
            )
            paper_abstract = paper.find("n:summary", namespaces=NAMESPACE).text.replace(
                "http://arxiv.org/", ""
            )
            paper_abstract = paper_abstract.replace("\n", " ").lstrip().rstrip()
            paper_author_list = []
            for au in all_authors:
                paper_author_list.append(list(au)[0].text)
            paper_details = {
                "arxiv_id": paper_id,
                "authors": paper_author_list,
                "title": temp_tile,
                "abstract": paper_abstract,
            }

            self.local_paper_list.append(ArxivPaper(**paper_details))
            self.update_paper_list(paper_details)

    def gather_data(
        self, paper_title=None, author=None, abstract=None, use_cache=False
    ):
        if paper_title == "":
            paper_title = None
        if author == "":
            author = None
        if abstract == "":
            abstract = None

        paper_list = self.get_paper_titles()
        author_list = self.get_paper_authors()
        abstract_list = self.get_paper_abstracts()

        if paper_title is not None:
            paper_ids_title = [
                f[0] for f in paper_list if utils.lev_dist(f[1], paper_title) < 30
            ]
        else:
            paper_ids_title = []
        if author is not None:
            paper_ids_author = [
                f[0] for f in author_list if utils.arxiv_author_match(author, f[1])
            ]
        else:
            paper_ids_author = []
        if abstract is not None:
            paper_ids_abstract = [
                f[0]
                for f in abstract_list
                if utils.arxiv_abstract_match(f[1], abstract)
            ]
        else:
            paper_ids_abstract = []
        paper_ids = paper_ids_title + paper_ids_author + paper_ids_abstract

        if bool(paper_ids) and use_cache == True:
            candidate_papers = [vars(f) for f in self.papers]
            papers_data = np.array(candidate_papers)[paper_ids].tolist()
        else:
            self.request_arxiv_api_and_update(paper_title, author, abstract)
            self.write_cache()
            papers_data = [vars(f) for f in self.local_paper_list]

        return papers_data


class AuthorTree:
    def __init__(self, cache_pth: str):
        self.cache_pth = cache_pth
        self.author_dict = {}
        self.read_cache()

    def read_cache(self):
        try:
            with open(self.cache_pth, "r") as f:
                data = json.load(f)
            if bool(data):
                for k, v in data.items():
                    self.author_dict[k] = Authors(**v)
        except:
            pass

    def write_cache(self):
        data_save = {}
        for author_id, val in self.author_dict.items():
            temp_dict = vars(val)
            data_save[author_id] = temp_dict

        with open(self.cache_pth, "w") as f:
            json.dump(data_save, f)
        return True

    def get_author_list(self):
        return list(self.author_dict.keys())

    def request_and_update(self, author_id: str):

        author_list = self.get_author_list()
        if author_id in author_list:

            pass
        else:
            papers_req = "papers.title,papers.authors"
            req_fields = f"name,affiliations,homepage,paperCount,citationCount,hIndex,{papers_req}"
            author_url = f"{SEMSCH_LINK}/author/{author_id}?fields={req_fields}"
            _results = requests.get(
                author_url, headers={"x-api-key": SemanticScholarCreds.API_KEY}
            )
            results = _results.json()
            try:
                self.update_author_info(results)
            except:
                import pdb

                pdb.set_trace()

        return author_id

    def update_author_info(self, results: Dict):
        _author_dict = {}

        author_id = results["authorId"]

        _author_dict["id"] = author_id
        _author_dict["name"] = results["name"]
        _author_dict["homepage"] = results["homepage"]
        _author_dict["paper_count"] = results["paperCount"]
        _author_dict["citations"] = results["citationCount"]
        _author_dict["hindex"] = results["hIndex"]

        author_papers = results["papers"]
        author_papers_id = [f["paperId"] for f in author_papers]
        _author_dict["papers"] = author_papers_id

        id_worked_with = [[f["authorId"] for f in f["authors"]] for f in author_papers]
        id_worked_with = [f for ff in id_worked_with for f in ff]

        id_worked_with = list(set(id_worked_with))
        id_worked_with = [f for f in id_worked_with if f != author_id]
        _author_dict["worked_with"] = id_worked_with
        author = Authors(**_author_dict)
        self.author_dict[author_id] = author

    def get_author_data(self, SEMSCHTREE, author_id: str):
        sem_sch_id = self.request_and_update(author_id)
        author = self.author_dict[sem_sch_id]

        author_papers_id = author.papers
        author_papers_id = [f for f in author_papers_id if f is not None]

        id_worked = author.worked_with
        id_worked = [f for f in id_worked if f is not None]

        i = 1
        for a_id in id_worked:
            if self.author_dict.get(a_id):
                pass
            else:
                self.request_and_update(a_id)
                i = i + 1
                if i % 98 == 0:
                    time.sleep(1)
        i = 1
        for p_id in author_papers_id:
            if SEMSCHTREE.papers_dict.get(p_id):
                pass
            else:
                SEMSCHTREE.update_paper_data(p_id)
                i = i + 1
                if i % 98 == 0:
                    time.sleep(1)

        worked_with_id = [f for f in author.worked_with]
        worked_with_authors = [self.author_dict.get(f) for f in worked_with_id]
        worked_with_authors = [f for f in worked_with_authors if f is not None]
        worked_with_authors = [
            f for f in worked_with_authors if f.citations is not None
        ]
        worked_with_authors = sorted(
            worked_with_authors, key=lambda x: x.citations, reverse=True
        )
        worked_with_authors = worked_with_authors[:50]
        worked_with_authors = [vars(f) for f in worked_with_authors]

        papers_author = [SEMSCHTREE.papers_dict.get(f) for f in author_papers_id]
        papers_author = [f for f in papers_author if f is not None]
        papers_author = [f for f in papers_author if f.citation_count is not None]
        papers_author = sorted(
            papers_author, key=lambda x: x.citation_count, reverse=True
        )
        papers_author = [vars(f) for f in papers_author]

        hindex = author.hindex
        cit_cnt = author.citations
        p_cnt = author.paper_count
        home = author.homepage
        name = author.name

        SEMSCHTREE.write_cache()
        self.write_cache()

        return (name, home, p_cnt, cit_cnt, hindex, worked_with_authors, papers_author)
