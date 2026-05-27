# FILE: seed_fake_orders.py
"""
Tạo dữ liệu giả thực tế từ 12/2025 → hiện tại
Chạy: python seed_fake_orders.py
"""

import random
import hashlib
from datetime import datetime, timedelta, date

# ── Setup path ────────────────────────────────────────────────
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_session
from database.init_db import init_database
from models.order import Order, OrderStatus
from models.order_item import OrderItem
from models.payment import Payment, PaymentMethod
from models.table import CafeTable, TableStatus
from models.product import Product, ProductSize
from models.user import User, Role

# ─────────────────────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────────────────────
START_DATE = date(2025, 12, 1)
END_DATE   = date.today()

random.seed(42)

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def weighted_choice(choices: list, weights: list):
    total = sum(weights)
    r = random.uniform(0, total)
    acc = 0
    for c, w in zip(choices, weights):
        acc += w
        if r <= acc:
            return c
    return choices[-1]


def get_hour_for_session(session_type: str) -> int:
    """Trả về giờ thực tế theo khung giờ cao điểm."""
    if session_type == "morning":
        # Sáng sớm 6-11h, đỉnh 7-9h
        return weighted_choice(
            [6, 7, 8, 9, 10, 11],
            [5, 20, 30, 25, 15, 5]
        )
    elif session_type == "afternoon":
        # Chiều 12-16h
        return weighted_choice(
            [12, 13, 14, 15, 16],
            [15, 25, 30, 20, 10]
        )
    else:  # evening
        # Tối 17-22h, đỉnh 18-20h
        return weighted_choice(
            [17, 18, 19, 20, 21, 22],
            [10, 25, 30, 20, 10, 5]
        )


def get_num_orders_for_day(d: date) -> int:
    """Số đơn trong ngày — cuối tuần nhiều hơn."""
    weekday = d.weekday()  # 0=Mon, 6=Sun
    is_weekend = weekday >= 5

    # Base orders
    if is_weekend:
        base = random.randint(35, 60)
    else:
        base = random.randint(20, 40)

    # Tháng 12 + tháng 1 (lễ Tết) tăng
    if d.month in [12, 1, 2]:
        base = int(base * 1.3)

    return base


def get_products_by_session(session_type: str, products_by_cat: dict) -> list:
    """
    Trả về danh sách sản phẩm phù hợp khung giờ.
    Sáng: cafe nhiều | Chiều: trà, nước giải khát | Tối: trà sữa, sinh tố
    """
    if session_type == "morning":
        weights = {
            "Cà phê":         40,
            "Latte và Sữa":   20,
            "Nước giải khát": 10,
            "Trà":            10,
            "Trà sữa":         5,
            "Nước ép":         8,
            "Sữa chua":        4,
            "Sinh tố":         3,
        }
    elif session_type == "afternoon":
        weights = {
            "Cà phê":         15,
            "Latte và Sữa":   15,
            "Nước giải khát": 20,
            "Trà":            20,
            "Trà sữa":        10,
            "Nước ép":        12,
            "Sữa chua":        5,
            "Sinh tố":         3,
        }
    else:  # evening
        weights = {
            "Cà phê":         10,
            "Latte và Sữa":   15,
            "Nước giải khát":  8,
            "Trà":            12,
            "Trà sữa":        30,
            "Nước ép":         5,
            "Sữa chua":       10,
            "Sinh tố":        10,
        }

    # Bestsellers: Cà Phê Phin Sữa, Trà Sữa Thái Xanh, Matcha Latte
    # sẽ được boost thêm ở chỗ chọn sản phẩm

    selected_cats = weighted_choice(
        list(weights.keys()),
        list(weights.values())
    )
    prods = products_by_cat.get(selected_cats, [])
    if not prods:
        # fallback
        all_prods = []
        for v in products_by_cat.values():
            all_prods.extend(v)
        return all_prods
    return prods


def pick_product(products: list, bestseller_ids: set) -> Product:
    """Chọn sản phẩm, bestseller có xác suất cao hơn."""
    weights = []
    for p in products:
        if p.id in bestseller_ids:
            weights.append(4)   # bestseller 4x
        else:
            weights.append(1)
    return weighted_choice(products, weights)


def get_size_for_product(product: Product, session: str) -> tuple[str, int]:
    """Trả về (size_name, extra_price) hoặc ('', 0)."""
    if not product.has_size or not product.sizes:
        return "", 0

    # Tối: khách thích size L hơn
    if session == "evening":
        size_weights = {"S": 10, "M": 40, "L": 50}
    else:
        size_weights = {"S": 15, "M": 50, "L": 35}

    valid_sizes = {s.size: s for s in product.sizes}
    choices = [s for s in ["S", "M", "L"] if s in valid_sizes]
    w = [size_weights.get(s, 30) for s in choices]

    chosen = weighted_choice(choices, w)
    size_obj = valid_sizes[chosen]
    return chosen, size_obj.price_delta


def get_payment_method(total: int) -> PaymentMethod:
    """Phương thức thanh toán theo giá trị đơn."""
    if total > 200_000:
        # Bill lớn: chuyển khoản nhiều hơn
        return weighted_choice(
            [PaymentMethod.CASH, PaymentMethod.BANKING, PaymentMethod.CARD],
            [30, 55, 15]
        )
    else:
        return weighted_choice(
            [PaymentMethod.CASH, PaymentMethod.BANKING, PaymentMethod.CARD],
            [55, 35, 10]
        )


# ─────────────────────────────────────────────────────────────
# MAIN SEED
# ─────────────────────────────────────────────────────────────
def seed():
    print("=" * 50)
    print("  SEED FAKE ORDERS")
    print(f"  {START_DATE} → {END_DATE}")
    print("=" * 50)

    init_database()
    session = get_session()

    try:
        # ── Kiểm tra xóa data cũ ──────────────────────────────
        existing = session.query(Payment).count()
        if existing > 0:
            confirm = input(
                f"\n⚠  Đã có {existing} payments. Xóa và tạo lại? (y/N): "
            ).strip().lower()
            if confirm != 'y':
                print("Hủy. Không thay đổi dữ liệu.")
                return

            print("Đang xóa data cũ...")
            from models.order_item import OrderItemTopping
            session.query(OrderItemTopping).delete()
            session.query(OrderItem).delete()
            session.query(Payment).delete()
            session.query(Order).delete()
            # Reset bàn về empty
            session.query(CafeTable).update({CafeTable.status: TableStatus.EMPTY})
            session.commit()
            print("✅ Đã xóa data cũ.\n")

        # ── Load data cần thiết ───────────────────────────────
        tables  = session.query(CafeTable).all()
        users   = session.query(User).filter(User.is_active == True).all()
        products = session.query(Product).filter(Product.is_active == True).all()

        if not tables or not users or not products:
            print("❌ Thiếu dữ liệu bàn/user/product. Chạy init_database trước.")
            return

        # Staff users (ưu tiên)
        staff_users = [u for u in users if u.role == Role.STAFF]
        if not staff_users:
            staff_users = users  # fallback

        # Nhóm sản phẩm theo category
        products_by_cat: dict[str, list] = {}
        for p in products:
            cat_name = p.category.name if p.category else "Khác"
            products_by_cat.setdefault(cat_name, []).append(p)

        # Bestsellers (sẽ được chọn nhiều hơn)
        bestseller_names = {
            "Cà Phê Phin Sữa", "Cà Phê Phin Đen", "Cà Phê Máy Đen",
            "Trà Sữa Thái Xanh Full Topping", "Trà Sữa Khoai Môn",
            "Matcha Latte", "Cacao Latte",
            "Sinh Tố Bơ", "Sữa Chua Đào",
            "Bò Húc", "Coca-Cola",
        }
        bestseller_ids = {p.id for p in products if p.name in bestseller_names}

        print(f"📦 Products: {len(products)}")
        print(f"🪑 Tables:   {len(tables)}")
        print(f"👤 Staff:    {len(staff_users)}")
        print(f"⭐ Bestsellers: {len(bestseller_ids)}\n")

        # ── Tạo orders theo từng ngày ─────────────────────────
        current_date = START_DATE
        total_orders = 0
        total_payments = 0
        order_id_counter = 1

        all_dates = []
        d = START_DATE
        while d <= END_DATE:
            all_dates.append(d)
            d += timedelta(days=1)

        for day_idx, current_date in enumerate(all_dates):
            num_orders = get_num_orders_for_day(current_date)
            is_today   = current_date == END_DATE
            weekday    = current_date.weekday()
            is_weekend = weekday >= 5

            # Phân bổ đơn theo khung giờ
            if is_weekend:
                session_dist = {"morning": 0.35, "afternoon": 0.30, "evening": 0.35}
            else:
                session_dist = {"morning": 0.45, "afternoon": 0.25, "evening": 0.30}

            orders_morning   = int(num_orders * session_dist["morning"])
            orders_afternoon = int(num_orders * session_dist["afternoon"])
            orders_evening   = num_orders - orders_morning - orders_afternoon

            day_orders = (
                [("morning",   orders_morning)] +
                [("afternoon", orders_afternoon)] +
                [("evening",   orders_evening)]
            )

            for session_type, count in day_orders:
                for _ in range(count):
                    hour = get_hour_for_session(session_type)
                    minute = random.randint(0, 59)
                    second = random.randint(0, 59)

                    order_dt = datetime(
                        current_date.year, current_date.month, current_date.day,
                        hour, minute, second
                    )

                    # Chọn bàn ngẫu nhiên
                    table = random.choice(tables)

                    # Chọn nhân viên — rotate theo giờ để realistic
                    if hour < 14:
                        # Ca sáng: staff 1, 2
                        staff_pool = staff_users[:max(1, len(staff_users)//2)]
                    else:
                        # Ca chiều/tối: staff 3, 4
                        staff_pool = staff_users[len(staff_users)//2:] or staff_users
                    user = random.choice(staff_pool)

                    # Tạo order
                    order = Order(
                        table_id=table.id,
                        user_id=user.id,
                        status=OrderStatus.PAID,
                        discount_amount=0,
                    )
                    order.created_at = order_dt
                    order.updated_at = order_dt
                    session.add(order)
                    session.flush()

                    # ── Thêm items ────────────────────────────
                    # Số lượng món: 1-5, cuối tuần/tối thường nhiều hơn
                    if is_weekend or session_type == "evening":
                        num_items = weighted_choice([1,2,3,4,5], [10,30,35,20,5])
                    else:
                        num_items = weighted_choice([1,2,3,4,5], [20,40,25,12,3])

                    subtotal = 0
                    for _ in range(num_items):
                        # Chọn sản phẩm theo session
                        cat_products = get_products_by_session(
                            session_type, products_by_cat
                        )
                        product = pick_product(cat_products, bestseller_ids)

                        size_name, size_delta = get_size_for_product(
                            product, session_type
                        )

                        unit_price = product.base_price + size_delta
                        quantity   = weighted_choice([1,2,3], [70, 25, 5])

                        item = OrderItem(
                            order_id=order.id,
                            product_id=product.id,
                            product_name=product.name,
                            size=size_name,
                            quantity=quantity,
                            unit_price=unit_price,
                            note="",
                        )
                        session.add(item)
                        subtotal += unit_price * quantity

                    # ── Giảm giá nhân viên (5% đơn) ──────────
                    apply_discount = random.random() < 0.05
                    discount_rate   = 0.20 if apply_discount else 0.0
                    discount_amount = int(subtotal * discount_rate)
                    final_amount    = subtotal - discount_amount

                    # ── Payment ───────────────────────────────
                    method = get_payment_method(final_amount)

                    # Tiền khách đưa (tiền mặt)
                    if method == PaymentMethod.CASH:
                        # Làm tròn lên
                        roundings = [0, 5000, 10000, 20000, 50000]
                        extra = random.choice(roundings)
                        amount_received = final_amount + extra
                    else:
                        amount_received = final_amount

                    change_amount = amount_received - final_amount

                    payment = Payment(
                        order_id=order.id,
                        method=method,
                        subtotal=subtotal,
                        discount_rate=discount_rate,
                        discount_amount=discount_amount,
                        total_amount=final_amount,
                        amount_received=amount_received,
                        change_amount=change_amount,
                        note="",
                    )
                    payment.paid_at = order_dt
                    session.add(payment)

                    total_orders   += 1
                    total_payments += 1

            # Commit theo ngày
            session.commit()

            # ── HÔM NAY: tạo thêm đơn ACTIVE để Staff có data ──
            if is_today:
                print(f"\n📅 Hôm nay ({current_date}): Tạo thêm đơn ACTIVE cho Staff...")
                now = datetime.now()
                active_count = random.randint(3, 8)
                used_tables = set()

                for i in range(active_count):
                    # Chọn bàn chưa dùng
                    available = [t for t in tables if t.id not in used_tables]
                    if not available:
                        break
                    table = random.choice(available)
                    used_tables.add(table.id)

                    user = random.choice(staff_users)
                    order_time = now - timedelta(minutes=random.randint(5, 90))

                    order = Order(
                        table_id=table.id,
                        user_id=user.id,
                        status=OrderStatus.ACTIVE,
                        discount_amount=0,
                    )
                    order.created_at = order_time
                    order.updated_at = order_time
                    session.add(order)
                    session.flush()

                    # Thêm 1-4 món
                    num_items = random.randint(1, 4)
                    for _ in range(num_items):
                        cat_products = get_products_by_session(
                            "morning", products_by_cat
                        )
                        product = pick_product(cat_products, bestseller_ids)
                        size_name, size_delta = get_size_for_product(
                            product, "morning"
                        )
                        unit_price = product.base_price + size_delta
                        quantity   = random.randint(1, 2)

                        item = OrderItem(
                            order_id=order.id,
                            product_id=product.id,
                            product_name=product.name,
                            size=size_name,
                            quantity=quantity,
                            unit_price=unit_price,
                            note="",
                        )
                        session.add(item)

                    # Cập nhật trạng thái bàn
                    table.status = TableStatus.USING
                    total_orders += 1

                session.commit()
                print(f"✅ Tạo {active_count} đơn ACTIVE cho Staff UI.\n")

            # Progress
            if (day_idx + 1) % 10 == 0 or current_date == END_DATE:
                print(
                    f"  [{day_idx+1}/{len(all_dates)}] "
                    f"{current_date}  "
                    f"orders={total_orders:,}  "
                    f"payments={total_payments:,}"
                )

        print("\n" + "=" * 50)
        print("✅  SEED HOÀN THÀNH!")
        print(f"   Tổng orders  : {total_orders:,}")
        print(f"   Tổng payments: {total_payments:,}")
        print(f"   Từ {START_DATE} → {END_DATE}")
        print("=" * 50)

        # ── Thống kê nhanh ────────────────────────────────────
        from models.payment import Payment as P
        from sqlalchemy import func

        total_rev = session.query(func.sum(P.total_amount)).scalar() or 0
        avg_bill  = session.query(func.avg(P.total_amount)).scalar() or 0
        max_bill  = session.query(func.max(P.total_amount)).scalar() or 0
        min_bill  = session.query(func.min(P.total_amount)).scalar() or 0

        cash_count     = session.query(P).filter(P.method == PaymentMethod.CASH).count()
        banking_count  = session.query(P).filter(P.method == PaymentMethod.BANKING).count()
        card_count     = session.query(P).filter(P.method == PaymentMethod.CARD).count()

        print(f"\n📊 THỐNG KÊ NHANH:")
        print(f"   Tổng doanh thu : {total_rev:,.0f}₫")
        print(f"   Bill trung bình: {avg_bill:,.0f}₫")
        print(f"   Bill lớn nhất  : {max_bill:,.0f}₫")
        print(f"   Bill nhỏ nhất  : {min_bill:,.0f}₫")
        print(f"   Tiền mặt   : {cash_count:,} đơn ({cash_count/total_payments*100:.0f}%)")
        print(f"   Chuyển khoản: {banking_count:,} đơn ({banking_count/total_payments*100:.0f}%)")
        print(f"   Thẻ        : {card_count:,} đơn ({card_count/total_payments*100:.0f}%)")

        # Top 5 sản phẩm
        from models.order_item import OrderItem as OI
        top5 = (
            session.query(
                OI.product_name,
                func.sum(OI.quantity).label("qty"),
                func.sum(OI.unit_price * OI.quantity).label("rev")
            )
            .group_by(OI.product_name)
            .order_by(func.sum(OI.quantity).desc())
            .limit(5)
            .all()
        )
        print(f"\n🏆 TOP 5 SẢN PHẨM:")
        for i, (name, qty, rev) in enumerate(top5, 1):
            print(f"   {i}. {name:<35} {qty:>5} ly  {rev:>12,.0f}₫")

        # Bàn đang active
        active_tables = session.query(CafeTable).filter(
            CafeTable.status == TableStatus.USING
        ).count()
        active_orders_today = session.query(Order).filter(
            Order.status == OrderStatus.ACTIVE
        ).count()
        print(f"\n🪑 Bàn đang sử dụng : {active_tables}")
        print(f"📋 Đơn đang mở      : {active_orders_today}")
        print("\n✅ Sẵn sàng để demo!")

    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        print(f"\n❌ Lỗi: {e}")
    finally:
        session.close()


if __name__ == "__main__":
    seed()