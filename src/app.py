from flask import Flask,request, render_template
import requests
# import arxiv_api as arxiv
from generate_object_tree import ArxivTree, SemSchTree
from primitive_objects import ArxivID

CACHE_ARXIV = "../data/papers_arxiv_v1.json"
CACHE_SEMSCH = "../data/papers_semsch_v1.json"
ARXIVTREE = ArxivTree(CACHE_ARXIV)
SEMSCHTREE = SemSchTree(CACHE_SEMSCH)

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
    paper_results = ARXIVTREE.gather_data(paper_title=paper_title, author=author_name, abstract=keyword)
    return render_template("papers.html", paper_results=paper_results)

@app.route("/papers/paper_explore", methods=['GET','POST'])
def explore_paper():
    for k, v in request.form.items():
        arxiv_id_paper = k
    arxiv_id_paper = arxiv_id_paper.replace("abs/", "").split("v")[0]
    ar_id = ArxivID(arxiv_id_paper)
    title,authors,abstract,ref_cnt,cit_cnt,inf_cit = SEMSCHTREE.fetch_paper_data(ar_id)
    return render_template("paper_explore.html", title=title,authors=authors,
    abstract=abstract,ref_cnt=ref_cnt,cit_cnt=cit_cnt,inf_cit=inf_cit)
    

if __name__ == '__main__':  
    print('starting Flask app', app.name)  
    app.run(debug=True)