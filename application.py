from flask import Flask, request, make_response, render_template, url_for
import mysql.connector

app = Flask(__name__)


@app.route('/', methods=['get', 'post'])
def homepage():
    resp = make_response(render_template("homepage.html"))
    return resp


@app.route('/database/', methods=['get', 'post'])
def database():
    show = ""
    search = ""
    search_in = ""
    connection = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                         user="rapwz@hannl-hlo-bioinformatica-mysqlsrv", db="rapwz", password="pwd123")


    searsch_in = request.form.getlist("search_in")
    show = request.form.getlist("show")
    zoekterm = request.form.get("zoekterm")
    print(searsch_in)
    print(show)
    print(zoekterm)

    final_show = ""
    final_search = ""
    final_search_in = ""
    first = True

    for term in searsch_in:
        if first:
            final_search += term
            first = False
        else:
            final_search += (r" ," + term)

    first = True

    for term in show:
        if first:
            final_show += term
            first = False
        else:
            final_show += (r", " + term)

    first = True

    for term in searsch_in:
        if first:
            final_search_in += term
            first = False
        else:
            final_search_in += (r", " + term)

    print("final search:", final_search)
    print("final show:", final_show)
    print("zoekterm:", zoekterm)

    quiry = ""
    resultaat = ""

    if zoekterm is not None:
        quiry = "select {} from blastresultatentabel where {} like '%{}%' limit 50".format(final_show, final_search_in, zoekterm)
        cursor = connection.cursor()
        cursor.execute(quiry)
        resultaat = cursor.fetchall()
        cursor.close()
        print(resultaat, "-" * 80)
        print("zoekterm is not none")

    if final_show is not "" and zoekterm is None:
        quiry = "select {} from blastresultatentabel limit 50".format(final_show)
        cursor = connection.cursor()
        print("zoekterm is none ")
        print(final_show)
        cursor.execute(quiry)
        resultaat = cursor.fetchall()
        cursor.close()
        print(resultaat, "-" * 80)


    print(quiry)

    site = render_template('database.html', resultaat=resultaat)

    connection.close()



    return site


if __name__ == '__main__':
    app.run()
