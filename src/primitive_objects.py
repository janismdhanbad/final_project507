class Authors:
    def __init__(self, author_id=None, author_name=None, author_aliases=None, 
    homepage=None, 
    paper_count=None, citations=None, hindex=None, author_name_query=None, 
    cache_file=None):


        if cache_file is None:
            if author_id is not None:
                self.id = author_id
            else:
                RuntimeError("Please pass a valid author ID")
            if author_name is not None:
                self.name = author_name
            else:
                self.name = None
            if author_aliases is not None:
                self.aliases = author_aliases
            else:
                self.aliases = None
            if homepage is not None:
                self.homepage = homepage
            else:
                self.homepage = None
            if paper_count is not None:
                self.paper_count = paper_count
            else:
                self.paper_count = None
            if citations is not None:
                self.citations =citations
            else:
                self.citations = None
            if hindex is not None:
                self.hindex =hindex
            else:
                self.hindex = None
            if author_name_query is not None:
                self.name_query=author_name_query
            else:
                self.name_query = None
            self.papers = None
        else:
            self.id = cache_file["id"]
            self.name = cache_file["name"]
            self.aliases = cache_file["aliases"]
            self.homepage = cache_file["homepage"]
            self.paper_count = cache_file["paper_count"]
            self.citations = cache_file["citations"]
            self.hindex = cache_file["hindex"]
            self.name_query = cache_file["name_query"]

class Paper:
    def __init__(self, id=None,arxiv_id= None, title=None, authors=None, 
    abstract=None, category = None, cache_file=None):
        if cache_file is None:
           
            self.id = id
            self.title = title
            self.authors = authors        
            self.abstract = abstract       
            self.arxiv_id = arxiv_id      
            self.category = category
        else:
            self.id = cache_file["id"]
            self.title = cache_file["title"]
            self.authors = cache_file["authors"]
            self.abstract = cache_file["abstract"]
            self.category = cache_file["category"]
            self.arxiv_id = cache_file["arxiv_id"]
    
class ArxivID:
    def __init__(self, ar_id:str):
        self.id = ar_id
class SemSchPaper(Paper):
    def __init__(self, id=None,arxiv_id=None, title=None, authors=None, 
    abstract=None, category = None,  year=None, reference_count=None, citation_count=None, 
    influential_paper_citations=None, is_open_access=None, citations=None, references=None, 
    cache_file=None):
        super().__init__(id, arxiv_id, title, authors, abstract, category, cache_file)
        
        if cache_file is None:

                self.year = year
                self.reference_count = reference_count
                self.citation_count = citation_count
                self.influential_paper_citations = influential_paper_citations
                self.is_open_access = is_open_access
                self.citations = citations
                self.references = references


        else:
            self.year = cache_file["year"]
            self.reference_count = cache_file["reference_count"]
            self.citation_count = cache_file["citation_count"]
            self.influential_paper_citations = cache_file["influential_paper_citations"]
            self.is_open_access = cache_file["is_open_access"]
            self.citations= cache_file["citations"]
            self.references = cache_file["references"]

class Categories:
    def __init__(self, category_name=None, paper_ids=None, cache_file=None):
        if cache_file is None:
            self.category_name = category_name
            self.paper_ids = paper_ids
        else:
            self.category_name = cache_file["category"]
            self.paper_ids = paper_ids


class TwitterData:
    def __init__(self,paper_id, text, retweet_count,reply_count ,like_count,quote_count):
        self.paper_id = paper_id
        self.text = text
        self.like_count = like_count
        self.retweet_count = retweet_count
        self.reply_count = reply_count
        self.quote_count = quote_count


class ArxivPaper(Paper):
    def __init__(self,id=None, arxiv_id=None, title=None, authors=None, 
    abstract=None, category=None, cache_file=None):
        super().__init__(id, arxiv_id, title, authors, abstract, category,cache_file)