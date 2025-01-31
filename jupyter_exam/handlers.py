import json
import requests
import os

from jupyter_server.base.handlers import APIHandler
from jupyter_server.utils import url_path_join
import tornado


class UserInfo(APIHandler):
    @tornado.web.authenticated
    def get(self):
        user = self.current_user
        sub = user.username
        name = user.name
        display_name = user.display_name
        print(f"sub: {sub}, name: {name}, display_name: {display_name}")

        self.finish(
            json.dumps(
                {
                    "sub": sub,
                    "name": name,
                    "display_name": display_name,
                }
            )
        )


class SubmitHandler(APIHandler):
    @tornado.web.authenticated
    def post(self):
        image = os.environ.get("JUPYTER_IMAGE") or "unknown"
        origin = self.get_origin()
        exam_url = os.environ.get("EXAM_URL") or "https://exam.spang-lab.de/api/submit"
        headers = {
            "Content-Type": "application/json",
            "Origin": origin,
        }
        try:
            data = self.get_json_body()
            if not data:
                raise ValueError("No data received")
            user = self.current_user
            sub = user.username
            name = user.name

            body = {
                "lecture": image,
                "user": {
                    "sub": sub,
                    "name": name,
                },
                "notebook": data,
            }
            response = requests.post(exam_url, headers=headers, json=body)
            response.raise_for_status()
            data = response.json()

            self.finish(json.dumps(data))
        except Exception as e:
            self.set_status(500)
            self.finish(json.dumps({"error": str(e)}))
            return


def setup_handlers(web_app):
    host_pattern = ".*$"
    base_url = url_path_join(web_app.settings["base_url"], "jupyter-exam")

    submit_url = url_path_join(base_url, "submit")
    user_url = url_path_join(base_url, "user")
    handlers = [
        (submit_url, SubmitHandler),
        (user_url, UserInfo),
    ]
    web_app.add_handlers(host_pattern, handlers)
