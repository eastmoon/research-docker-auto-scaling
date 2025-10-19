# Docker auto scaling

考量 [Kubernetes](https://github.com/eastmoon/infra-kubernetes) 的設計方向與用途，在雲端系統著實恰當，但若考量只是主機本地服務的小規模運用，且需逐步擴大適用範圍以整合入 Kubernetes。

本專案是基於上述概念，調查 Docker 的服務擴展 ( Scaling ) 機制，以及自行設計自動擴展 ( autoscaling )、負載平衡 ( load balancing ) 控制機制等；並配合 [ISA](https://github.com/eastmoon/infrastructure-service-application) 專案架構，以配置方式建構服務。

## 環境

本專案基於 [ISA](https://github.com/eastmoon/infrastructure-service-application) 專案結構設計。

### 啟動開發環境

```
# 啟動開發環境
do dev
# 進入開發容器
do dev --into
```

### 執行配置

+ 使用命令，於開發容器內
```
isa exec default
```
+ 使用路由，非開發容器內
```
curl -X POST http://localhost:8080/isa/exec/default
```

## Nginx LoadBalancer

In NGINX, an "upstream" block defines a group of backend servers to which NGINX can proxy requests. This is commonly used for load balancing and routing requests to a cluster of application servers or web servers.

+ [Module ngx_http_upstream_module](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#upstream)

Load balancing mode :

+ Round Robin – Requests are distributed evenly across the servers, with server weights taken into consideration. This method is used by default; there is no directive for enabling it.
+ [Least Connections](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#least_conn) – A request is sent to the server with the least number of active connections. This method also takes server weights into consideration.
+ [IP Hash](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#ip_hash) – The server to which a request is sent is determined from the client IP address.
+ [Hash](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#hash) – The server to which a request is sent is determined from a user‑defined key.
+ [Least Time (NGINX Plus only)](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#least_time) – For each request, NGINX Plus selects the server with the lowest average latency and the lowest number of active connections.
+ [Random (NGINX Plus only)](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#random) – Each request will be passed to a randomly selected server.

標準的啟用設定參考範例：

+ [Docker Compse](./conf/docker/docker-compose-nginx-lb.yml) 配置
    - 使用 Round Robin 的 [Nginx 設定](./infra/loadbalancer/conf.d/default.conf)，此範例嘗試用 include 動態指定配置內容
    - 使用 Least Connections 的 [Nginx 設定](./infra/loadbalancer-least-connected/conf.d/default.conf)，此範例採用標準寫法配置內容
+ 啟用範例：
```
# 啟動環境
do loadbalancer
# 進入環境
do loadbalancer --into
```
+ 執行測試 ```bash test-nginx-default-lb.sh```，預期輸出結果如下
```
root@isa:/test# bash test-nginx-default-lb.sh
Worker 1 : 600
Worker 2 : 400
total execute 17 seconds
```

本範例使用 Round Robin 的預設負載平衡 ( load balancing ) 機制，測試主要發送 1000 次請求並確認執行結果使否如權重設定一樣的 3:2 執行比重。

## Docker Compose scaling

若要在 Docker 管理服務擴展 ( Scaling )，必需基於 Compsoe 機制，且有兩個方式：

#### Using docker compose up --scale.

+ [docker compose up](https://docs.docker.com/reference/cli/docker/compose/up/)
    - ```--scale```：Scale SERVICE to NUM instances. Overrides the scale setting in the Compose file if present.
+ 範例
```
docker compose up -d --scale web=3
```

透過 ```docker compose up``` 指令啟動指定 web 服務並且擴展為 3 個服務。

#### Using docker compose file deploy specification

+ [Compose Deploy Specification](https://docs.docker.com/reference/compose-file/deploy/)
+ 範例
    - [Docker Compse](./conf/docker/docker-compose-autoscaling.yml) 配置
    - 使用 Round Robin 的 [Nginx 設定](./infra/loadbalancer-to-docekr-scaling/conf.d/default.conf)
+ 啟用範例：
```
# 啟動環境
do autoscaling
# 進入環境
do autoscaling --into
```    
+ 執行測試 ```bash test-docker-default-lb```，檢測 Docker compose 對 service 的分流
    - 當 Docker compose 透過配置啟動服務擴展，其服務容器皆會歸屬在相同服務下，可以透過以下方式知悉此服務下有多少容器。
        + ```nslookup [service-name]```：使用 DNS 工具檢查目標域名下包括的服務容器網址。
        + ```docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $(isa infra ps | grep [service-name] | awk '{print $1}')```：藉由 ```isa infra ps ``` 包裝的 Docker compose 指令取得執行容器清單，過濾服務名稱後，以實際容器名稱與 Docker 查詢並取回網址設定。
+ 執行測試 ```bash test-docker-nginx-lb```，檢測 Nginx 負載平衡

在 Docker 對服務擴展後，雖然會提供一個域名作為進入點並分流內容，但在 1000 次請求下的容器被呼叫的次數約為 6:4 上下反覆跳動，而透過負載平衡則是穩定在 1:1 平均執行狀態。

#### Docker Event-driven Autoscaling

參考 [Kubernetes Event-driven Autoscaling (KEDA)](https://keda.sh/) 設計理念，運用 ISA 機制對擴展目標服務。

+ ISA 自動擴展模組 [autoscaling](./app/modules/autoscaling.py)
+ ISA 自動擴展配置 [default](./app/configs/default.yml)
  - autoscaling.container.name : 必要參數，指定擴展的服務名稱
  - autoscaling.deploy.scale : 指定要擴大或減少，若不提供則預設為擴大
  - autoscaling.deploy.replicas.up : 指定可擴大的服務上限數量，若不提供會無限擴大
  - autoscaling.deploy.replicas.down : 指定可減少的服務下限數量，若不提供則最少減少至 1
  - 為第一步執行服務擴展、第二步重啟負載平衡，將 ```autoscaling``` 改為 ```Step1.module: autoscaling``` 與 ```Step2.module: autoscaling```，意指此兩階段都使用 autoscale 模組
+ 啟用範例：
```
# 啟動環境
do autoscaling
# 進入環境
do autoscaling --into
```    
+ 執行 ```iwa exec``` 來依據 default 配置擴展服務
+ 執行測試 ```bash test-docker-nginx-lb```，檢測 Nginx 負載平衡

#### Docker Swarm with Auto-Scaling: ( 待確認 )

If automatic scaling based on metrics like CPU usage or request load is required, you could consider Docker Swarm for orchestration platforms.

Docker Swarm, which integrates with Docker Compose files, offers features for service replication and can be combined with external monitoring and scaling tools to achieve a form of auto-scaling within a Swarm cluster.

## 文獻

+ Nginx LoadBalancer
  + [Using nginx as HTTP load balancer](https://nginx.org/en/docs/http/load_balancing.html)
    - [HTTP Load Balancing](https://docs.nginx.com/nginx/admin-guide/load-balancer/http-load-balancer/)
  + [淺談 Nginx 基本配置、負載均衡、緩存和反向代理](https://www.maxlist.xyz/2020/06/18/flask-nginx/)
  + [使用 Nginx 做 Load Balancer](https://blog.dtask.idv.tw/Nginx/2018-07-31/)
+ Docker auto-scaling
  - [Compose Deploy Specification](https://docs.docker.com/reference/compose-file/deploy/)
  - [Scaling in Docker Compose with hands-on Examples](https://docker77.hashnode.dev/scaling-in-docker-compose-with-hands-on-examples)
  - [Scaling Docker Compose Up](https://www.docker.com/blog/scaling-docker-compose-up/)
  - [Running auto-scalling docker services](https://www.reddit.com/r/docker/comments/102cny0/running_autoscalling_docker_services/)
    + [docker-swarm-autoscaler - Dockerhub](https://github.com/jcwimer/docker-swarm-autoscaler)
  - [Implementing Auto-Scaling for Improved Performance: A Backend Engineer's Journey](https://dev.to/jackynote/implementing-auto-scaling-for-improved-performance-a-backend-engineers-journey-43g7)
    + [Collect Docker metrics with Prometheus](https://docs.docker.com/engine/daemon/prometheus/)
    + [Docker Scout metrics exporter](https://docs.docker.com/scout/explore/metrics-exporter/)
+ [Translate a Docker Compose File to Kubernetes Resources](https://kubernetes.io/docs/tasks/configure-pod-container/translate-compose-kubernetes/)
