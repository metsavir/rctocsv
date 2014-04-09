# -*- coding: utf-8 -*-
from flask import Flask, request,  render_template, make_response, abort
from bs4 import BeautifulSoup
import requests

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def resultcode():

    team_id = ""
    frm_start = ""
    frm_end = ""
    duration = ""
    error = ""

    if request.method == 'POST':
        team_id = request.form['team_id']
        frm_start = request.form['frm_start']
        frm_end = request.form['frm_end']
        duration = request.form['duration']

        if not frm_start:
            frm_start = '2014'

        if not frm_end:
            frm_end = '2015'

        url = "http://www.resultcode.fi/sarjat/joukkue/jou_ottelut.php?joukkue_id=" + \
         team_id + "&frm_alku=" + frm_start + "&frm_loppu=" + frm_end

        try:
            r  = requests.get(url)
            data = r.text
            soup = BeautifulSoup(data)

            if duration == "0":
                response = "Subject, Start Date, Start Time, Location\n"    
            else:
                response = "Subject, Start Date, End Date, Start Time, End Time, Location\n"

            tables = soup.find_all('table')[3:]
            rows = []

            for table in tables:
                rows += table.find_all('tr')

            if len(rows) > 0:
                for row in rows:
                    data = row.find_all("td")

                    if len(data) > 0:
                        startdate = data[1].get_text().strip()
                        st_raw = data[2].get_text().strip()
                        starttime = st_raw[:2] + ":" + st_raw[-2:]

                        match = data[3].get_text().strip() + " - " + data[5].get_text().strip()
                        location = data[7].get_text().strip()

                        if duration == "0":
                            row = match + ", " + startdate + ", " + starttime + ", " + location + "\n"
                        else:
                            endtime = str(int(st_raw[:2]) + int(duration)) + ":" + st_raw[-2:]
                            enddate = startdate

                            row = match + ", " + startdate + ", " + enddate + ", " + starttime + \
                            ", " + endtime + ", " + location + "\n"


                        response += row

                if 'download' in request.form:
                    response_dl = make_response(response)
                    response_dl.headers["Content-Disposition"] = "attachment; filename=" + team_id + "_" +\
                        frm_start + "_" + frm_end + ".csv"

                    return response_dl

                elif 'show' in request.form:
                    return render_template('layout.html', response=response, team_id=team_id, \
                        frm_start=frm_start, frm_end=frm_end, duration=duration)

            else:
                error = u"JoukkueID:lle " + team_id + u" ei löytynyt otteluita aikaväliltä " \
                        + frm_start + " - " + frm_end + "."
                return render_template('layout.html', team_id=team_id, \
                        frm_start=frm_start, frm_end=frm_end, duration=duration, error=error)


        except:
            abort(500)
    else:
        return render_template('layout.html', team_id=team_id, \
                        frm_start=frm_start, frm_end=frm_end, duration=duration)


if __name__ == '__main__':
    app.run()