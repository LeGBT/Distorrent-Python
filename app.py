from bottle import get, post, run, request, static_file
import json
import requests
import untangle
import re
import datetime
from threading import Timer
import subprocess


with open('data.json') as f:
    data = json.load(f)


def update_data():
    with open('data.json', 'w') as f:
        json.dump(data, f)


main_html = """<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="utf-8">
    <meta http-equiv="Content-type" content="text/html;charset=UTF-8" />
    <title>THOR</title>
    <link rel="stylesheet" type="text/css" href="/static/style.css">
</head>
<body>
<div id="lapage">
    <header>
    <div id="logo">
        <img src='/static/thor.png' alt='Thor' />
    </div>
        <nav>
            <ul>
                <li><a href="/rss">RSS</a></li>
                <li><a href="/filter">Filtres</a></li>
                <li><a href="/scan">Scan</a></li>
            </ul>
        </nav>
    </header>
    <section>

        {0}

    <footer>
        <div class="e1">
            <p>{1}</p>
        </div>
        <p class='shinyfooter'> Contain some Alban Avenant inside </p>
    </footer>
</div>
</body>
</html>"""


def gen_html(maindata):
    return main_html.format(maindata, "<br><br>".join(data["log"]))

welcome_html = """
<h1>Bienvenue !</h1>
<p class='simple'>Je marche mieux maintenant !</p>"""


@get('/static/<filename>')
def server_static(filename):
    return static_file(filename, root='static')


@get('/')
def index():
    return gen_html(welcome_html)


@get('/scan')
def scan():
    for rss in data["rss"]:
        r = requests.get(data["rss"][rss])
        if r.status_code == 200:
            rssfile = untangle.parse(r.text)
            for item in rssfile.rss.channel.item:
                for i, flt in enumerate(data["filter"]):
                    if re.match(".*"+flt[1]+"[^0-9]*0?"+str(flt[2]),
                                item.title.cdata, flags=re.I):
                        subprocess.run(["transmission-remote", "--add",
                                        item.link.cdata])
                        del data["log"][0]
                        l = datetime.datetime.now().strftime(
                            '%Y/%m/%d %Hh%M') + " " + flt[0]
                        data["log"].append(l)
                        data["filter"][i][2] += 1
                        update_data()

    return gen_html("""
    <div class='simple'>
        <b>scan effectué :
            {0} rss.
        </b>
        </div>""".format(len(data["rss"])))


def rss_list():
    rsslist = ['''<p><div class="thename">{0}
               <a href="/rss/{0}" class="theadress">{1}</a>
               </div> <br/></p>'''.format(r, address)
               for r, address in data["rss"].items()]
    out = "".join(rsslist)
    return out


newrssstring = '<br><a href="/new_rss" class="special">Nouveau</a>'


@get('/rss')
def get_rss_list(msg=""):
    return gen_html(msg+rss_list()+newrssstring)


@get('/new_rss')
def new_rss():
    return gen_html("""
        <form action="/new_rss" method="post">
            <label>Nom:</label><br/>
            <input name="name" type="text" value=""/>
            <br><br>
            <label>Adresse:</label><br/>
            <input name="adress" type="text" value="">
            <br><br>
            <input type="submit" value="Ajouter un RSS"/>
        </form>
        <br><br>
        <a href="/rss" class="special">Retour</a>""")


@post('/new_rss')
def do_new_rss():
    name = request.forms.get('name')
    adress = request.forms.get('adress')
    if adress == "" or name == "":
        return get_rss_list('''<p style="color: red">Tous les champs
 doivent être renseignés</p>''')
    data["rss"].update({name: adress})
    update_data()
    return get_rss_list()


@get('/rss/<name>')
def get_rss(name):
    return gen_html("""
        <p><div class='simple'>
            <b>Nom:</b>
           {0}
        </div></p>
        <p><div class='simple'>
            <b>Adresse:</b>
           {1}
        </div></p><p></p><br>
        <a href="/edit_rss/{0}" class="special" >Éditer</a><p></p> <br/>
        <a href="/destroy_rss/{0}" confirm="Vous êtes sûr ?" class="special">
            Supprimer</a><p></p> <br/>
        <a href="/rss" class="special">Retour</a>
        """.format(name, data["rss"][name]))


@get('/edit_rss/<name>')
def edit_rss(name):
    return gen_html("""
        <form action="/edit_rss/{0}" method="post">
            <label>Nom:</label><br/>
            <input name="name" type="text" value="{0}"/>
            <br><br>
            <label>Adresse:</label><br/>
            <input name="adress" type="text" value="{1}">
            <br><br>
            <input type="submit" value="Mettre à jour"/>
        </form>
        <br><br>
        <a href="/rss" class="special">Retour</a>
        """.format(name, data["rss"][name]))


@post('/edit_rss/<oldname>')
def do_edit_rss(oldname):
    name = request.forms.get('name')
    adress = request.forms.get('adress')
    del data["rss"][oldname]
    data["rss"].update({name: adress})
    update_data()
    return get_rss(name)


@get('/destroy_rss/<name>')
def destroy_rss(name):
    del data["rss"][name]
    update_data()
    return gen_html('''<p style="color: green">{0} a
 été supprimé.</p>'''.format(name) + rss_list()+newrssstring)


def filter_list():
    filterlist = ['''<p><div class='filter'><div class="thename">{3}
        <a href="/filter/{0}" class="theadress">{2}</a>
        </div>
        <a href="/inc_filter/{0}" class="incdec" >+</a>
        <a href="/dec_filter/{0}" class="incdec" >-</a>
        </div>
        <br/></p>'''.format(i, filtr[0], filtr[1],
                            "{0} {1}".format(filtr[0], filtr[2]))
                  for i, filtr in enumerate(data["filter"])]
    out = "".join(filterlist)
    return out

newfilterstring = '<br><a href="/new_filter" class="special">Nouveau</a>'


@get('/filter')
def get_filter_list(msg=""):
    return gen_html(msg+filter_list()+newfilterstring)


@get('/new_filter')
def new_filter():
    return gen_html("""
    <form action="/new_filter" method="post">
        <label>Nom:</label><br>
        <input name="name" type="text" value=""/>
        <br><br>
        <label>Expression régulière :</label><br/>
        <input name="regexp" type="text" value=""/>
        <br><br>
        <label >Épisode:</label><br/>
        <input name="ep" type="text" value=""/>
        <br><br>
        <input type="submit" value="Ajouter"/>
    </form>
    <br><br>
    <a href="/filter" class="special">Retour</a>""")


@post('/new_filter')
def do_new_filter():
    name = request.forms.get('name')
    regexp = request.forms.get('regexp')
    ep = request.forms.get('ep')
    if regexp == "" or name == "":
        return get_filter_list('''<p style="color: red">Tous les champs
 doivent être renseignés</p>''')
    ep = int(ep)
    data["filter"].append([name, regexp, ep])
    update_data()
    return get_filter_list()


@get('/filter/<i>')
def get_filter(i):
    fltr = data["filter"][int(i)]
    return gen_html("""
    <p><div class='simple'><b>Nom:</b>
    {1}</div></p>
    <p><div class='simple'><b>Expression régulière :</b>
    {2}</div></p>
    <p><div class='simple'><b>Episode:</b>{3}</div></p>
    <br>
    <a href="/edit_filter/{0}" class="special" >Edit</a><p></p> <br/>
    <a href="/destroy_filter/{0}" confirm="Vous êtes sûr ?" class="special">
    Supprimer</a><p></p><br>
    <a href="/filter" class="special">Retour</a>
        """.format(i, fltr[0], fltr[1], fltr[2]))


@get('/edit_filter/<i>')
def edit_filter(i):
    fltr = data["filter"][int(i)]
    return gen_html("""
    <form action= /edit_filter/{0} method="post">
    <label>Name:</label><br/>
    <input name="name" type="text" value= {1} />
    <br><br>
    <label >Expression régulière :</label><br/>
    <input name="regexp" type="text" value= {2} />
    <br><br>
    <label >Episode:</label><br/>
    <input name="ep" type="text" value={3} />
    <br><br>
    <input type="hidden" name="id" value= id />
    <input type="submit" value="Mettre à jour" />
    </form>
    <br><br>
    <a href="/filter" class="special">Retour</a>
    """.format(i, fltr[0], fltr[1], fltr[2]))


@post('/edit_filter/<i>')
def do_edit_filtr(i):
    name = request.forms.get('name')
    regexp = request.forms.get('regexp')
    ep = request.forms.get('ep')
    ep = int(float(ep))
    if regexp == "" or name == "":
        return get_rss_list('''<p style="color: red">Tous les champs
 doivent être renseignés</p>''')
    del data["filter"][int(i)]
    data["filter"].append([name, regexp, ep])
    update_data()
    return get_filter(len(data["filter"])-1)


@get('/destroy_filter/<i>')
def destroy_filter(i):
    name = data["filter"][int(i)][0]
    del data["filter"][int(i)]
    update_data()
    return gen_html('''<p style="color: green">{0} a
 été supprimé.</p>'''.format(name) + filter_list()+newfilterstring)


@get('/inc_filter/<i>')
def inc_filter(i):
    data["filter"][int(i)][2] += 1
    update_data()
    return get_filter_list('''<p style="color: green">{0}
 a été incrémenté</p>'''.format(
        data["filter"][int(i)][0]))


@get('/dec_filter/<i>')
def dec_filter(i):
    ep = data["filter"][int(i)][2]
    data["filter"][int(i)][2] = max(0, ep-1)
    update_data()
    return get_filter_list('''<p style="color: green">{0}
    a été décrémenté</p>'''.format(
        data["filter"][int(i)][0]))


def schedule():
    scan()
    Timer(41*60, schedule).start()

schedule()
run(host='0.0.0.0', port=4001, debug=True)
