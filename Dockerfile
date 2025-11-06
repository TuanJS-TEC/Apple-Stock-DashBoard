# --- GIAI ĐOẠN 1: "BUILDER" ---
# Giai đoạn này dùng Python để chạy script và TẠO RA các file website
FROM python:3.11-slim as builder

# Đặt thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Sao chép toàn bộ mã nguồn VÀ dữ liệu vào container
# (Dockerfile này sẽ copy chính nó, build_website.py, data/, v.v.)
COPY . .

# Chạy script để xây dựng website
# Lệnh này sẽ tạo ra các file: index.html, *.html, charts_static/, charts_interactive/
RUN python build_website.py

# --- GIAI ĐOẠN 2: "FINAL" ---
# Giai đoạn này dùng Nginx để PHỤC VỤ các file đã được tạo ở Giai đoạn 1
FROM nginx:alpine

# Đặt thư mục làm việc
WORKDIR /usr/share/nginx/html

# Xóa file index.html mặc định
RUN rm index.html

# Sao chép các file website ĐÃ ĐƯỢC TẠO từ Giai đoạn 1 (builder)
# vào thư mục web server của Nginx
COPY --from=builder /app/*.html .
COPY --from=builder /app/charts_static ./charts_static
COPY --from=builder /app/charts_interactive ./charts_interactive

# Mở cổng 80
EXPOSE 80