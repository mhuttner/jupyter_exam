import json
import requests

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado


class RouteHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        try:
            data = self.get_json_body()
            if not data:
                raise ValueError("No data received")
            user = self.get_current_user()
            if not user:
                raise ValueError("No user found")
            self.finish(json.dumps({"data": data}))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))
            return


def setup_handlers(web_app):
    host_pattern = ".*$"

    base_url = web_app.settings["base_url"]
    route_pattern = url_path_join(base_url, "jupyter-exam", "submit")
    handlers = [(route_pattern, RouteHandler)]
    web_app.add_handlers(host_pattern, handlers)
