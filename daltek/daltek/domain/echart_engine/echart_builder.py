class EchartJSONBuidler:
    def __init__(self):
        pass

    def build_json(self, data):
        # Placeholder for building Echart JSON
        echart_json = {
            "title": {"text": "Sample Echart"},
            "tooltip": {},
            "legend": {"data": ["Example"]},
            "xAxis": {"data": [item["category"] for item in data]},
            "yAxis": {},
            "series": [
                {
                    "name": "Example",
                    "type": "bar",
                    "data": [item["value"] for item in data],
                }
            ],
        }
        return echart_json
