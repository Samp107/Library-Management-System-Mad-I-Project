from flask import redirect, render_template, request, flash, session, url_for
from flask import current_app as app
from datetime import datetime, timedelta
from flask_login import login_user, LoginManager, login_required, logout_user, current_user
from flask_bcrypt import Bcrypt
import os



from .model import db, User, Section, Book, Cart

#-------initiallize login manager--------------
bcrypt = Bcrypt(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(id):
    return User.query.get(id)


def addadmin():
    if User.query.filter_by(role='admin').first() is None:

        user = User(email = 'admin@gmail.com', password = bcrypt.generate_password_hash('12345',10), role ='admin')
        db.session.add(user)
        db.session.commit()


@app.route("/register", methods = ["GET","POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    if request.method == "POST":
        email = request.form["email"]
        existing_email =  User.query.filter_by(user_mail = email).first()
        if existing_email:
            flash("email already registered")
            return redirect("/login")
        else:
            password = request.form["password"]
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = User(email = email, password= hashed_password, role = "user")
            db.session.add(new_user)
            db.session.commit()
            flash("You are now registered, Please Login")
            return redirect('/login')


@app.route("/login", methods =["GET","POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    if request.method == "POST":
        email = request.form["email"]
        password =  request.form["password"]
        user =  User.query.filter_by(user_mail = email).first()
        if user is not None and user.role == 'user':
            if bcrypt.check_password_hash(user.password, password):
                login_user(user)
                return redirect('/')
            else:
                flash("Wrong Password, Please Login")
                return redirect("/login")
        else:
            flash("You are not registered, Please register")
            return redirect("/register")

@app.route("/delete_user/<int:user_id>")
@login_required
def delete_user(user_id):
    if current_user.role == 'admin':
        user = User.query.filter_by(user_id = user_id).first()
        db.session.delete(user)
        db.session.commit()
        return redirect("/all_users")
    else:
        return "Please login as Admin to access this page"


@app.route("/admin_login", methods =["GET","POST"])
def admin_login():
    if request.method == "GET":
        return render_template("adminlogin.html")
    if request.method == "POST":
        email = request.form["email"]
        password =  request.form["password"]  
        """ if (email == "admin@gmail.com" and password == "12345"):
            session['email'] = email
            return redirect('/admin_dashboard')
        else:
            flash("You are not Admin, Please Register/Login as User")
            return redirect("/register") """
        admin =  User.query.filter_by(user_mail = email, role='admin').first()        
        if admin:
            if bcrypt.check_password_hash(admin.password, password):
                login_user(admin)
                return redirect('/admin_dashboard')
            else:
                flash("Wrong Password, Please Login")
                return redirect("/login")
        else:
            flash("You are not Admin, Please Register/Login as User")
            return redirect("/register")
        

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/login")



@app.route('/',methods = ["GET", "POST"])
@login_required
def home():
    if request.method == "GET":
        sections = Section.query.all()
        books = Book.query.all()
        user_id = current_user.user_id
        user = User.query.filter_by(user_id = user_id).first()
        if user.role == 'user':
            return render_template("user/home.html", sections = sections, books = books)
        
    
    
@app.route("/admin_dashboard", methods= ["GET"])
@login_required
def admin_dashboard():
    if request.method == "GET":
        users = User.query.all()
        user_count = len(users)
        orders = Cart.query.all()
        sections = Section.query.all()
        section_count = len(sections)
        books = Book.query.all()
        book_count = len(books)
        order_count = len(orders)
        user_id = current_user.user_id
        user = User.query.filter_by(user_id = user_id).first()
        if user.role == 'admin':
            return render_template('admin/admindashboard.html/', users = users, sections = sections, orders = orders,
                                    books = books, user_count = user_count, section_count = section_count, book_count = book_count, order_count = order_count)
        else:
            return "Please login as Admin to access this page"

@app.route("/user_list", methods= ["GET"])
@login_required
def user_list():
    if request.method == "GET":
        users = User.query.all()
        return  render_template('admin/userlist.html/', users = users)


@app.route("/profile", methods= ["GET"])
@login_required
def profile():
    if request.method == "GET":
        user_logined_id = current_user.user_id
        sections = Section.query.all()
        user = User.query.filter_by(user_id = user_logined_id).first()
        return render_template("user/profile.html", user = user, sections = sections)
    
    
@app.route("/edit_profle", methods = ["GET","POST"])
@login_required
def edit_profile():
    if request.method == "GET":
        user_logined_id = current_user.user_id
        sections = Section.query.all()
        user = User.query.filter_by(user_id = user_logined_id).first()
        return render_template("user/edit_profile.html", user=user, sections = sections)
    if request.method == "POST":
        user_name = request.form["user_name"]
        user_mail= request.form["user_mail"]
        profile_pic = request.files["profile_pic"]
        profile_pic.save("static/user/" + profile_pic.filename)

        user_logined_id = current_user.user_id
        user = User.query.filter_by(user_id = user_logined_id).first()
        user.user_name = user_name
        user.user_mail = user_mail
        user.profile_img_path = "static/user/" + profile_pic.filename
        db.session.commit()
        return redirect('/profile')
    
@app.route("/add_section", methods= ["GET", 'POST'])
@login_required
def add_section():
    if current_user.role == 'admin':
        if request.method == "GET":
            return render_template("admin/add_section.html")
        if request.method == "POST":
            name = request.form["section_name"]
            existing_section =  Section.query.filter_by(section_name = name).first()
            if existing_section:
                flash("Section already registered")
                return redirect("/admin_dashboard")
            else:
                new_section = Section(name = name)
                db.session.add(new_section)
                db.session.commit()
                flash("New section added successfully")
                return redirect('/admin_dashboard')
    else:
        return "Please login as Admin to access this page"

@app.route("/edit_section/<int:section_id>", methods = ["GET","POST"])
@login_required
def edit_section(section_id):
    if current_user.role == 'admin':
        if request.method == "GET":
            section = Section.query.filter_by(section_id = section_id).first()
            return render_template("admin/edit_section.html", section = section)
        if request.method == "POST":
            section_name = request.form.get("section_name")

            section = Section.query.filter_by(section_id = section_id).first()
            section.section_name = section_name
            db.session.commit()
            flash('section is Edited successfully','success')
            return redirect('/all_sections')
    else:
        return "Please login as Admin to access this page"

@app.route("/delete_section/<int:section_id>")
@login_required
def delete_section(section_id):
    if current_user.role == 'admin':
        section = Section.query.filter_by(section_id = section_id).first()
        section_name = section.section_name
        cart = Cart.query.filter_by(section_name = section_name).all()
        db.session.delete(section)
        db.session.commit()
        return redirect("/all_sections")
    else:
        return "Please login as Admin to access this page"


@app.route("/add_book", methods=["GET","POST"])
@login_required
def add_book():
    if current_user.role == 'admin':
        if request.method == "GET":
            section = Section.query.all()
            return render_template("admin/add_book.html", section = section)
        if request.method == "POST":
            book_title = request.form.get("book_title")
            Author = request.form.get("Author")
            book_image = request.files.get("book_image")
            book_pdf = request.files.get("book_pdf")
            book_content = request.form.get("book_content")
            section_name = request.form.get("section_name") 
            book_image.save("static/books/book_image/" + book_image.filename)
            book_pdf.save("static/books/book_pdf/" + book_pdf.filename)
            book_price = request.form.get("book_price")
            date_added = datetime.now()
            new_book = Book(book_title = book_title, Author = Author, book_img_path = "static/books/book_image/" + book_image.filename, 
                            book_pdf_path= "static/books/book_pdf/" + book_pdf.filename, book_content = book_content, 
                            section_name = section_name, book_price = book_price, date_added = date_added)
            db.session.add(new_book)
            db.session.commit()
            flash("New Book added successfully")
            return redirect('/all_books')
    else:
        return "Please login as Admin to access this page"



@app.route("/edit_book/<int:book_id>", methods = ["GET","POST"])
@login_required
def edit_book(book_id):
    if current_user.role == 'admin':
        if request.method == "GET":
            section = Section.query.all()
            book = Book.query.filter_by(book_id = book_id).first()
            return render_template("admin/edit_book.html", book=book, section = section)
        if request.method == "POST":
            book_title = request.form.get("book_title")
            Author = request.form.get("Author")
            book_image = request.files.get("book_image")
            book_pdf = request.files.get("book_pdf")
            book_content = request.form.get("book_content")
            section_name = request.form.get("section_name") 
            book_image.save("static/books/book_image/" + book_image.filename)
            book_pdf.save("static/books/book_pdf/" + book_pdf.filename)
            book_price = request.form.get("book_price")

            book = Book.query.filter_by(book_id = book_id).first()
            book.book_title = book_title
            book.Author = Author
            book.book_content = book_content
            book.section_name = section_name
            book.book_price = book_price
            book.book_img_path = "static/books/book_image/" + book_image.filename
            book.book_pdf_path= "static/books/book_pdf/" + book_pdf.filename
            
            db.session.commit()
            flash('Book is Edited successfully','success')
            return redirect('/all_books')
    else:
        return "Please login as Admin to access this page"



@app.route('/<int:book_id>', methods=["GET"])
def getBook(book_id):
    book = Book.query.get(book_id)
    sections = Section.query.all()
    if current_user.role == 'admin':
        return render_template('admin/getbook.html', book = book)
    else:
        return render_template('user/getbook1.html', book = book, sections = sections)



@app.route("/delete_book/<int:book_id>")
@login_required
def delete_book(book_id):
    if current_user.role == 'admin':
        book = Book.query.filter_by(book_id = book_id).first()
        if Cart.query.filter_by(book_id = book_id).first() is not None:
            order = Cart.query.filter_by(book_id = book_id).first()
            if book.book_id != order.book_id:
                db.session.delete(book)
                db.session.commit()
                flash('Book is deleted successfully','success')
            else:
                flash('Book is in order list, Please donot delete', 'warning')
        else:
            db.session.delete(book)
            db.session.commit()
            flash('Book is deleted successfully','success')
        return redirect("/all_books")
    else:
        return "Please login as Admin to access this page"


@app.route("/admin_account", methods= ["GET", 'POST'])
@login_required
def admin_account():
    if request.method == "GET":
        section = Section.query.all()
        return render_template("admin_account.html", section = section)
        #return "admin account"
    if request.method == "POST":
        name = request.form["section_name"]
        existing_section =  Section.query.filter_by(section_name = name).first()
        if existing_section:
            flash("Section already registered")
            return redirect("/admin_dashboard")
        else:
            new_section = Section(name = name)
            db.session.add(new_section)
            db.session.commit()
            flash("New section added successfully")
            return redirect('/admin_dashboard')

@app.route("/cart")
@login_required
def cart():
    user_id = current_user.user_id
    cart_items = Cart.query.filter_by(user_id=user_id).all()
    allbook = Book.query.all()
    sections = Section.query.all()
    books = []
    final_total = 0
    for item in cart_items:
        if item.status == 0 or item.status == 2:
            book = Book.query.get(item.book_id)
            final_total += book.book_price
            books.append(book)
    return render_template('user/cart.html', cart = books, final_total = final_total, sections = sections)

@app.route('/<int:book_id>/add_to_cart', methods=["POST", "GET"])
@login_required
def add_to_cart(book_id):
    if current_user.is_authenticated:
        user_id = current_user.user_id
        requests = Cart.query.filter_by(user_id=user_id).all()
        print(len(requests))
        book = Book.query.filter_by(book_id = book_id).first()
        book_title = book.book_title
        book_price = book.book_price
        section_name = book.section_name
        date_issued = None
        date_return = None
        cart_item = Cart.query.filter_by(book_id = book_id, book_title = book_title, section_name = section_name, 
                                        book_price  =  book_price, user_id=user_id, date_issued = date_issued,  date_return= date_return ).first()
        if cart_item:
            flash('Book is already in order list', 'warning')

        else:
            if len(requests) <= 5:
                cart = Cart(book_id = book_id, user_id=user_id,  book_title = book_title, section_name = section_name, 
                                book_price  =  book_price, date_issued = date_issued,  date_return= date_return)
                cart.save_book()
                return redirect('/cart')
            else:
                flash('You can issue maximum 5 books')
    else:
        flash('You need to log in to add items to your cart', category='danger')
        return redirect('/')
    return redirect('/')

@app.route('/cart/<int:book_id>/remove', methods=["POST", "GET"])
def remove_from_cart(book_id):
    user_id = current_user.user_id
    cart_item = Cart.query.filter_by(book_id = book_id, user_id = user_id).first()

    if not cart_item:
        return redirect(url_for('cart'))

    else:
        cart_item.delete_book()

    return redirect(url_for('cart'))

@app.route('/cart/clear', methods=["POST", "GET"])
def clear_cart():
    user_id = current_user.user_id
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    for cart_item in cart_items:
        cart_item.delete_book()

    return redirect(url_for('cart'))


@app.route('/all_users', methods=["GET"])
@login_required
def all_users():
    if current_user.role == 'admin':
        if request.method == "GET":
            orders = Cart.query.all()
            users = User.query.all()
            sections = Section.query.all()
            return render_template('admin/all_users.html', users = users, sections = sections, orders =  orders)
    else:
        return "Please login as Admin to access this page"


@app.route('/all_books', methods=["GET"])
@login_required
def all_books():
    if current_user.role == 'admin':
        if request.method == "GET":
            books = Book.query.all()
            sections = Section.query.all()
            return render_template('admin/all_books.html', books = books, sections = sections)
    else:
        return "Please login as Admin to access this page"  

@app.route('/all_sections', methods=["GET"])
@login_required
def all_sections():
    if current_user.role == 'admin':
        if request.method == "GET":
            books = Book.query.all()
            
            sections = Section.query.all()
            return render_template('admin/all_sections.html', books = books, sections = sections) 
    else:
        return "Please login as Admin to access this page"


@app.route('/orders', methods=["POST", "GET"])
@login_required
def orders():
    if current_user.role == 'admin':
        if request.method == "GET":
            orders = Cart.query.all()
            num = len(orders)
            sections = Section.query.all()
            books = Book.query.all()
            
            return render_template("admin/orders.html", orders = orders, books = books, sections = sections, num = num)
    else:
        return "Please login as Admin to access this page"
           


@app.route('/admin/approve/<int:id>')
@login_required
def adminapprove(id):
    if current_user.role == 'admin':
        cart = Cart.query.filter_by(id = id).first()
        Cart('user_id', 'book_id', 'book_title', 'section_name', 'book_price').query.filter_by(id = id).update(dict(status = 1))
        cart.date_issued = datetime.now()
        cart.date_return = datetime.now() + timedelta(minutes=15)
        db.session.commit()
        flash('Approve successfully', 'success')
        return redirect('/orders')
    else:
        return "Please login as Admin to access this page"


@app.route('/admin/notapprove/<int:id>')
@login_required
def adminnotapprove(id):
    if current_user.role == 'admin':
        cart = Cart.query.filter_by(id = id).first()
        Cart('user_id', 'book_id', 'book_title', 'section_name', 'book_price').query.filter_by(id = id).update(dict(status = 2))
        db.session.commit()
        flash('Not Approve successfully', 'success')
        return redirect('/orders')
    else:
        return "Please login as Admin to access this page"


@app.route('/userbook')
@login_required
def userbook():
    user_id = current_user.user_id
    order = Cart.query.filter_by(user_id=user_id).all()
    sections = Section.query.all()
    mybooks = []
    for item in order:
        if item.status == 1 and item.date_return > datetime.now():

            book = Book.query.get(item.book_id)
            mybooks.append(book)
  
    return render_template('user/userbook.html', cart = mybooks, order = order, sections = sections)



@app.route("/search", methods=["GET","POST"])
@login_required
def search():
    if request.method == "GET":
        sections = Section.query.all()
        if current_user.role == 'admin': 
            return render_template("admin/search.html", sections = sections)
        else:
            return render_template("user/search1.html", sections = sections)
    if request.method == "POST":
        user_id = current_user.user_id
        user = User.query.filter_by(user_id = user_id)
        search_for = "%" + request.form["search_for"] + "%"
 
        books = []
        sections = Section.query.all()
        user_search = User.query.filter(User.user_name.like(search_for)).all()
        section_search = Section.query.filter(Section.section_name.like(search_for)).all()
        book_search = Book.query.filter(Book.book_title.like(search_for)).all()
       
        author_search = Book.query.filter(Book.Author.like(search_for)).all()
        for item in author_search:
            books.append(item)
        if current_user.role == 'admin': 
            return render_template("admin/search.html", user_search=user_search, section_search=section_search, 
                                book_search= book_search, author_search=author_search, books = books, sections = sections)
        else:
            return render_template("user/search1.html", user_search=user_search, section_search=section_search, 
                                book_search= book_search, author_search=author_search, books = books, sections = sections)


@app.route('/<int:book_id>/delete_from_cart')
@login_required
def delete_from_cart(book_id):
    if current_user.role == 'admin':
        cart = Cart.query.filter_by(book_id = book_id).first()
        #if cart.date_return <= datetime.now():
        db.session.delete(cart)
        db.session.commit()
        flash('Order is deleted successfully','success')
        return redirect('/orders')
    else:
        return "Please login as Admin to access this page"


@app.route('/<int:section_id>/section_books', methods=["GET"])
@login_required
def section_books(section_id):
    if request.method == "GET":
        books = Book.query.all()
        sections = Section.query.all()
        section = Section.query.filter_by(section_id=section_id).first()
        section_name = section.section_name
        if current_user.role == 'admin':
            return render_template('admin/sectionbook.html', books = books, section_name = section_name, sections = sections)
        else:
            return render_template('user/sectionbook1.html', books = books, section_name = section_name, sections = sections)

@app.route('/new_arrivals', methods=["GET"])
@login_required
def new_arrivals():
    if request.method == "GET":
           
            books = Book.query.order_by(Book.book_id.desc()).limit(4).all()
            sections = Section.query.all()
            return render_template('user/newarrivals.html', books = books, sections = sections)


@app.route('/policy', methods=["GET"])
@login_required
def policy():
    if request.method == "GET":
        sections = Section.query.all()
        return render_template('user/policy.html', sections = sections)
  