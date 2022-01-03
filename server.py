
from flask import Flask, render_template, send_file, make_response, url_for, Response, redirect, request 
import io
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from Script import Method
 
#initialise app
app = Flask(__name__)

@app.route('/' )
def index():
    return render_template('index.html',
                           PageTitle = "Landing page")

@app.route('/', methods = ["POST"] )
def plot_png():
    movie = request.form["movie"]

    if movie!="":
        fig = Method(movie)

        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype = 'image/png')
        #The created image will be opened on a new page
    
    else:
        return render_template('index.html',
                        PageTitle = "Landing page")
        #This just reloads the page if no file is selected and the user tries to POST. 

if __name__ == '__main__':
    app.run(debug = True)