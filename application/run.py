from flask import Flask, request, render_template, jsonify

import application.Repository.GeneralRepository as GeneralRepository

app = Flask(__name__)


##
# GET METHOD
##
@app.route('/')
def index():
    return render_template("main.html", title='Vietnamese Text Mining')


@app.route('/category')
def get_category():
    result = {'result': False, 'data': []}

    # load category_nodes from neo4j
    category_nodes = GeneralRepository.category_nodes
    for category in category_nodes.keys():
        result['data'].append(category)

    # if true
    if len(result['data']) != 0:
        result['result'] = True
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


##
# POST METHOD
##
@app.route('/get-papers-cat-dat', methods=['POST'])
def get_paper_by_category_and_date():
    result = {'result': False, 'data': []}

    category = request.form['category']
    date = request.form['date']

    data = []
    papers = GeneralRepository.get_paper_by_category_and_date(category, date)
    # format: [[title, path],...]
    for paper in papers:
        data.append([paper[0]['title'], paper[0]['path']])

    result['result'] = True
    result['data'] = data
    return jsonify(result)


# 2018-05-10: Dac: Only run your app when this file is main file (code run directly - not an imported file)
if __name__ == "__main__":
    app.run(debug=True)
