import base64
from io import BytesIO
from sqlalchemy import and_

# matplotlib has to be opened without the GUI event loop connection to run on the server.
# see https://stackoverflow.com/questions/51188461/using-pyplot-close-crashes-the-flask-app
import matplotlib
import pandas as pd

matplotlib.use("agg")

from matplotlib import pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.backends.backend_svg import FigureCanvasSVG
from matplotlib.figure import Figure

from upstream.extensions import db


class EventChartBuilder:
    def __init__(self, event):
        self.event = event

    def build(self):
        # Build the chart
        data = {
            "labels": [],
            "sold": [],
            "remains": [],
        }

        # For each event:
        for item in self.event.inventory.all():
            data["labels"].append(item.item.name)
            items = self.event.inventory.all()
            # Get the number of each item taken
            data["sold"].append(item.sold)
            data["remains"].append(item.available)

        return data

class ItemChartBuilder:
    # Handle creating multi-line plots to show sales at events.
    # This is for single items
    def __init__(self, item):
        self.item = item

    def __create_line_figure(self):
        from upstream.models import Event, Market, Transaction
        markets = Market.query.all()
        colors = ['#000', '#b73351', '#7abbff' ]
        fig = Figure(figsize=(10.0, 5.0))
        ax = fig.subplots(1, 1)

        df = pd.read_sql(
            db.session.query(
                Event, 
                Transaction).outerjoin(
                    Event, 
                    Transaction.event_id == Event.id, 
                    ).filter(Transaction.event_item_id == self.item.id).statement, 
            con=db.engine
        )

        sales = df.groupby(['market_id', 'starts']).agg({'quantity': 'sum'})

        for market in markets:
            if sales['quantity'].get(market.id) is not None:
                ax.plot(sales['quantity'].get(market.id), marker='o', color=colors[market.id], label=market.name)

        plt.xticks(rotation=45)
        ax.tick_params(axis="x", labelsize=10)
        ax.legend()
        ax.grid(True)

        return fig
    
    def build(self):
        fig = self.__create_line_figure()
        output = BytesIO()
        FigureCanvasSVG(fig).print_svg(output)
        data = output.getvalue().decode("ascii")
        return data


class ChartService:
    def __init__(self, data):
        # Accept a series as list of tuples with the (x, y) defined
        self.data = data

    def __create_pie_figure(self):
        fig = Figure(figsize=(4.0, 3.0))
        labels = self.data["labels"]
        sizes = self.data["series"]

        colors = ["#32c192", "#e9164f"]

        px = 1 / plt.rcParams["figure.dpi"]

        ax1 = fig.subplots()
        ax1.pie(sizes, labels=labels, colors=colors, startangle=90)
        ax1.axis("equal")

        return fig

    def __create_stacked_bar_figure(self):
        fig = Figure()
        labels = self.data["labels"]
        sold = self.data["sold"]
        remains = self.data["remains"]
        width = 0.5

        fig, ax = plt.subplots()

        ax.bar(labels, sold, width, label="Sold", color="#32c192")
        ax.bar(labels, remains, width, label="Remaining", bottom=sold, color="#3c637a")

        ax.set_ylabel("Total")
        ax.set_xlabel("Items")
        ax.legend()
        plt.xticks(rotation=45)
        plt.tick_params(axis="x", labelsize=10)
        plt.tight_layout()

        return fig

    def stacked_bar(self):
        fig = self.__create_stacked_bar_figure()
        output = BytesIO()
        FigureCanvasSVG(fig).print_svg(output)
        data = output.getvalue().decode("ascii")
        return data

    def pie(self):
        fig = self.__create_pie_figure()
        output = BytesIO()
        fig.savefig(output, format="png")
        output.seek(0)
        data = base64.b64encode(output.getbuffer()).decode("ascii")
        FigureCanvas(fig).print_png(output)
        return data
