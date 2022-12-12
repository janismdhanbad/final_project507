from flask import Flask,request, render_template
import requests
# import arxiv_api as arxiv
from generate_object_tree import ArxivTree, SemSchTree, AuthorTree
from primitive_objects import ArxivID

CACHE_ARXIV = "../data/papers_arxiv_v1.json"
CACHE_SEMSCH = "../data/papers_semsch_v1.json"
CACHE_AUTHORS = "../data/authors_semsch_v1.json"
ARXIVTREE = ArxivTree(CACHE_ARXIV)
SEMSCHTREE = SemSchTree(CACHE_SEMSCH)
AUTHORTREE = AuthorTree(CACHE_AUTHORS)

app = Flask(__name__)
@app.route('/')
def index(): 
    """Main landing page
    """
    
    return render_template("index.html")

@app.route("/papers", methods=['GET','POST'])
def paper_display():
    paper_title = request.form["paper_title"]
    author_name = request.form["author_name"]
    keyword = request.form["keyword"]

    if request.form.get("use_cache"):
        use_cache = True
    else:
        use_cache = False
    paper_results = ARXIVTREE.gather_data(paper_title=paper_title, author=author_name, abstract=keyword, use_cache=use_cache)
    return render_template("papers.html", paper_results=paper_results)

@app.route("/papers/paper_explore", methods=['GET','POST'])
def explore_paper():
    # for k, v in request.form.items():
    if request.form.get("paper_id"):
        arxiv_id_paper = request.form["paper_id"]
        arxiv_id_paper = arxiv_id_paper.replace("abs/", "").split("v")[0]
        ar_id = ArxivID(arxiv_id_paper)
        title, authors, abstract, ref_cnt, cit_cnt, inf_cit, url, reference_list, citation_list = SEMSCHTREE.fetch_paper_data(ar_id)
        return render_template("paper_explore.html", title = title, authors = authors,
        abstract = abstract, ref_cnt = ref_cnt, cit_cnt = cit_cnt, inf_cit = inf_cit, 
        url = url, reference_list = reference_list, citation_list = citation_list)

@app.route("/papers/paper_explore_sch", methods=['GET','POST'])
def explore_paper_sch():
    # for k, v in request.form.items():
    if request.form.get("paper_id"):
        id_paper = request.form["paper_id"]
        title, authors, abstract, ref_cnt, cit_cnt, inf_cit, url, reference_list, citation_list = SEMSCHTREE.fetch_paper_data(id_paper)
        return render_template("paper_explore.html", title = title, authors = authors,
        abstract = abstract, ref_cnt = ref_cnt, cit_cnt = cit_cnt, inf_cit = inf_cit,
        url = url, reference_list = reference_list, citation_list = citation_list)
    
@app.route("/papers/author_explore", methods=['GET','POST'])
def explore_author_sch():
    # for k, v in request.form.items():
    if request.form.get("author_id"):
        author_id = request.form["author_id"]
        name, home, p_cnt, cit_cnt, hindex, worked_with_authors, papers_author = AUTHORTREE.get_author_data(SEMSCHTREE, author_id)
        return render_template("author_explore.html", name = name, home = home,
        p_cnt = p_cnt, cit_cnt = cit_cnt, hindex = hindex,  
        worked_with_authors = worked_with_authors, 
        papers_author = papers_author)

if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(debug=True)