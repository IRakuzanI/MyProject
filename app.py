from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from datetime import datetime
#import os


#file_path = os.path.abspath(os.getcwd()) + "\\blog.db"
app = Flask(__name__)
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + file_path
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'any_symbols'
db = SQLAlchemy(app)
admin = Admin(app)


class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False, unique=True)
    articles = db.relationship('Article', backref='category_name')

    def __repr__(self):
        return f'Category: {self.id} - {self.name}'


class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    title = db.Column(db.String(50), nullable=False, unique=True)
    introduction = db.Column(db.String(100), nullable=False)
    text = db.Column(db.Text(), nullable=False)
    pub_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'Article: {self.id} - {self.title}'


class CategoryView(ModelView):
    create_modal = True
    column_list = ['id', 'name', 'articles']


admin.add_view(CategoryView(Category, db.session))
admin.add_view(ModelView(Article, db.session))


@app.route('/test.html')
def test():
    articles = ['First', 'Second', 'Third']
    return render_template('test.html', lst=articles)


@app.route('/')
def index():
    last_articles = Article.query.order_by(Article.pub_date.desc())[:3]

    return render_template('index.html', articles=last_articles)


@app.route('/blog.html')
def blog():
    category = Category.query.filter_by(name='Блог').first()
    # first() - метод, который возвращает первую найденную категорию, на случай, если какой то даун создал 2 одинаковые
    articles = Article.query.filter_by(category_id=category.id)

    return render_template('blog.html', articles=articles)


@app.route('/news.html')
def news():
    category = Category.query.filter_by(name='Новости').first()
    # first() - метод, который возвращает первую найденную категорию, на случай, если какой то даун создал 2 одинаковые
    articles = Article.query.filter_by(category_id=category.id)

    return render_template('news.html', articles=articles)


@app.route('/new_post', methods=['GET', 'POST'])
def new_post():
    if request.method == 'POST':
        category_id = request.form['category_select']
        title = request.form['title']
        introduction = request.form['introduction']
        article_text = request.form['article_text']

        article = Article(
            category_id=category_id,
            title=title,
            introduction=introduction,
            text=article_text
        )
        try:
            db.session.add(article)
            db.session.commit()
        except Exception as err:
            return f'Возникла ошибка! -> {err}'

        return redirect(url_for('index'))

    else:
        categories = Category.query.all()
        return render_template('new_post.html', categories=categories)


@app.route('/edit/<int:article_id>', methods=['GET', 'POST'])
def edit_post(article_id):
    article = Article.query.get_or_404(article_id)
    if request.method == 'POST':
        article.category_id = request.form['category_select']
        article.title = request.form['title']
        article.introduction = request.form['introduction']
        article.text = request.form['article_text']

        try:
            db.session.commit()

            return redirect(url_for('index'))
        except Exception as err:
            print(f'Возникла ошибка -> {err}')
    else:
        categories = Category.query.all()

        return render_template('edit_post.html', article=article, categories=categories)


@app.route('/detailed_post/<int:article_id>')
def detailed_post(article_id):
    article = Article.query.get_or_404(article_id)

    return render_template('detailed.html', article=article)


@app.route('/delete/<int:article_id>')
def delete_post(article_id):
    article = Article.query.get_or_404(article_id)

    try:
        db.session.delete(article)
        db.session.commit()

        return redirect(url_for('index'))
    except Exception as err:
        print(f'Возникла ошибка -> {err}')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
