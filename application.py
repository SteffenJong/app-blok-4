from flask import Flask, request, make_response, render_template, url_for
from Bio.Blast import NCBIXML, NCBIWWW
import mysql.connector


def verwerk_get_list_show(list):
    """ verwerkt de lijst naar een string die in de query gebruikt kan worden bij het select statement.
    :param list: lijst met alle aangevinkte parameters van website.
    :return: een string die in een query gezet kan worden.
    """
    first = True
    final_search = ""

    for term in list:
        if first:
            final_search += term
            first = False
        else:
            final_search += (r" ," + term)
    return final_search

def verwerk_get_list_search(list):
    """verwerkt de lijst naar een string die in de query gebruikt kan worden bij where statement.
    :param list: lijst met alle aangevinkte parameters van website.
    :return: een string die in een query gezet kan worden.
    """
    first = True
    final_search = ""

    for term in list:
        if first:
            final_search += term
            first = False
        else:
            final_search += (r" or " + term)
    return final_search


def get_list_blastrecord(blast_record):
    """verwerkt de output van blast tot een lijst die makkelijk weertegecven is op de website
    :param blast_record: blast resultaten
    :return: een 2d lijst met resultaat items per resultaat
    """
    lijst_res = []
    for alignment in blast_record.alignments:
            for hsp in alignment.hsps:
                hit_description = ""
                hit_id = ""
                ids = ""
                e_v = ""
                sc = ""
                gap = ""
                hit_description = alignment.hit_def
                hit_id = alignment.hit_id
                ids = hsp.identities
                e_v = hsp.expect
                sc = hsp.score
                gap = hsp.gaps
                lijst_res.append([hit_id, hit_description, e_v, sc, ids, gap])
    return lijst_res


app = Flask(__name__)


@app.route('/')
def homepage():
    """laat de home pagina
    :return: gerenderd html template voor de home pagina
    """
    resp = make_response(render_template("homepage.html"))
    return resp


@app.route('/database/', methods=['get', 'post'])
def database():
    """laat de database pagina en zorgt dat database te bevragen is van uit de website
        :return: gerenderd html template voor de database pagina
        """
    connection = mysql.connector.connect(host="hannl-hlo-bioinformatica-mysqlsrv.mysql.database.azure.com",
                                         user="rapwz@hannl-hlo-bioinformatica-mysqlsrv", db="rapwz", password="pwd123")

    searsch_in = request.form.getlist("search_in")
    show = request.form.getlist("show")
    zoekterm = request.form.get("zoekterm")

    final_show = ""
    final_search = ""

    final_search = verwerk_get_list_search(searsch_in)
    final_show = verwerk_get_list_show(show)

    quiry = ""
    resultaat = ""
    titel_tabel = show

    if zoekterm is not None:
        quiry = "select {} from blastresultatentabel where {} like '%{}%' limit 50".format(final_show, final_search,
                                                                                           zoekterm)

    if final_show is not "" and zoekterm is None:
        quiry = "select {} from blastresultatentabel limit 50".format(final_show)

    if quiry is not "":
        cursor = connection.cursor()
        cursor.execute(quiry)
        resultaat = cursor.fetchall()
        cursor.close()

    site = render_template('database.html', resultaat=resultaat, titel_tabel=titel_tabel)

    connection.close()

    return site


@app.route('/Blast', methods=['get', 'post'])
def blast():
    """ laat de blast pagina en zorgt dat er te blasten valt van uit de website
    :return: erenderd html template voor de blast pagina
    """
    program = ""
    sequentie = ""
    lijst_res = []
    lijst_titel_kol = []
    program = request.form.get("program")
    sequentie = request.form.get("sequentie")

    if program and sequentie is not "":
        print("blasting")
        result_handle = NCBIWWW.qblast(
            program=program, database="nr", sequence=sequentie)

        blast_records = NCBIXML.parse(result_handle)
        blast_record = next(blast_records)

        lijst_res = get_list_blastrecord(blast_record)

        lijst_titel_kol = ["accessiecode_ncbi", "description", "e_value", "score", "identities", "gaps"]
    print("done")

    resp = make_response(render_template("blast.html", lijst_res=lijst_res, lijst_titel_kol=lijst_titel_kol))
    return resp


@app.route('/about')
def about():
    """laat de about pagina
    :return: gerenderd html template voor de about pagina
    """
    resp = make_response(render_template("about.html"))
    return resp


if __name__ == '__main__':
    app.run()
