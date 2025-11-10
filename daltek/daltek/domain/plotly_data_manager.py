# daltek/domain/dashboard_data.py
class PlotlyDataManager:
    """
    Clase para manejar múltiples datasets y preparar los datos
    para diferentes widgets y gráficos de un dashboard.
    """

    def __init__(self):
        self.datasets = {}

    def add_dataset(self, name, dataset):
        """Agrega un dataset"""
        self.datasets[name] = dataset

    def get_dataset(self, name):
        return self.datasets.get(name)

    def summary_table(self, dataset_name, group_by=None, agg=None):
        """
        Devuelve un resumen tabular listo para un widget tipo tabla.
        """
        ds = self.get_dataset(dataset_name)
        if not ds:
            return None
        if group_by:
            ds = ds.group_by(group_by, agg)
        return ds.to_dict()

    def prepare_for_plot(self, dataset_name, x, y, kind="line"):
        """
        Prepara los datos en formato dict para Plotly o cualquier librería.
        kind: 'line', 'bar', 'pie', etc.
        """
        ds = self.get_dataset(dataset_name)
        if not ds:
            return None
        return {"x": ds.df[x].tolist(), "y": ds.df[y].tolist(), "type": kind}

    def filter_dataset(self, dataset_name, **conditions):
        ds = self.get_dataset(dataset_name)
        if ds:
            return ds.filter_rows(**conditions)
        return None
