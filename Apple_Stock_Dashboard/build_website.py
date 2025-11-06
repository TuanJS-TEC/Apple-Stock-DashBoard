import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
from wordcloud import WordCloud

def get_global_css():
    """
    Trả về một chuỗi CSS chung để nhúng vào mọi trang.
    (Nâng cấp V3: Thêm CSS cho Modal Lightbox)
    """
    return """
    <style>
        /* --- Tổng thể --- */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            margin: 0;
            background-color: #f4f7f6;
            color: #333;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }

        /* --- Thanh Điều hướng (NAV) --- */
        nav {
            background-color: #ffffff;
            padding: 15px 30px;
            border-bottom: 1px solid #ddd;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            text-align: center;
        }
        nav a {
            margin: 0 20px;
            text-decoration: none;
            font-size: 18px;
            font-weight: 500;
            color: #007bff;
            transition: color 0.2s;
        }
        nav a:hover {
            color: #0056b3;
        }
        nav a.active {
            color: #333;
            font-weight: 700;
            border-bottom: 2px solid #333;
            padding-bottom: 5px;
        }

        /* --- Tiêu đề --- */
        h1 {
            color: #222;
            border-bottom: 2px solid #007bff;
            padding-bottom: 10px;
        }
        
        /* --- Lưới chứa biểu đồ --- */
        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(600px, 1fr));
            gap: 25px;
            margin-top: 30px;
        }

        /* --- Thẻ (Card) chứa biểu đồ --- */
        .chart-card {
            background-color: #ffffff;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.08);
            padding: 25px;
            overflow: hidden;
        }
        .chart-card h2 {
            margin-top: 0;
            color: #0056b3;
            border-bottom: 1px solid #eee;
            padding-bottom: 15px;
        }
        
        /* >>> MỚI: CSS ĐỂ BIẾN BIỂU ĐỒ THÀNH NÚT BẤM <<< */
        .chart-card img,
        .chart-card iframe {
            width: 100%;
            border-radius: 5px;
            border: 1px solid #eee;
            box-sizing: border-box;
            cursor: pointer; /* Biến con trỏ thành hình bàn tay */
            transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
        }
        .chart-card img:hover,
        .chart-card iframe:hover {
            transform: scale(1.02); /* Phóng to nhẹ khi di chuột */
            box-shadow: 0 8px 16px rgba(0,0,0,0.1);
        }
        
        /* --- Phần Phân tích (Insight) --- */
        .insight {
            background-color: #e6f7ff;
            border-left: 5px solid #007bff;
            padding: 15px 20px;
            margin-top: 20px;
            margin-bottom: 20px;
            border-radius: 4px;
            font-size: 1.05em;
            line-height: 1.6;
        }
        .insight strong {
            color: #0056b3;
        }

        /* >>> MỚI: CSS CHO MODAL (LIGHTBOX) <<< */
        .modal-overlay {
            position: fixed; /* Che toàn bộ màn hình */
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.85); /* Lớp mờ màu đen */
            display: none; /* Ẩn ban đầu */
            justify-content: center;
            align-items: center;
            z-index: 1000;
        }
        .modal-overlay.visible {
            display: flex; /* Hiện khi có class 'visible' */
        }
        .modal-content {
            position: relative;
            background: #fff;
            padding: 20px;
            border-radius: 8px;
            width: 90vw; /* Rộng 90% màn hình */
            height: 90vh; /* Cao 90% màn hình */
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .modal-content iframe,
        .modal-content img {
            width: 100%;
            height: 100%;
            border: none;
            object-fit: contain; /* Hiển thị toàn bộ ảnh (cho PNG) */
        }
        .modal-close {
            position: absolute;
            top: -15px;
            right: -15px;
            width: 35px;
            height: 35px;
            line-height: 35px;
            text-align: center;
            background: #fff;
            border-radius: 50%;
            font-size: 28px;
            font-weight: bold;
            color: #333;
            cursor: pointer;
            z-index: 1001;
        }

        /* --- Responsive cho màn hình nhỏ --- */
        @media (max-width: 700px) {
            .chart-grid {
                grid-template-columns: 1fr;
            }
            nav a {
                display: block;
                margin: 10px 0;
            }
            .modal-content {
                width: 95vw;
                height: 80vh;
            }
        }
    </style>
    """

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Tạo đường dẫn đầy đủ và chính xác đến file CSV
DATA_FILE_PATH = os.path.join(BASE_DIR, 'data', 'Apple_historical_data.csv')

# --- BƯỚC 2: XỬ LÝ DỮ LIỆU VÀ LẤY API ---

def process_stock_data(filepath):
    """
    Đọc dữ liệu cổ phiếu từ file CSV, chuẩn hóa và tạo cột đặc trưng.
    (Đáp ứng Yêu cầu B)
    """
    print("Đang xử lý dữ liệu cổ phiếu...")
    try:
        df = pd.read_csv(filepath)
    except FileNotFoundError:
        print(f"Lỗi: Không tìm thấy file tại {filepath}")
        return None

    temp_date_col = pd.to_datetime(df['Date'], utc=True, errors='coerce')
    df['Date'] = temp_date_col.dt.date
    df['Date'] = pd.to_datetime(df['Date'])    

    # Xử lý thiếu (ví dụ đơn giản là xóa dòng có dữ liệu thiếu)
    df.dropna(inplace=True) 
    
    # Tạo cột đặc trưng mới
    df['Year'] = df['Date'].dt.year
    df['Month'] = df['Date'].dt.month
    df['Day'] = df['Date'].dt.day
    df['Daily_Change_Percent'] = ((df['Close'] - df['Open']) / df['Open']) * 100
    
    print("Xử lý dữ liệu cổ phiếu... Xong.")
    return df

def get_apple_news_text():
    """
    Lấy các tiêu đề tin tức mới nhất về 'Apple Inc.' từ Google News.
    (Đáp ứng Yêu cầu A: Dùng requests/BeautifulSoup)
    """
    print("Đang lấy tin tức từ Google News...")
    try:
        # Chúng ta dùng Google News làm API mở (Mô phỏng)
        url = "https://www.google.com/search?q=Apple+Inc.+stock&tbm=nws"
        # Google yêu cầu User-Agent để trông giống trình duyệt
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Báo lỗi nếu request thất bại
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Lấy tất cả các tiêu đề tin (thường trong thẻ <div> có vai trò 'heading')
        headlines = soup.find_all('div', {'role': 'heading'})
        
        if not headlines:
            print("Không tìm thấy tiêu đề tin tức (có thể cấu trúc Google đã thay đổi).")
            return "Không có tin tức"

        # Nối tất cả các tiêu đề lại thành một chuỗi văn bản lớn
        text_data = " ".join([h.get_text() for h in headlines])
        
        print(f"Lấy tin tức... Xong (Tìm thấy {len(headlines)} tiêu đề).")
        return text_data
        
    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi lấy tin tức: {e}")
        return "Không thể lấy tin tức"
    
# --- BƯỚC 3: TẠO BIỂU ĐỒ (PHIÊN BẢN NÂNG CẤP) ---

def create_visualizations(df, news_text, static_dir, interactive_dir):
    """
    Tạo tất cả các biểu đồ tĩnh (PNG) và tương tác (HTML).
    (Đáp ứng Yêu cầu C & D)
    """
    print("Đang tạo biểu đồ (phiên bản 10 biểu đồ)...")
    
    # Chuẩn bị dữ liệu cho một số biểu đồ
    df_recent = df[df['Year'] > df['Year'].max() - 15] # 15 năm gần nhất
    df_grouped = df.groupby(['Year', 'Month'])['Volume'].sum().reset_index() # Dùng cho Treemap/Sunburst
    df_sample = df.sample(min(5000, len(df))) # Dùng cho Scatter
    
    # --- 1. Biểu đồ Tĩnh (Lưu vào /charts_static/) ---
    
    # BIỂU ĐỒ 1 (Tĩnh): Histogram
    plt.figure(figsize=(10, 6))
    sns.histplot(df['Daily_Change_Percent'], bins=50, kde=True)
    plt.title('Phân phối % Thay đổi giá hàng ngày')
    plt.xlabel('% Thay đổi')
    plt.ylabel('Tần suất')
    plt.savefig(os.path.join(static_dir, 'daily_change_histogram.png'))
    plt.close()

    # BIỂU ĐỒ 2 (Tĩnh): Boxplot
    plt.figure(figsize=(12, 7))
    sns.boxplot(x='Year', y='Close', data=df_recent)
    plt.title('Boxplot giá đóng cửa (15 năm gần nhất)')
    plt.savefig(os.path.join(static_dir, 'price_boxplot_by_year.png'))
    plt.close()
    
    # BIỂU ĐỒ 3 (Tĩnh): Heatmap
    plt.figure(figsize=(8, 6))
    corr_cols = ['Open', 'High', 'Low', 'Close', 'Volume', 'Daily_Change_Percent']
    corr = df[corr_cols].corr()
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='coolwarm')
    plt.title('Heatmap tương quan')
    plt.savefig(os.path.join(static_dir, 'correlation_heatmap.png'))
    plt.close()

    # BIỂU ĐỒ 4 (Tĩnh): WordCloud
    try:
        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(news_text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('WordCloud Tin tức về Apple')
        plt.savefig(os.path.join(static_dir, 'news_wordcloud.png'))
        plt.close()
    except ValueError:
        print("Lỗi: Không thể tạo WordCloud. Bỏ qua.")

    # BIỂU ĐỒ 5 (Tĩnh - MỚI): Violin Plot
    plt.figure(figsize=(12, 7))
    sns.violinplot(x='Year', y='Daily_Change_Percent', data=df_recent)
    plt.title('Violin Plot: % Thay đổi hàng ngày (15 năm gần nhất)')
    plt.ylim(-10, 10) # Giới hạn trục Y để dễ nhìn hơn
    plt.savefig(os.path.join(static_dir, 'daily_change_violin_by_year.png'))
    plt.close()


    # --- 2. Biểu đồ Tương tác (Lưu vào /charts_interactive/) ---
    
    # BIỂU ĐỒ 6 (Tương tác): Line (Giá)
    fig_line = px.line(df, x='Date', y='Close', title='Biến động giá đóng cửa (AAPL) theo thời gian')
    fig_line.write_html(os.path.join(interactive_dir, 'price_over_time.html'))

    # BIỂU ĐỒ 7 (Tương tác): Scatter
    fig_scatter = px.scatter(df_sample, x='High', y='Low', trendline='ols', 
                             title='Scatter Plot High vs Low (có hồi quy - 5000 điểm mẫu)')
    fig_scatter.write_html(os.path.join(interactive_dir, 'scatter_regression.html'))

    # BIỂU ĐỒ 8 (Tương tác): Treemap
    fig_treemap = px.treemap(df_grouped, path=[px.Constant('Tất cả'), 'Year', 'Month'], values='Volume',
                             title='Treemap tổng khối lượng giao dịch theo Năm/Tháng')
    fig_treemap.write_html(os.path.join(interactive_dir, 'volume_treemap.html'))
    
    # BIỂU ĐỒ 9 (Tương tác - MỚI): Area (Volume)
    fig_area = px.area(df, x='Date', y='Volume', title='Biến động Khối lượng Giao dịch theo thời gian')
    fig_area.write_html(os.path.join(interactive_dir, 'volume_over_time.html'))

    # BIỂU ĐỒ 10 (Tương tác - MỚI): Sunburst
    fig_sunburst = px.sunburst(
    df_grouped,
    path=['Year', 'Month'],
    values='Volume',
    color='Year',  # tô màu theo năm để dễ phân biệt
    color_continuous_scale='Blues',  # thang màu nhẹ, dễ nhìn
    title='📊 Sunburst: Khối lượng giao dịch Apple (AAPL) theo Năm và Tháng',
)

    # --- Tùy chỉnh giao diện ---
    fig_sunburst.update_traces(
        textinfo="label+percent parent",  # chỉ hiển thị nhãn và phần trăm trong năm
        insidetextorientation='radial',
        hovertemplate="<b>%{label}</b><br>Volume: %{value:,}<extra></extra>",  # định dạng số dễ đọc
    )

    fig_sunburst.update_layout(
        title_font_size=20,
        uniformtext=dict(minsize=10, mode='hide'),
        margin=dict(t=80, l=0, r=0, b=0),
        height=700,
        coloraxis_showscale=False,  # ẩn thanh màu
        paper_bgcolor="white",
        font=dict(family="Arial", size=13)
    )

    # Ghi ra file HTML
    fig_sunburst.write_html(os.path.join(interactive_dir, 'volume_sunburst.html'))
    print("✅ Biểu đồ Sunburst (nâng cấp) đã được tạo!")
        
    print("Tạo biểu đồ... Xong (10 biểu đồ).")

# --- BƯỚC 4: TẠO CÁC TRANG WEB HTML ---

def get_navigation_menu(current_page=""):
    """Tạo một menu điều hướng (navbar) sử dụng class CSS. (V4: Thêm Storytelling)"""
    pages = {
        "index.html": "Trang chủ (Tổng quan)",
        "1_timeseries.html": "Phân tích Thời gian",
        "2_distributions.html": "Phân tích Phân phối",
        "3_relationships.html": "Phân tích Quan hệ",
        "4_storytelling.html": "Câu chuyện Dữ liệu" # <-- TRANG MỚI
    }
    
    menu_html = '<nav>'
    for page_file, page_title in pages.items():
        # Thêm class 'active' nếu là trang hiện tại
        active_class = 'active' if page_file == current_page else ''
        menu_html += f'<a href="{page_file}" class="{active_class}">{page_title}</a>'
        
    menu_html += '</nav>'
    return menu_html


# --- BƯỚC 4: TẠO CÁC TRANG WEB HTML (PHIÊN BẢN NÂNG CẤP) ---
def create_html_pages(base_dir, static_dir_name, interactive_dir_name):
    """
    Tạo tất cả các file HTML cho website (phiên bản nâng cấp V4 - Thêm Storytelling).
    """
    print("Đang tạo các trang web HTML (phiên bản nâng cấp V4)...")
    
    global_css = get_global_css()
    
    # --- MỚI: Cấu trúc HTML và JS cho Modal (Giữ nguyên từ bước trước) ---
    modal_html_and_js = """
        <div class="modal-overlay" id="chartModal">
            <span class="modal-close" id="modalCloseButton">&times;</span>
            <div class="modal-content" id="modalContent">
                </div>
        </div>
        <script>
            document.addEventListener('DOMContentLoaded', () => {
                const modal = document.getElementById('chartModal');
                const modalContent = document.getElementById('modalContent');
                const closeModal = document.getElementById('modalCloseButton');
                const charts = document.querySelectorAll('.chart-card img, .chart-card iframe');
                charts.forEach(chart => {
                    chart.addEventListener('click', (e) => {
                        e.preventDefault(); 
                        modalContent.innerHTML = '';
                        let newElement;
                        if (chart.tagName === 'IMG') {
                            newElement = document.createElement('img');
                            newElement.src = chart.src;
                        } else if (chart.tagName === 'IFRAME') {
                            newElement = document.createElement('iframe');
                            newElement.src = chart.src;
                            newElement.setAttribute('frameborder', '0');
                        }
                        if (newElement) {
                            modalContent.appendChild(newElement);
                            modal.classList.add('visible');
                        }
                    });
                });
                const closeTheModal = () => {
                    modal.classList.remove('visible');
                    modalContent.innerHTML = '';
                };
                closeModal.addEventListener('click', closeTheModal);
                modal.addEventListener('click', (e) => {
                    if (e.target === modal) {
                        closeTheModal();
                    }
                });
            });
        </script>
    """

    # --- index.html (Trang chủ) ---
    # (Giữ nguyên code tạo trang index.html)
    html_index = f"""
    <html>
        <head>
            <title>Trang chủ - Dashboard Cổ phiếu Apple</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {global_css}
        </head>
        <body>
            {get_navigation_menu("index.html")}
            <div class="container">
                <h1>Trang chủ: Tổng quan Tin tức & Tương quan</h1>
                <p>Tổng hợp các tin tức và mối tương quan của cổ phiếu Apple (AAPL). (Click vào biểu đồ để xem toàn màn hình)</p>
                <div class="chart-grid">
                    <div class="chart-card">
                        <h2>WordCloud Tin tức</h2>
                        <p class="insight"><strong>Insight:</strong> Các từ khóa nổi bật trong tin tức gần đây.</p>
                        <img src="{static_dir_name}/news_wordcloud.png" alt="WordCloud Tin tức">
                    </div>
                    <div class="chart-card">
                        <h2>Heatmap Tương quan</h2>
                        <p class="insight"><strong>Insight:</strong> 'Open', 'High', 'Low', 'Close' tương quan 1:1. Mối quan hệ giữa 'Volume' và 'Daily_Change' không rõ rệt.</p>
                        <img src="{static_dir_name}/correlation_heatmap.png" alt="Heatmap Tương quan">
                    </div>
                </div>
            </div>
            {modal_html_and_js}
        </body>
    </html>
    """
    with open(os.path.join(base_dir, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(html_index)

    # --- 1_timeseries.html (Trang thời gian) ---
    # (Giữ nguyên code tạo trang 1_timeseries.html)
    html_page1 = f"""
    <html>
        <head>
            <title>Phân tích Thời gian</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {global_css}
        </head>
        <body>
            {get_navigation_menu("1_timeseries.html")}
            <div class="container">
                <h1>Phân tích Biến động theo Thời gian (Tương tác)</h1>
                <p>Click vào biểu đồ để mở chế độ xem lớn (vẫn giữ nguyên tương tác).</p>
                <div class="chart-grid">
                    <div class="chart-card">
                        <h2>Biểu đồ Đường: Giá Đóng cửa</h2>
                        <p class="insight"><strong>Insight:</strong> Cho thấy sự tăng trưởng dài hạn. Bạn có thể zoom vào để xem các đợt khủng hoảng và phục hồi.</p>
                        <iframe src="{interactive_dir_name}/price_over_time.html" height="500" title="Biểu đồ đường giá đóng cửa"></iframe>
                    </div>
                    <div class="chart-card">
                        <h2>Biểu đồ Vùng: Khối lượng Giao dịch (MỚI)</h2>
                        <p class="insight"><strong>Insight:</strong> Những đỉnh khối lượng đột biến thường xảy ra khi có tin tức lớn (báo cáo tài chính, ra mắt sản phẩm).</p>
                        <iframe src="{interactive_dir_name}/volume_over_time.html" height="500" title="Biểu đồ vùng khối lượng giao dịch"></iframe>
                    </div>
                </div>
            </div>
            {modal_html_and_js}
        </body>
    </html>
    """
    with open(os.path.join(base_dir, '1_timeseries.html'), 'w', encoding='utf-8') as f:
        f.write(html_page1)

    # --- 2_distributions.html (Trang phân phối) ---
    # (Giữ nguyên code tạo trang 2_distributions.html)
    html_page2 = f"""
    <html>
        <head>
            <title>Phân tích Phân phối & Rủi ro</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {global_css}
        </head>
        <body>
            {get_navigation_menu("2_distributions.html")}
            <div class="container">
                <h1>Phân tích Phân phối & Rủi ro (Tĩnh)</h1>
                <p>Click vào biểu đồ để phóng to và xem chi tiết hơn.</p>
                <div class="chart-grid">
                    <div class="chart-card">
                        <h2>Histogram % Thay đổi hàng ngày</h2>
                        <p class="insight"><strong>Insight:</strong> Hầu hết các ngày, giá chỉ thay đổi nhẹ (quanh 0%). Các "đuôi" (tails) ở 2 bên thể hiện rủi ro "sự kiện bất ngờ".</p>
                        <img src="{static_dir_name}/daily_change_histogram.png" alt="Histogram % Thay đổi hàng ngày">
                    </div>
                    <div class="chart-card">
                        <h2>Boxplot Giá đóng cửa (15 năm gần nhất)</h2>
                        <p class="insight"><strong>Insight:</strong> Cho thấy xu hướng tăng giá (hộp đi lên) và mức độ biến động (hộp càng dài, biến động càng lớn) qua từng năm.</p>
                        <img src="{static_dir_name}/price_boxplot_by_year.png" alt="Boxplot Giá đóng cửa">
                    </div>
                    <div class="chart-card">
                        <h2>Violin Plot: % Thay đổi hàng ngày (MỚI)</h2>
                        <p class="insight"><strong>Insight:</strong> Kết hợp Histogram và Boxplot. Phần "thân đàn" phình to cho thấy dữ liệu tập trung (quanh 0%) ở các năm.</p>
                        <img src="{static_dir_name}/daily_change_violin_by_year.png" alt="Violin Plot % Thay đổi hàng ngày">
                    </div>
                </div>
            </div>
            {modal_html_and_js}
        </body>
    </html>
    """
    with open(os.path.join(base_dir, '2_distributions.html'), 'w', encoding='utf-8') as f:
        f.write(html_page2)
    
    # --- 3_relationships.html (Trang quan hệ) ---
    # (Giữ nguyên code tạo trang 3_relationships.html)
    html_page3 = f"""
    <html>
        <head>
            <title>Phân tích Mối quan hệ & Phân cấp</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {global_css}
        </head>
        <body>
            {get_navigation_menu("3_relationships.html")}
            <div class="container">
                <h1>Phân tích Mối quan hệ & Phân cấp (Tương tác)</h1>
                <p>Click vào biểu đồ để mở chế độ xem lớn (vẫn giữ nguyên tương tác).</p>
                <div class="chart-grid">
                    <div class="chart-card">
                        <h2>Scatter Plot High vs Low (Tương tác)</h2>
                        <p class="insight"><strong>Insight:</strong> Các điểm tập trung dày đặc quanh đường chéo cho thấy mối tương quan 1:1, thể hiện tính nhất quán của dữ liệu.</p>
                        <iframe src="{interactive_dir_name}/scatter_regression.html" height="500" title="Scatter Plot High vs Low"></iframe>
                    </div>
                    <div class="chart-card">
                        <h2>Treemap Khối lượng Giao dịch (Tương tác)</h2>
                        <p class="insight"><strong>Insight:</strong> Nhấp vào một năm (ví dụ: 2020) để "zoom" vào và xem tháng nào trong năm đó có giao dịch sôi động nhất.</p>
                        <iframe src="{interactive_dir_name}/volume_treemap.html" height="700" title="Treemap Khối lượng Giao dịch"></iframe>
                    </div>
                    <div class="chart-card">
                        <h2>Sunburst Khối lượng Giao dịch (MỚI - Tương tác)</h2>
                        <p class="insight"><strong>Insight:</strong> Tương tự Treemap nhưng ở dạng hình tròn. Vòng trong là Năm, vòng ngoài là Tháng. Giúp so sánh trực quan các tháng.</p>
                        <iframe src="{interactive_dir_name}/volume_sunburst.html" height="700" title="Sunburst Khối lượng Giao dịch"></iframe>
                    </div>
                </div>
            </div>
            {modal_html_and_js}
        </body>
    </html>
    """
    with open(os.path.join(base_dir, '3_relationships.html'), 'w', encoding='utf-8') as f:
        f.write(html_page3)
        
    # --- MỚI: 4_storytelling.html (Trang kể chuyện) ---
    # Chúng ta sẽ viết một bài phân tích dài, sử dụng lại các biểu đồ đã tạo
    
    html_page4 = f"""
    <html>
        <head>
            <title>Câu chuyện Dữ liệu Apple</title>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            {global_css}
            <style>
                .story-container {{
                    max-width: 900px; /* Giới hạn chiều rộng để dễ đọc */
                    margin: 20px auto;
                    line-height: 1.7;
                    font-size: 1.1em;
                }}
                .story-container h2 {{
                    color: #0056b3;
                    border-bottom: 2px solid #007bff;
                    padding-bottom: 10px;
                    margin-top: 40px;
                }}
                .story-container .chart-card {{
                    margin-top: 20px;
                    margin-bottom: 30px;
                }}
                .story-container .insight {{
                    font-size: 1.1em;
                    line-height: 1.6;
                }}
            </style>
        </head>
        <body>
            {get_navigation_menu("4_storytelling.html")}
            
            <div class="container story-container">
                <h1>Câu chuyện của Apple qua 45 năm Dữ liệu</h1>
                <p>Dữ liệu không chỉ là những con số. Đó là những câu chuyện. Bằng cách nhìn vào lịch sử giá cổ phiếu Apple (AAPL) từ 1980 đến 2025,
                chúng ta có thể thấy được một trong những hành trình kinh doanh đáng kinh ngạc nhất lịch sử.</p>

                <h2>Chương 1: Sự Khởi đầu Khiêm tốn và Sự Sống còn</h2>
                <p>Nhìn vào biểu đồ giá dài hạn, chúng ta thấy một đường gần như bằng phẳng kéo dài suốt 20 năm đầu tiên (1980-2000). 
                Đây là thời kỳ Apple chỉ là một công ty máy tính thích hợp (niche), chật vật cạnh tranh và thậm chí suýt phá sản.</p>
                <p>Giá cổ phiếu (đã điều chỉnh) gần như bằng 0. Nếu bạn zoom vào, bạn sẽ thấy sự biến động, nhưng trên bức tranh toàn cảnh, 
                đó chỉ là một đường thẳng. Đó là câu chuyện về sự sống còn.</p>
                
                <div class="chart-card">
                    <h3>Biểu đồ Đường: Giá Đóng cửa (1980 - 2025)</h3>
                    <p class="insight">
                        <strong>Insight:</strong> Toàn bộ sự tăng trưởng dường như chỉ xảy ra sau năm 2005. 
                        Điều này cho thấy tầm quan trọng của việc "tái phát minh" công ty. 
                        Bạn có thể click vào biểu đồ và dùng công cụ zoom để xem kỹ 20 năm đầu tiên.
                    </p>
                    <iframe src="{interactive_dir_name}/price_over_time.html" height="500" title="Biểu đồ đường giá đóng cửa"></iframe>
                </div>

                <h2>Chương 2: Cuộc Cách mạng iPhone (2007)</h2>
                <p>Một điều gì đó đã thay đổi rõ rệt vào khoảng năm 2007. Đó chính là iPhone. 
                Đây không chỉ là một sản phẩm mới; đó là một "điểm uốn" (inflection point) đã thay đổi quỹ đạo của công ty mãi mãi.
                Từ thời điểm đó, đường giá bắt đầu một quỹ đạo gần như thẳng đứng.</p>
                
                <p>Nhưng không chỉ giá cả. Hãy nhìn vào khối lượng giao dịch. Sự quan tâm (và tiền bạc) của thị trường 
                đổ vào Apple tăng vọt. Những "ngọn núi" về khối lượng giao dịch đột nhiên xuất hiện, thường trùng với các sự kiện ra mắt sản phẩm 
                hoặc báo cáo tài chính quan trọng.</p>
                
                <div class="chart-card">
                    <h3>Biểu đồ Vùng: Khối lượng Giao dịch</h3>
                    <p class="insight">
                        <strong>Insight:</strong> Khối lượng giao dịch (sự quan tâm) bùng nổ sau kỷ nguyên iPhone. 
                        Những đợt tăng đột biến khổng lồ (như giai đoạn 2008, 2020) cho thấy những thời điểm thị trường 
                        vừa phấn khích vừa hoảng sợ, nhưng luôn tập trung vào Apple.
                    </p>
                    <iframe src="{interactive_dir_name}/volume_over_time.html" height="500" title="Biểu đồ vùng khối lượng giao dịch"></iframe>
                </div>

                <h2>Chương 3: Tính cách của một Gã khổng lồ</h2>
                <p>Khi đã trở thành công ty lớn nhất thế giới, Apple có còn rủi ro không? Biểu đồ Histogram về % thay đổi hàng ngày cho chúng ta câu trả lời.</p>
                <p>Hầu hết các ngày (phần đỉnh nhọn ở giữa), cổ phiếu Apple rất "buồn tẻ", chỉ di chuyển nhẹ quanh 0%. 
                Đây là đặc điểm của một cổ phiếu vốn hóa lớn, ổn định. 
                Nhưng... hãy nhìn vào hai "cái đuôi" (tails) ở hai bên. Luôn có những ngày hiếm hoi mà cổ phiếu 
                tăng hoặc giảm cực mạnh (5-10%).</p>
                
                <div class="chart-card">
                    <h3>Histogram % Thay đổi hàng ngày</h3>
                    <p class="insight">
                        <strong>Insight:</strong> Apple là một cổ phiếu <strong>ổn định nhưng không nhàm chán</strong>. 
                        Nó ổn định 95% thời gian, nhưng 5% còn lại là những biến động cực lớn. 
                        Đây là rủi ro và cũng là cơ hội mà dữ liệu cảnh báo.
                    </p>
                    <img src="{static_dir_name}/daily_change_histogram.png" alt="Histogram % Thay đổi hàng ngày">
                </div>
                
                <h2>Chương 4: Thị trường đang Nghĩ gì?</h2>
                <p>Cuối cùng, chúng ta có thể kết hợp dữ liệu để hiểu "tâm lý thị trường". 
                Biểu đồ Treemap cho thấy những năm và tháng nào "nóng" nhất về giao dịch (các ô càng lớn, khối lượng càng nhiều). 
                Thường thì đó là các tháng cuối năm (mùa lễ hội, ra mắt sản phẩm) hoặc các giai đoạn khủng hoảng (như đầu năm 2020).</p>
                
                <p>Khi kết hợp với WordCloud (lấy từ tin tức), chúng ta thấy thị trường đang tập trung vào đâu. 
                Những từ như "iPhone", "Pro", "Doanh thu" (Revenue) luôn là trung tâm. Câu chuyện của Apple luôn xoay quanh 
                sự đổi mới sản phẩm và kết quả tài chính.</p>

                <div class="chart-grid">
                    <div class="chart-card">
                        <h2>Treemap Khối lượng Giao dịch</h2>
                        <p class="insight">Click vào các năm để xem tháng nào sôi động nhất.</p>
                        <iframe src="{interactive_dir_name}/volume_treemap.html" height="500" title="Treemap Khối lượng Giao dịch"></iframe>
                    </div>
                    <div class="chart-card">
                        <h2>WordCloud Tin tức</h2>
                        <p class="insight">Thị trường luôn tập trung vào sản phẩm và lợi nhuận.</p>
                        <img src="{static_dir_name}/news_wordcloud.png" alt="WordCloud Tin tức">
                    </div>
                </div>

                <h2>Kết luận</h2>
                <p>Câu chuyện của Apple, được kể qua dữ liệu, là một câu chuyện về sự kiên nhẫn và sự bùng nổ. 
                Hơn 20 năm đầu kiên trì gần như vô hình, theo sau là 20 năm tăng trưởng phi mã được thúc đẩy 
                bởi sự đổi mới mang tính cách mạng (iPhone). Dữ liệu cho thấy rõ ràng Apple đã biến mình 
                từ một công ty máy tính thích hợp thành một gã khổng lồ về công nghệ tiêu dùng, và thị trường 
                đã phản ứng lại bằng sự quan tâm và giá trị bùng nổ.</p>

            </div>
            {modal_html_and_js}
        </body>
    </html>
    """
    with open(os.path.join(base_dir, '4_storytelling.html'), 'w', encoding='utf-8') as f:
        f.write(html_page4)
    
    print("Tạo các trang web HTML... Xong (phiên bản V4 - có Storytelling).")

# --- PHẦN ĐỂ CHẠY THỬ NGHIỆM (Sẽ thêm hàm main() sau) ---
if __name__ == "__main__":
    # --- Thiết lập Đường dẫn ---
    # BASE_DIR là thư mục chứa file build_website.py
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    # Đường dẫn tuyệt đối (cho Python sử dụng)
    DATA_FILE_PATH = os.path.join(BASE_DIR, 'data', 'Apple_historical_data.csv')
    STATIC_DIR_PATH = os.path.join(BASE_DIR, 'charts_static')
    INTERACTIVE_DIR_PATH = os.path.join(BASE_DIR, 'charts_interactive')

    # Tên thư mục tương đối (cho HTML sử dụng)
    # HTML <img src="charts_static/file.png">
    STATIC_DIR_NAME = 'charts_static'
    INTERACTIVE_DIR_NAME = 'charts_interactive'

    # Đảm bảo các thư mục con tồn tại
    os.makedirs(STATIC_DIR_PATH, exist_ok=True)
    os.makedirs(INTERACTIVE_DIR_PATH, exist_ok=True)


    # --- BƯỚC 2 (Thực thi) ---
    print("--- BƯỚC 2: XỬ LÝ DỮ LIỆU ---")
    df = process_stock_data(DATA_FILE_PATH)
    news_text = get_apple_news_text()
    print("-" * 30 + "\n")

    if df is not None:
        # --- BƯỚC 3 (Thực thi) ---
        print("--- BƯỚC 3: TẠO BIỂU ĐỒ ---")
        create_visualizations(df, news_text, STATIC_DIR_PATH, INTERACTIVE_DIR_PATH)
        print("-" * 30 + "\n")

        # --- BƯỚC 4 (Thực thi) ---
        print("--- BƯỚC 4: TẠO WEBSITE ---")
        create_html_pages(BASE_DIR, STATIC_DIR_NAME, INTERACTIVE_DIR_NAME)
        print("-" * 30 + "\n")

        print("\n=== HOÀN TẤT DỰ ÁN! ===")
        print(f"Mở file sau trong trình duyệt để xem website của bạn:")
        print(f"file://{os.path.join(BASE_DIR, 'index.html')}")
    else:
        print("Dừng chương trình vì không thể xử lý dữ liệu.")