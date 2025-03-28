# 银行家算法可视化 Banker algorithm visualization
项目 Demo: [zgcc.online/zgcc](http://zgcc.online/zgcc)

## 目录
- [架构](#架构)
- [安装与运行](#安装与运行)
- [主要功能](#主要功能)
- [前端实现](#前端实现)
- [后端实现](#后端实现)
- [使用方法](#使用方法)
- [接口说明](#接口说明)
- [补充说明](#补充说明)
- [附录](#附录)

## 架构
本项目由 Docker 完全容器化管理，共用数据库 PostgreSQL 容器，前端 Vue3 和后端 Django 使用不同容器开发，流量由 Nginx 容器统一代理dev_network容器网络。各容器通过 docker-compose 编排，基本结构如下：

- **db**: PostgreSQL 容器 (共享数据库)
- **backend_dev1**: Django 后端容器
- **frontend_dev1**: Vue3 前端容器
- **nginx**: 统一的 Nginx 代理容器

## 安装与运行
1. **克隆项目**  
   ```bash
   git clone https://github.com/ZGCC3890/VisualBanker.git
   ```

2. **准备环境**  
   - 安装 Docker 与 docker-compose
   - 确保 80/443 端口空闲

3. **启动容器**  
   在项目根目录下执行:
   ```bash
   docker-compose up -d
   ```
   这会拉取/构建必要的镜像，并启动所有容器。

4. **访问前端**  
   - 浏览器访问 `http://<服务器IP>` 或 [http://localhost](http://localhost) 即可通过 Nginx 查看前端页面
   - 项目 Demo 地址: [zgcc.online/zgcc](http://zgcc.online/zgcc)

## 主要功能
- 一键模拟银行家算法的资源分配场景
- 实时生成每个“客户(进程)”的 Max、Allocation、Need 等矩阵
- 自动检测系统是否安全，并输出安全序列
- 若有多条安全序列，可查看并对比资源利用率，展示最优序列
- 从多个背景图片中随机选取一个充满页面背景

## 前端实现
- 使用 **Vue3** 编写，核心页面在 `VisualBanker/frontend/src/components/Banker.vue` 组件中。
- 通过输入客户数 n、资源种类 m 后点击“运行算法”按钮触发请求。
- 接口调用封装在 `VisualBanker/frontend/src/api/banker.js` 中，向后端发送 POST 请求。
- 接收到后端返回的数据后，进行表格和列表渲染，包括:  
  `total_resources / available`  
  `max_resources / allocation / need`  
  `execute_time`(执行所需时间)  
  安全检查结果 (安全 或 不安全)  
  安全序列 (one_safe_sequence, all_safe_sequences, best_sequence)  

## 后端实现
- 使用 **Django** 开发，主要逻辑在 `banker_algorithm` 视图函数中：
  **随机生成**各个进程的最大需求 Max、资源占用时间 `execute_time`
  **设置总资源量** `total_resources`
  **随机分配**已占用资源 `allocation` 并计算当前 `available`
  **检查安全性**首先通过 `is_safe_once()` 方法进行初步安全状态判定；若安全则继续回溯搜索所有安全序列
  **计算资源利用率**并选出最优序列
- 最终通过 JSON 格式返回数据给前端，供可视化渲染。

## 使用方法
1. **进入前端页面**  
   根据前端项目启动后返回的地址，或者直接访问 Nginx 暴露的 80 端口。

2. **输入参数**  
   在页面输入“客户数 (n)”和“资源种类 (m)”后点击“运行算法”，默认`n = 5` `m = 3`。

3. **查看结果**  
   - 若系统处于安全状态，会显示安全序列、最优序列以及前 10 条“资源利用率”最高的序列。
   - 若系统不安全，则会有红字提示。
   ```
   资源利用率 = max[(1 - 当前剩余资源量 / 总资源量) * 100%]
   ```

## 接口说明
- **URL**: `/api/banker` (示例，实际请以路由配置为准)
- **请求方法**: `POST`
- **请求体**: 
  ```json
  {
    "n": 5,  // 客户数
    "m": 3   // 资源种类数
  }
  ```
- **返回示例**:
  ```json
  {
    "total_resources": [10, 18, 22],
    "max_resources": [[2,3,5], [4,1,3], ...],
    "allocation": [[0,1,3], [2,0,2], ...],
    "need": [[2,2,2], [2,1,1], ...],
    "available": [5, 10, 8],
    "execute_time": [4, 6, 2, 7, 5],
    "safe": true,
    "one_safe_sequence": [1, 0, 2, 4, 3],
    "all_safe_sequences": [[...], [...], ...],
    "best_sequence": [...]
  }
  ```

## 补充说明
- 如果需要自定义数据库配置，请在 `docker-compose.yml` 中修改 `POSTGRES_USER`, `POSTGRES_PASSWORD`, `DB_HOST` 等环境变量。
- 若要自定义 Nginx 配置，可修改项目内的 `nginx.conf` 并重新构建容器。
- 部署至服务器后，请根据实际 IP/域名访问；并在域名解析或安全组等配置上开放对应端口。

## 附录
### nginx/nginx.conf
```
events {
    worker_connections 1024;
}

http {
    server {
        listen 80;
        server_name zgcc.online;

        # 开发者 1 的前端
        location /zgcc/ {
            rewrite ^/zgcc/(.*)$ /$1 break;
            proxy_pass http://vue_frontend_zgcc:80; 
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 开发者 1 的后端（通过 Docker 网络访问）
        location /zgcc/api/ {
            rewrite ^/zgcc/api(/.*)$ $1 break;
            proxy_pass http://django_backend_zgcc:8000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # # 开发者 2 的前端
        # location /bjx/ {
        #     rewrite ^/bjx/(.*)$ /$1 break;
        #     proxy_pass http://vue_frontend_bjx:80; 
        #     proxy_set_header Host $host;
        #     proxy_set_header X-Real-IP $remote_addr;
        #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        #     proxy_set_header X-Forwarded-Proto $scheme;
        # }

        # # 开发者 2 的后端（通过 Docker 网络访问）
        # location /bjx/api/ {
        #     rewrite ^/bjx/api(/.*)$ $1 break;
        #     proxy_pass http://django_backend_bjx:8000/;
        #     proxy_set_header Host $host;
        #     proxy_set_header X-Real-IP $remote_addr;
        #     proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        #     proxy_set_header X-Forwarded-Proto $scheme;
        # }
    }
}
```
### nginx/docker-compose.yml
```
services:
  nginx:
    image: nginx:latest
    container_name: nginx_proxy
    restart: always
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    networks:
      - dev_network

networks:
  dev_network:
    external: true
```