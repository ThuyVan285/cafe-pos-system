# ☕ Cafe POS

Phần mềm quản lý bán hàng (POS) cho quán cà phê, xây dựng bằng **Python + PyQt6**, hỗ trợ quản lý bàn, gọi món, thanh toán, thống kê doanh thu và quản lý người dùng/sản phẩm theo phân quyền.

---

## Tính năng chính

### Đăng nhập & phân quyền
- 3 vai trò: `ADMIN`, `MANAGER`, `STAFF`
- Mỗi vai trò có menu và quyền thao tác khác nhau (Admin có thêm quản lý người dùng/sản phẩm, đổi mật khẩu, xuất báo cáo...)

### Dashboard / Tổng quan
- Thẻ thống kê nhanh: doanh thu hôm nay, số đơn, bàn đang phục vụ, doanh thu đơn đang mở
- Biểu đồ doanh thu theo giờ / theo ngày / theo thứ (matplotlib)
- Biểu đồ lượng khách hàng theo thời gian
- Biểu đồ tròn (donut) hiệu quả thực đơn theo danh mục
- Bảng xếp hạng Top món bán chạy
- Feed hoạt động bán hàng gần đây (real-time-ish)

### Báo cáo
- Doanh thu hôm nay / tuần / tháng, so sánh % với kỳ trước
- Dự đoán doanh thu ngày mai (Moving Average 7 ngày)
- Biểu đồ doanh thu 7 ngày gần nhất
- Top sản phẩm theo doanh thu / số lượng (progress bar trực quan)
- Xuất báo cáo ra file CSV/Excel

### Quản lý người dùng *(Admin)*
- Thêm / sửa / xóa tài khoản nhân viên
- Phân quyền theo Role
- Tìm kiếm theo tên / username

### Quản lý sản phẩm
- Danh sách sản phẩm theo danh mục, giá, size
- Thêm / sửa / ẩn sản phẩm *(Admin)*
- Hỗ trợ sản phẩm có nhiều size và topping

### Hỗ trợ bán hàng (POS)
- Sơ đồ bàn dạng lưới, có phân trang, lọc theo trạng thái (Tất cả / Đang dùng / Trống)
- Gọi món theo danh mục, tìm kiếm món nhanh
- Giỏ hàng: tăng/giảm số lượng, ghi chú từng món, xóa món
- Chuyển bàn, gộp bàn
- Thông báo bếp / quầy pha chế
- In tạm tính, thanh toán đơn hàng
- Lịch sử ca làm việc của nhân viên

---

## Công nghệ sử dụng

| Thành phần        | Công nghệ                     |
|--------------------|--------------------------------|
| Giao diện           | PyQt6                         |
| Biểu đồ             | Matplotlib (QtAgg backend)    |
| Icon                | QtAwesome (qtawesome)         |
| ORM / Database      | SQLAlchemy                    |
| Xử lý số liệu       | NumPy                         |

---

## Cấu trúc thư mục

```
cafe_pos/
├── main.py                      # Điểm khởi chạy ứng dụng
├── config/
│   └── settings.py              # Cấu hình kết nối database, hằng số hệ thống
├── database/
│   └── db.py                    # Khởi tạo session / kết nối DB
├── models/                      # Định nghĩa entity (SQLAlchemy models)
│   ├── user.py                  # User, Role
│   ├── order.py                 # Order, OrderStatus
│   ├── table.py                 # CafeTable, TableStatus
│   ├── payment.py                # Payment
│   ├── product.py               # Product, Size...
│   └── category.py              # Category
├── repositories/                # Lớp truy vấn dữ liệu (Repository pattern)
│   ├── user_repository.py
│   ├── product_repository.py
│   └── table_repository.py
├── services/                    # Xử lý nghiệp vụ
│   ├── statistic_service.py     # Thống kê, dự đoán doanh thu
│   ├── order_service.py
│   ├── product_service.py
│   └── payment_service.py
├── controllers/                 # Điều phối giữa UI và Service
│   ├── order_controller.py
│   ├── product_controller.py
│   └── payment_controller.py
└── ui/
    ├── main_window.py           # Cửa sổ chính, điều hướng theo user đăng nhập
    ├── screens/
    │   ├── dashboard_screen.py  # Màn hình Admin/Manager: tổng quan, người dùng, sản phẩm, báo cáo
    │   └── pos_screen.py        # Màn hình bán hàng: sơ đồ bàn, gọi món, thanh toán
    └── dialogs/                 # Các hộp thoại: user_dialog, product_dialog,
                                  # payment_dialog, invoice_dialog, transfer_table_dialog, notify_dialog...
```

---

## Cài đặt

### 1. Yêu cầu
- Python 3.11+
- Hệ quản trị cơ sở dữ liệu được cấu hình trong `config/settings.py` (`DB_CONFIG`)

### 2. Clone dự án
```bash
git clone <repo-url>
cd cafe_pos
```

### 3. Tạo môi trường ảo (khuyến nghị)
```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

### 4. Cài thư viện
```bash
pip install -r requirements.txt
```
> Nếu chưa có `requirements.txt`, cài tối thiểu các gói sau:
```bash
pip install PyQt6 SQLAlchemy matplotlib numpy qtawesome
```

### 5. Cấu hình kết nối database
Mở `config/settings.py` và chỉnh `DB_CONFIG` (host, port, username, password, tên database) cho phù hợp với môi trường của bạn.

### 6. Chạy ứng dụng
```bash
python main.py
```

Lần đầu chạy, hệ thống sẽ tự khởi tạo database và tạo sẵn 3 tài khoản mẫu:

| Tài khoản | Mật khẩu     | Vai trò  |
|-----------|--------------|----------|
| admin     | admin123     | ADMIN    |
| manager   | manager123   | MANAGER  |
| staff     | staff123     | STAFF    |

>  Nên đổi mật khẩu các tài khoản mặc định trước khi đưa vào sử dụng thực tế.

---

## Ghi chú

- Ứng dụng chạy ở chế độ desktop (PyQt6), phù hợp cho máy tính quầy thu ngân tại quán.
- Các biểu đồ thống kê được vẽ bằng Matplotlib và nhúng trực tiếp vào giao diện Qt.
- Có thể mở rộng thêm các phương thức thanh toán, tích hợp máy in hóa đơn, hoặc đồng bộ dữ liệu nhiều chi nhánh.

---

## License

Dự án nội bộ — vui lòng cập nhật phần License phù hợp với nhu cầu sử dụng (MIT, riêng tư, thương mại...).
