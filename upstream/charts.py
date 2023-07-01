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
import matplotlib.dates as mdates
from matplotlib.figure import Figure
import matplotlib.ticker as ticker

from upstream.extensions import db


class EventChartBuilder:
    def __init__(self, event):
        self.event = event
        # breakpoint()
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
        fig = Figure(figsize=(7.0, 5.0))
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

        sales = df.groupby(['market_id', df['starts'].dt.date]).agg({'quantity': 'sum'})

        labels = [market.date for market in df['starts']]
        
        for market in markets:
            if sales['quantity'].get(market.id) is not None:
                ax.plot(sales['quantity'].get(market.id), marker='o', label=market.name)
                ax.fill_between(sales['quantity'],sales['quantity'], 0, facecolor=colors[market.id], color=colors[market.id], alpha=0.2)
                ax.set_xticklabels(market.name, rotation=40, ha="right")

        ax.legend()
        ax.grid(True)
        ax.set_ylabel("Sales")
        ax.set_xlabel("Date")
        ax.set_xlim([df['starts'].dt.date.min(), df['starts'].dt.date.max()])
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%d/%y"))
        ax.yaxis.set_major_locator(ticker.MaxNLocator(integer=True))
        plt.rc('font', size=9)

        for spine in ax.spines.values():
            spine.set_edgecolor((0, 0, 0, 0.1))
        fig.tight_layout()
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
        fig = Figure(figsize=(7.0, 5.0))
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
        plt.xticks(rotation=40, ha="right")
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
