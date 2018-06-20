from flask import Flask, request, render_template, jsonify

import application.Library.Constant.GeneralConstant as GeneralConstant
import application.Repository.GeneralRepository as GeneralRepository

app = Flask(__name__)

""" GET """


@app.route('/')
def index():
    return render_template("main.html", title='Vietnamese Text Mining')


@app.route('/category')
def get_category():
    result = {'code': False, 'data': []}
    # load category_nodes from neo4j
    category_nodes = GeneralRepository.category_nodes
    for category in category_nodes.keys():
        result['data'].append(category)
    # if true
    if len(result['data']) != 0:
        result['code'] = True
    return jsonify(result)


# Todo: change to method GET later
@app.route('/load-paper', methods=['POST'])
def get_paper():
    result = {'code': False, 'data': []}
    paper_path = request.form['path']
    try:
        # read file
        content = ''
        paper_file = open(paper_path.replace('..\\', ''), "r", encoding='UTF-8')
        if paper_file.mode == 'r':
            lines = paper_file.readlines()
            for line in lines:
                content += line
            result['data'] = content
        # if true
        if len(result['data']) != 0:
            result['code'] = True
    except Exception as e:
        print('[get_paper] Failed in getting content of paper: '.format(e.args[0]))
    return jsonify(result)


@app.route('/tuna', methods=['GET', 'POST'])
def tuna():
    if request.method == 'GET':
        return 'You are using GET method'
    else:
        return 'You are using POST method'


@app.route('/profile/<username>')
def profile(username):
    return '<h2>Hello {0}</h2>'.format(username)


@app.route('/post/<int:post_id>')
def show_post(post_id):
    return '<h2>Post Id: {0}</h2>'.format(post_id)


""" POST """


@app.route('/get-papers-cat-dat', methods=['POST'])
def get_papers_by_category_and_date():
    result = {'code': False, 'data': []}
    category = request.form['category']
    date = request.form['date']
    data = []
    papers = GeneralRepository.get_papers_by_category_and_date(category, to_date=date)
    # Todo: change path to id
    # format: [[name, path],...]
    for paper in papers:
        data.append([paper[0].id, paper[0]['name'], paper[0]['path']])
    result['code'] = True
    result['data'] = data
    return jsonify(result)


@app.route('/post-keywords-paper', methods=['POST'])
def post_keywords_by_paper():
    paper_id = request.form['paperId']
    keyword_result = GeneralRepository.get_keyword_by_paper_id(paper_id)
    return jsonify(keyword_result)


# 2018-05-10: Dac: Only run your app when this file is main file (code run directly - not an imported file)
if __name__ == "__main__":
    app.run(debug=True)
