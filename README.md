# Keenetic Grafana Monitör

- `config/__config.ini` dosyasında keenetic arayüzünüzün kullanıcı adı ve şifresini belirtin.
  - dosya adını `config.ini` olarak değiştirin.

```bash
docker compose up -d --build
```

komutu ile konteynerleri başlatın ve ardından Grafana Arayüzüne erişin.

```txt
Grafana Arayüzü : http://127.0.0.1:3000
Grafana User    : admin
Grafana Pass    : admin
```

[Home > Connections > Your connections > Data sources](http://127.0.0.1:3000/connections/your-connections/datasources)

Adresinden yeni bir `InfluxDB` veri kaynağı oluşturun.

```txt
URL      : http://influxdb:8086
DATABASE : keenetic
USER     : merhaba
PASSWORD : dunya
```

Ardından `grafana-dashboard.json` dosyasını `Import` edin.
