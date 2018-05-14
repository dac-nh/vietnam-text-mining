from flask import Flask, request, render_template

app = Flask(__name__)


##
# GET METHOD
##
@app.route('/')
def index():
    return render_template("main.html", title='Vietnamese Text Mining')


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


# 2018-05-10: Dac: Only run your app when this file is main file (code run directly - not an imported file)
if __name__ == "__main__":
    app.run(debug=True)
