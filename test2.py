from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import plotly.graph_objects as go

app = FastAPI()

# @app.get("/", response_class=HTMLResponse)
# async def plot():
#     # Dummy-Daten
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[10, 15, 7, 12], mode='lines', name='Temperatur'))

#     # HTML-Code generieren
#     graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

#     # HTML-Seite zurückgeben
#     html_content = f"""
#     <html>
#         <head>
#             <title>Plotly Diagramm</title>
#         </head>
#         <body>
            
#             {graph_html}
#         </body>
#     </html>
#     """
#     return HTMLResponse(content=html_content)


from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
import plotly.graph_objects as go

app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def plot(request: Request):
    # Dummy-Daten
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=[1, 2, 3, 4], y=[0,0,0,0], mode='lines', name='Temperatur'))
    graph_html = fig.to_html(full_html=False, include_plotlyjs='cdn')

    return templates.TemplateResponse("plot.html", {"request": request, "graph_html": graph_html})
