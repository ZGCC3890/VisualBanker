# backend/Dockerfile

# python镜像
FROM python:3.12

# 工作目录
WORKDIR /app

# 拷贝后端依赖文件
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY . /app/

# 暴露端口
EXPOSE 8000

# 启动
CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]