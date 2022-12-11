import sys
sys.path.append("../")
import json
import pandas as pd
from primitive_objects import Authors, SemSchPaper, ArxivPaper, ArxivID
import numpy as np
from tqdm import tqdm
from typing import List, Dict, Tuple
import requests
import xml.etree.ElementTree as ET
import utils
import json
import re
from data.twitter_key import SemanticScholarCreds
import time
import langid

SEMSCH_PAPER_KEYS = [
    'id','paper_arxiv_id', 'title', 'authors', 'abstract', 'category', 'year', 
    'reference_count', 'citation_count', 'influential_paper_citations', 
    'is_open_access'
    ]
SEMSCH_LINK = "https://api.semanticscholar.org/graph/v1"
ARXIV_KEYS = ["arxiv_id", "title", "authors", "abstract"]
ARXIV_LINK= "http://export.arxiv.org/api/query?search_query="
NAMESPACE={'n':'http://www.w3.org/2005/Atom'}

class SemSchTree:

    def __init__(self, cache_pth: str):
        self.cache_pth = cache_pth
        self.papers_dict = {}
        self.read_cache()
        
    
    def read_cache(self):
        try:
            with open(self.cache_pth, 'r') as f: data = json.load(f)
            if bool(data):
                for k,v in data.items():
                    self.papers_dict[k] = SemSchPaper(**v)
        except:
            pass

    def write_cache(self):
        data_save = {}
        for paper_id, val in self.papers_dict.items():
            temp_dict = vars(val)
            data_save[paper_id] = temp_dict

        with open(self.cache_pth, 'w') as f:
            json.dump(data_save, f)
        return True
    
    def get_paper_list(self):
        return list(self.papers_dict.keys())
    
    def get_semschID_for_arxivID(self, arxiv_id):
        url = f"{SEMSCH_LINK}/paper/arXiv:{arxiv_id}"
        res = requests.get(url, headers={"x-api-key":SemanticScholarCreds.API_KEY })
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
            author_fields = "authors.name,authors.hIndex,authors.paperCount,authors.citationCount"
            citations_fields = "citations.title,citations.influentialCitationCount"
            req_fields = f"url,title,{author_fields},abstract,year,referenceCount,citationCount,influentialCitationCount,isOpenAccess,fieldsOfStudy,{citations_fields},references&limit=50"
            url_paper = f"{SEMSCH_LINK}/paper/{semsch_paperid}?fields={req_fields}"
            _results = requests.get(url_paper, headers={"x-api-key":SemanticScholarCreds.API_KEY })
            results = _results.json()
            self.update_paper_info(results, input_id)
        return semsch_paperid


    def update_paper_info(self, results, arxiv_id):
        _initialize_dict = {}
        _initialize_dict["id"] =  results["paperId"]
        if isinstance(arxiv_id, ArxivID):
            _initialize_dict["arxiv_id"] = arxiv_id.id
        else:
            _initialize_dict["arxiv_id"] = None
        # _initialize_dict["url"] = results['url']
        _initialize_dict["title"] = results['title']
        _initialize_dict["authors"] = results['authors']
        _initialize_dict["abstract"] = results['abstract']
        _initialize_dict["category"] = None
        _initialize_dict["year"] = results['year']
        _initialize_dict["reference_count"] = results['referenceCount']
        _initialize_dict["citation_count"] = results['citationCount']
        _initialize_dict["influential_paper_citations"] = results['influentialCitationCount']
        _initialize_dict["is_open_access"] = results['isOpenAccess']
        
        citations = [f for f in results["citations"] if f["paperId"] is not None]
        citations = [f for f in citations if f["influentialCitationCount"] is not None]
        citations = sorted([f for f in citations], key = lambda x: x["influentialCitationCount"], reverse=True)
        citations = [f["paperId"] for f in citations][:10]
        references = [f["paperId"] for f in results["references"]]
        citations = [f for f in citations if f is not None]
        references = [f for f in references if f is not None]

        _initialize_dict["citations"] = citations
        _initialize_dict["references"] = references
        paper = SemSchPaper(**_initialize_dict)
        self.papers_dict[results["paperId"]] = paper



    def update_papers(self, paper_ids):
        for i, ref_id in enumerate(paper_ids):
            self.update_paper_data(ref_id)
            if ((i%98 == 0) and (i != 0)) :
                time.sleep(1.)
    
    def fetch_paper_data(self, input_id):
        semsch_paperid = self.update_paper_data(input_id)
        paper = self.papers_dict[semsch_paperid]
        references = paper.references
        citations = paper.citations
        self.update_papers(references)
        self.update_papers(citations)
        
        self.write_cache()
        return (paper.title, paper.authors, paper.abstract, 
        paper.reference_count,paper.citation_count, paper.influential_paper_citations)
        
        





        
        



    


    def _initialize_paper(self, paper_dict:Dict):

        def __init__(self):
            self.lst = []
        _paper_dict = {}
        for k in SEMSCH_PAPER_KEYS:
            _paper_dict[k] = paper_dict.get(k)
        paper = SemSchPaper(**_paper_dict)
        return paper

    def initialize_papers(self, paper_list:List[Dict]):
        for paper_dict in paper_list:
            paper = self._initialize_paper(paper_dict=paper_dict)
            self.lst.append(paper)




class ArxivTree:

    def __init__(self, cache_pth: str):
        self.cache_pth = cache_pth
        self.papers = []
        self.read_cache()

    def read_cache(self):
        try:
            with open(self.cache_pth, 'r') as f: data = json.load(f)
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

        with open(self.cache_pth, 'w') as f:
            json.dump(data_save, f)
        return True

    def get_paper_titles(self):
        return [[i, f.title] for i, f in enumerate(self.papers)]

    def update_paper_list(self, paper_dict):
        self.papers.append(ArxivPaper(**paper_dict))

    def construct_arxiv_link(self, paper_title=None, author=None, abstract=None, start_idx = 0, max_results= 100):
        param_dict= {
            "ti": paper_title,
            "au":author,
            "abs": abstract,
            }
        str_query = ""
        query_list = []
        for k, v in param_dict.items():
            if v is not None:
                value_str = "\ ".join(v.split(" "))
                query_list.append(f"{k}:{value_str}")
        str_query = "+AND+".join(query_list)
        str_query += f"&sortBy=relevance&sortOrder=descending&start={start_idx}&max_results={max_results}"
        return ARXIV_LINK + str_query

    def request_arxiv_api_and_update(self, paper_title, author, abstract):
        self.local_paper_list = []
        link_arxiv = self.construct_arxiv_link(paper_title=paper_title, author=author,abstract=abstract, max_results=100)
        response = requests.get(link_arxiv)
        xmlstring = response.text
        tree = ET.ElementTree(ET.fromstring(xmlstring))
        tree_root = tree.getroot()
        all_papers = tree_root.findall('n:entry',namespaces=NAMESPACE)
        for paper in all_papers:
            temp_tile = paper.find('n:title',namespaces=NAMESPACE).text
            all_authors = list(paper.findall('n:author',namespaces=NAMESPACE))
            paper_id = paper.find('n:id',namespaces=NAMESPACE).text.replace("http://arxiv.org/","")
            paper_author_list = []
            for au in all_authors:
                paper_author_list.append(list(au)[0].text)
            paper_details = {"arxiv_id":paper_id, "authors": paper_author_list, "title": temp_tile}
            self.local_paper_list.append(paper_id)
            self.update_paper_list(paper_details)
        

    def gather_data(self, paper_title=None, author=None, abstract=None):
        if paper_title == "":
            paper_title = None
        if author == "":
            author = None
        if abstract == "":
            abstract = None
        
        paper_list = self.get_paper_titles()
        paper_ids = [f[0] for f in paper_list if utils.lev_dist(f[1], paper_title)< 30]
        if bool(paper_ids):
            candidate_papers = [vars(f) for f in self.papers]
            
            papers_data = np.array(candidate_papers)[paper_ids].tolist()
        else:
            self.request_arxiv_api_and_update(paper_title, author, abstract)
            self.write_cache()
            papers_data = [vars(f) for f in self.papers]

        return papers_data

        

