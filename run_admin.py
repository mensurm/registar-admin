__author__ = 'mensur'

from admin import app

app.debug = True
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)