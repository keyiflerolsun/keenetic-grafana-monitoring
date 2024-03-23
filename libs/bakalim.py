from Kekik.cli        import konsol
import configparser, json, os, time
from typing           import Dict, List
from jsonpath_rw      import parse
from keenetic_api     import KeeneticClient, KeeneticApiException
from value_normalizer import normalize_value

def json_path_init(paths: Dict[str, str]):
    return {
        pathName: path
            if path == "~" else parse(path)
        for pathName, path in paths.items()
    }

class KeeneticCollector(object):
    def __init__(self, keenetic_client: KeeneticClient, metric_configuration: Dict[str, object]):
        self._keenetic_client = keenetic_client
        self._command: str    = metric_configuration["command"]
        self._params          = metric_configuration.get("param", {})
        self._root            = parse(metric_configuration["root"])
        self._tags            = json_path_init(metric_configuration["tags"])
        self._values          = json_path_init(metric_configuration["values"])

    def collect(self) -> List[dict]:
        try:
            response = self._keenetic_client.metric(self._command, self._params)
        except KeeneticApiException as e:
            konsol.log(
                f"`{self._command}` metriğinin toplanması, Keenetic API istisnası nedeniyle atlandı."
                f"Durum kodu: `{e.status_code}` | Yanıt: `{e.response_text}`"
            )
            return []

        roots      = self._root.find(response)
        metrics    = []
        start_time = time.time_ns()

        for root in roots:
            tags   = self._params.copy()
            values = {}

            for tag_name, tag_path in self._tags.items():
                if tag_path == "~":
                    tags[tag_name] = root.path.fields[0]
                elif str(tag_path).startswith("`parent`"):
                    full_path      = root.full_path.child(tag_path)
                    tags[tag_name] = self.get_first_value(full_path.find(response))
                else:
                    tags[tag_name] = self.get_first_value(tag_path.find(root.value))

            for value_name, value_path in self._values.items():
                value = self.get_first_value(value_path.find(root.value))
                if value is not None:
                    values[value_name] = normalize_value(value)

            if values.__len__() == 0:
                continue

            metric = self.create_metric(self._command, tags, values)
            # print(json.dumps(metric))
            metrics.append(metric)

        metrics.append(self.create_metric(
            "collector",
            {"command"  : self._command},
            {"duration" : (time.time_ns() - start_time)}
        ))

        return metrics

    @staticmethod
    def create_metric(measurement, tags, values):
        return {
            "measurement" : measurement,
            "tags"        : tags,
            "time"        : time.time_ns(),
            "fields"      : values
        }

    @staticmethod
    def get_first_value(array):
        return array[0].value if array and len(array) > 0 else None


if __name__ == "__main__":
    pwd                   = os.path.dirname(os.path.realpath(__file__))
    metrics_configuration = json.load(open(f"{pwd}/../config/metrics.json", "r"))

    metrics = metrics_configuration["metrics"]
    config  = configparser.ConfigParser(interpolation=None)
    config.read(f"{pwd}/../config/config.ini", encoding="utf-8")

    keenetic_config = config["keenetic"]
    konsol.log(f"Router'a Bağlanıyor: {keenetic_config['admin_endpoint']}")

    collectors = []
    with KeeneticClient(
        keenetic_config["admin_endpoint"],
        keenetic_config.getboolean("skip_auth"),
        keenetic_config["login"],
        keenetic_config["password"]
    ) as kc:
        for metric_configuration in metrics:
            konsol.log(f"Metrik Yapılandırılıyor: `{metric_configuration['command']}`")
            collectors.append(KeeneticCollector(kc, metric_configuration))

        wait_interval = config["collector"].getint("interval_sec")
        konsol.log(f"Yapılandırma Tamamlandı. `{wait_interval}` saniye aralıklarla toplanıyor..")
        while True:
            for collector in collectors:
                metrics = collector.collect()
                konsol.print(metrics)
            time.sleep(wait_interval)