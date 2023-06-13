
from flask import Flask, render_template, url_for, request, redirect, session, abort, jsonify
from authlib.integrations.flask_client import OAuth
from constants import CITIES
from parsers import find_flats_cian, find_flats
from auth import appConf, TOKEN
from firebase import add_liked_to_database, get_liked_from_database, user_creation

app = Flask(__name__)

CITIESMAIN = {}

for city, num in CITIES:
    CITIESMAIN[city] = num

app.secret_key = appConf.get("FLASK_SECRET")

oauth = OAuth(app)

oauth.register(
    "FlatMap",
    client_id=appConf.get("OAUTH2_CLIENT_ID"),
    client_secret=appConf.get("OAUTH2_CLIENT_SECRET"),
    client_kwargs={
        "scope": "openid profile email"},
    server_metadata_url=f'{appConf.get("OAUTH2_META_URL")}',
)


@app.route("/signin-google")
def googleCallback():
    token = oauth.FlatMap.authorize_access_token()
    session["user"] = token
    user_email = session.get('user').get('userinfo').get('email')
    user_creation(user_email)
    return redirect(url_for("registration"))


@app.route("/google-login")
def googleLogin():
    if "user" in session:
        abort(404)
    return oauth.FlatMap.authorize_redirect(redirect_uri=url_for("googleCallback", _external=True))


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("registration"))


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        return render_template("filter_page.html")
    else:
        return render_template("index.html")


@app.route('/filters', methods=['POST', 'GET'])
def main():
    if request.method == 'POST':
        one_room = 1 if request.form.get("one_room") == "on" else 0
        two_rooms = 1 if request.form.get("two_room") == "on" else 0
        three_rooms = 1 if request.form.get("three_room") == "on" else 0
        four_rooms = 1 if request.form.get("four_room") == "on" else 0
        min_price = int(request.form.get("min_price")
                        ) if request.form.get("min_price") != "" else 0
        max_price = int(request.form.get("max_price")) if request.form.get(
            "max_price") != "" else "1000000000"

        # city = CITIESMAIN[request.form.get("location")] if request.form.get(
        #     "location") != "" else ""

        flats = []
        rooms = [one_room, two_rooms, three_rooms, four_rooms]
        r = []
        for i, room in enumerate(rooms):
            if room:
                r.append(i + 1)
        if len(r) == 0:
            r.append(1)
        for i in range(1):
            # url_cian = f"https://www.cian.ru/cat.php?deal_type=sale&engine_version=2&offer_type=flat&p={i}&region=1&room1={one_room}&room2={two_rooms}&room3={three_rooms}&room4={four_rooms}&maxprice={max_price}&minprice={min_price}&region={city}"
            url_other = f"https://ads-api.ru/main/api?user=x545275@gmail.com&token={TOKEN}&city={request.form.get('location')}&price1={min_price}&price2={max_price}&category_id=2&param[1943]=Продам&param[1945]={max(r)}"
            # flats += find_flats_cian(url_cian)
            flats += find_flats(url_other)

        flats.sort(key=lambda x: x['model_prediction'], reverse=True)

        return render_template("flats_showcase.html", flats=flats)

    else:
        return render_template("filter_page.html")


@app.route('/dreamflat', methods=['POST'])
def flatpage():
    name = request.form['name']
    price = request.form['price']
    photos = request.form.getlist('photos[]')
    description = request.form['description']
    rooms = request.form['rooms']
    space = request.form['space']
    floor = request.form['floor']
    link = request.form['link']
    address = request.form['address']
    return render_template('flat_page.html', name=name, price=price, description=description, photos=photos, rooms=rooms, space=space, floor=floor, link=link, address=address)


@app.route('/saved_flats', methods=['POST'])
def savepage():
    if "user" in session:
        name = request.form['name']
        photos = request.form.getlist('photos[]')
        price = request.form['price']
        description = request.form['description']
        rooms = request.form['rooms']
        space = request.form['space']
        floor = request.form['floor']
        link = request.form['link']
        address = request.form['address']
        return render_template('flat_page.html', name=name, price=price, description=description, photos=photos, rooms=rooms, space=space, floor=floor, link=link, address=address)
    else:
        return render_template('registration.html', session=session.get('user'))

@app.route('/save', methods=['POST'])
def save():
    user_email = session.get('user').get('userinfo').get('email')

    name = request.form.get('name')
    price = request.form.get('price')
    description = request.form.get('description')
    photos = request.form.getlist('photos[]')
    index = request.form.get('index')
    link = request.form.get('link')
    rooms = request.form.get('rooms')
    space = request.form.get('space')
    floor = request.form.get('floor')
    address = request.form.get('address')
    result = add_liked_to_database(user_email, {
                                   "name": name, "price": price, "description": description, "photos": photos, "index": index, "link": link, "rooms": rooms, "floor": floor, "space": space, "address": address })
    return jsonify(result="Success")


@app.route('/login')
def registration():
    return render_template("registration.html", session=session.get("user"))


@app.route('/about_us')
def info():
    return render_template("about_us.html")


@app.route('/saved_flats')
def saved():
    user_email = session.get('user').get('userinfo').get('email')
    flats = get_liked_from_database(user_email)
    return render_template("saved_flats.html", flats=flats)


@app.route('/about_us')
def about_us():
    return render_template("about_us.html")


if __name__ == "__main__":
    app.run(debug=True)
