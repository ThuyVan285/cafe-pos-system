# FILE: ui/screens/dashboard_screen.py
# Thêm import ở đầu file
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QStackedWidget, QScrollArea,
    QGridLayout, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QMessageBox,
    QDialog, QFormLayout, QCheckBox, QSizePolicy
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

from database.db import get_session
from models.user import Role


# ─────────────────────────────────────────────────────────────
# STAT CARD
# ─────────────────────────────────────────────────────────────
class StatCard(QWidget):
    def __init__(self, icon, title, value, color):
        super().__init__()
        self.setFixedHeight(110)
        self.setStyleSheet(f"""
            QWidget {{
                background: white;
                border-radius: 14px;
                border-left: 5px solid {color};
            }}
        """)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        top = QHBoxLayout()
        lbl_icon = QLabel(icon)
        lbl_icon.setFont(QFont("Segoe UI", 22))
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: bold; border: none;"
        )
        top.addWidget(lbl_icon)
        top.addWidget(lbl_title)
        top.addStretch()
        layout.addLayout(top)

        self.lbl_value = QLabel(value)
        self.lbl_value.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
        self.lbl_value.setStyleSheet("color: #1E2D3D; border: none;")
        layout.addWidget(self.lbl_value)

    def set_value(self, value):
        self.lbl_value.setText(value)


# ─────────────────────────────────────────────────────────────
# SIDEBAR BUTTON
# ─────────────────────────────────────────────────────────────
class SidebarBtn(QPushButton):
    def __init__(self, icon, label):
        super().__init__(f"  {icon}  {label}")
        self.setFixedHeight(48)
        self.setFont(QFont("Segoe UI", 11))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setCheckable(True)
        self.set_active(False)

    def set_active(self, active: bool):
        if active:
            self.setStyleSheet("""
                QPushButton {
                    background: rgba(255,255,255,0.2);
                    color: white;
                    border: none;
                    border-left: 4px solid white;
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                    font-weight: bold;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    color: rgba(255,255,255,0.75);
                    border: none;
                    border-left: 4px solid transparent;
                    border-radius: 0px;
                    text-align: left;
                    padding-left: 16px;
                }
                QPushButton:hover {
                    background: rgba(255,255,255,0.1);
                    color: white;
                }
            """)


# ─────────────────────────────────────────────────────────────
# DASHBOARD SCREEN
# ─────────────────────────────────────────────────────────────
class DashboardScreen(QWidget):

    def __init__(self, user):
        super().__init__()
        self.user = user
        self.session = get_session()
        self.setStyleSheet("background: #F0F4FA;")
        self.sidebar_btns = []
        self.build_ui()

    def build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        root.addWidget(self._build_sidebar())
        root.addWidget(self._build_content(), 1)

    # ── SIDEBAR ───────────────────────────────────────────────
    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("background: #1565C0;")

        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QWidget()
        header.setFixedHeight(100)
        header.setStyleSheet("background: #0D47A1;")
        h = QVBoxLayout(header)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)

        lbl_icon = QLabel("☕")
        lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icon.setStyleSheet("font-size: 28px;")

        lbl_name = QLabel(self.user.full_name)
        lbl_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_name.setStyleSheet(
            "color: white; font-size: 13px; font-weight: bold;"
        )

        lbl_role = QLabel(self.user.role.value)
        lbl_role.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_role.setStyleSheet(
            "color: rgba(255,255,255,0.7); font-size: 11px;"
        )

        h.addWidget(lbl_icon)
        h.addWidget(lbl_name)
        h.addWidget(lbl_role)
        layout.addWidget(header)
        layout.addSpacing(8)

        # Menu items theo role
        if self.user.role == Role.ADMIN:
            menus = [
                ("📊", "Tổng quan",      0),
                ("👥", "Người dùng",     1),
                ("🍹", "Sản phẩm",       2),
                ("📈", "Báo cáo",        3),

            ]
        else:  # MANAGER
            menus = [
                ("📊", "Tổng quan",      0),
                ("🍹", "Sản phẩm",       2),
                ("📈", "Báo cáo",        3),
                ("🪑", "Hỗ trợ bán hàng", 4),
            ]

        for icon, label, idx in menus:
            btn = SidebarBtn(icon, label)
            btn.clicked.connect(
                lambda checked, i=idx, b=btn: self._switch_tab(i, b)
            )
            self.sidebar_btns.append((btn, idx))
            layout.addWidget(btn)

        layout.addStretch()

        # Logout
        btn_logout = QPushButton("  🚪  Đăng xuất")
        btn_logout.setFixedHeight(44)
        btn_logout.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_logout.setStyleSheet("""
            QPushButton {
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.8);
                border: none;
                text-align: left;
                padding-left: 16px;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(229,57,53,0.6);
                color: white;
            }
        """)
        btn_logout.clicked.connect(self._on_logout)
        layout.addWidget(btn_logout)

        return sidebar

    def _switch_tab(self, index, clicked_btn):
        self.stack.setCurrentIndex(index)
        titles = {
            0: "📊  Tổng quan",
            1: "👥  Quản lý người dùng",
            2: "🍹  Quản lý sản phẩm",
            3: "📈  Báo cáo doanh thu",
            5: "🪑  Hỗ trợ bán hàng",
        }
        self.header_title.setText(titles.get(index, ""))
        for btn, _ in self.sidebar_btns:
            btn.set_active(btn == clicked_btn)
    # ── CONTENT ───────────────────────────────────────────────
    def _build_content(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background: #F0F4FA;")

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header bar
        self.header_bar = QWidget()
        self.header_bar.setFixedHeight(52)
        self.header_bar.setStyleSheet(
            "background: white; border-bottom: 1px solid #DDE5F0;"
        )
        hb = QHBoxLayout(self.header_bar)
        hb.setContentsMargins(20, 0, 16, 0)

        self.header_title = QLabel("📊  Tổng quan")
        self.header_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        self.header_title.setStyleSheet("color: #1E2D3D;")
        hb.addWidget(self.header_title)
        hb.addStretch()

        # ✅ THÊM NÚT MENU 3 GẠCH
        self.admin_menu_btn = QPushButton("☰")
        self.admin_menu_btn.setFixedSize(38, 38)
        self.admin_menu_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.admin_menu_btn.setStyleSheet("""
            QPushButton {
                background: #F0F4FA;
                color: #1565C0;
                border: 1.5px solid #DDEAF8;
                border-radius: 10px;
                font-size: 18px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: #E3F2FD;
                border: 1.5px solid #1565C0;
            }
        """)
        self.admin_menu_btn.clicked.connect(self._show_admin_menu)
        hb.addWidget(self.admin_menu_btn)

        layout.addWidget(self.header_bar)

        # Stack giữ nguyên...
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_overview())
        self.stack.addWidget(self._build_users())
        self.stack.addWidget(self._build_products())
        self.stack.addWidget(self._build_reports())
        self.stack.addWidget(self._build_pos_support())

        layout.addWidget(self.stack, 1)

        if self.sidebar_btns:
            self.sidebar_btns[0][0].set_active(True)

        return widget

    # ── TAB 0: OVERVIEW ───────────────────────────────────────


    def _build_overview(self) -> QWidget:
        from services.statistic_service import StatisticService
        from models.order import Order, OrderStatus
        from models.table import CafeTable, TableStatus
        from models.payment import Payment
        from sqlalchemy import func
        from datetime import datetime

        stat = StatisticService(self.session)

        outer = QWidget()
        outer.setStyleSheet("background: #F0F4FA;")

        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        # =========================================================
        # SCROLL AREA
        # =========================================================
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setFrameShape(QFrame.Shape.NoFrame)

        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: #F0F4FA;
            }

            QScrollBar:vertical {
                background: #E8EEF8;
                width: 8px;
                border-radius: 4px;
            }

            QScrollBar::handle:vertical {
                background: #B0C4DE;
                border-radius: 4px;
            }
        """)

        widget = QWidget()
        widget.setStyleSheet("background: #F0F4FA;")

        widget.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Minimum
        )

        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(14)

        # =========================================================
        # DATA
        # =========================================================
        today = datetime.now().date()

        today_rev = stat.get_today_revenue()

        today_count = self.session.query(Order).filter(
            Order.status == OrderStatus.PAID,
            func.date(Order.created_at) == today
        ).count()

        total_tables = self.session.query(CafeTable).count()

        using_tables = self.session.query(CafeTable).filter(
            CafeTable.status == TableStatus.USING
        ).count()

        active_orders_list = self.session.query(Order).filter(
            Order.status == OrderStatus.ACTIVE
        ).all()

        active_orders = len(active_orders_list)

        active_rev = sum(o.subtotal for o in active_orders_list)

        all_paid = self.session.query(Order).filter(
            Order.status == OrderStatus.PAID
        ).all()

        def fmt_rev(v):
            v = int(v)
            if v == 0:
                return "0đ"
            return f"{v:,}đ"

        # =========================================================
        # TITLE
        # =========================================================
        lbl_title = QLabel("Bức tranh kinh doanh")
        lbl_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #1E2D3D;")

        layout.addWidget(lbl_title)

        # =========================================================
        # FORMAT
        # =========================================================
        def fmt_money(v):
            v = int(v)
            if v == 0:
                return "0đ"
            return f"{v:,}đ"
        # =========================================================
        # TOP CARDS
        # =========================================================
        cards_widget = QWidget()
        cards_widget.setStyleSheet("background: transparent;")

        cards_row = QHBoxLayout(cards_widget)
        cards_row.setContentsMargins(0, 0, 0, 0)
        cards_row.setSpacing(12)

        def make_top_card(title, value, sub, color, icon):
            w = QWidget()

            w.setMinimumHeight(120)

            w.setStyleSheet(f"""
                QWidget {{
                    background: white;
                    border-radius: 12px;
                    border-top: 4px solid {color};
                }}
            """)

            v = QVBoxLayout(w)
            v.setContentsMargins(16, 14, 16, 14)
            v.setSpacing(4)

            top_row = QHBoxLayout()

            lbl_ic = QLabel(icon)
            lbl_ic.setStyleSheet("font-size: 20px; border: none;")

            lbl_t = QLabel(title)
            lbl_t.setStyleSheet(
                "color: #888; font-size: 12px; border: none;"
            )

            top_row.addWidget(lbl_ic)
            top_row.addWidget(lbl_t, 1)

            v.addLayout(top_row)

            lbl_val = QLabel(value)
            lbl_val.setFont(QFont("Segoe UI", 20, QFont.Weight.Bold))
            lbl_val.setStyleSheet(
                f"color: {color}; border: none;"
            )

            v.addWidget(lbl_val)

            lbl_sub = QLabel(sub)
            lbl_sub.setStyleSheet(
                "color: #AAB; font-size: 11px; border: none;"
            )

            v.addWidget(lbl_sub)

            return w

        week_rev = stat.get_week_revenue()

        prev_rev = week_rev / 7 if week_rev else 0

        pct = (
            f"+{((today_rev - prev_rev) / prev_rev * 100):.0f}% so với TB tuần"
            if prev_rev else
            "Chưa có dữ liệu"
        )

        cards_row.addWidget(
            make_top_card(
                "Doanh thu hôm nay",
                fmt_rev(today_rev),
                pct,
                "#1565C0",
                "💰"
            )
        )

        cards_row.addWidget(
            make_top_card(
                "Đơn hôm nay",
                str(today_count),
                f"{today_count} đơn thanh toán",
                "#2E7D32",
                "📋"
            )
        )

        cards_row.addWidget(
            make_top_card(
                "Bàn đang phục vụ",
                f"{using_tables}/{total_tables}",
                f"{active_orders} đơn đang mở",
                "#E65100",
                "🪑"
            )
        )

        cards_row.addWidget(
            make_top_card(
                "Doanh thu đang phục vụ",
                fmt_rev(active_rev),
                f"{active_orders} đơn",
                "#6A1B9A",
                "🔄"
            )
        )

        layout.addWidget(cards_widget)

        # =========================================================
        # MAIN ROW
        # =========================================================
        main_row = QHBoxLayout()
        main_row.setSpacing(12)

        # =========================================================
        # LEFT SIDE
        # =========================================================
        charts_widget = QWidget()
        charts_widget.setStyleSheet("background: transparent;")

        charts_col = QVBoxLayout(charts_widget)
        charts_col.setContentsMargins(0, 0, 0, 0)
        charts_col.setSpacing(12)

        # =========================================================
        # REVENUE CHART
        # =========================================================
        rev_card = QWidget()

        rev_card.setStyleSheet("""
            background: white;
            border-radius: 12px;
        """)

        rev_layout = QVBoxLayout(rev_card)

        rev_layout.setContentsMargins(16, 14, 16, 14)
        rev_layout.setSpacing(8)

        lbl_rev_title = QLabel("Doanh thu thuần")
        lbl_rev_title.setFont(
            QFont("Segoe UI", 13, QFont.Weight.Bold)
        )

        lbl_rev_title.setStyleSheet("color: #1E2D3D;")

        rev_layout.addWidget(lbl_rev_title)

        lbl_week = QLabel(
            f"{week_rev:,}₫ ({len(all_paid)} hóa đơn)"
        )

        lbl_week.setStyleSheet(
            "color: #888; font-size: 12px;"
        )

        rev_layout.addWidget(lbl_week)

        # Tabs
        self.rev_tab_btns = {}
        self.rev_mode = "hour"

        tab_row = QHBoxLayout()
        tab_row.setSpacing(0)

        for mode, label in [
            ("hour", "Theo giờ"),
            ("day", "Theo ngày"),
            ("weekday", "Theo thứ")
        ]:
            btn = QPushButton(label)

            btn.setFixedHeight(30)

            btn.setCheckable(True)

            btn.setCursor(
                Qt.CursorShape.PointingHandCursor
            )

            btn.clicked.connect(
                lambda checked, m=mode:
                self._switch_rev_chart(m)
            )

            self.rev_tab_btns[mode] = btn

            tab_row.addWidget(btn)

        tab_row.addStretch()

        rev_layout.addLayout(tab_row)

        self.rev_fig = Figure(
            figsize=(8, 3.0),
            facecolor='white'
        )

        self.rev_canvas = FigureCanvas(self.rev_fig)

        self.rev_canvas.setMinimumHeight(260)

        rev_layout.addWidget(self.rev_canvas)

        charts_col.addWidget(rev_card)

        # =========================================================
        # CUSTOMER CHART
        # =========================================================
        cust_card = QWidget()

        cust_card.setStyleSheet("""
            background: white;
            border-radius: 12px;
        """)

        cust_layout = QVBoxLayout(cust_card)

        cust_layout.setContentsMargins(16, 14, 16, 14)
        cust_layout.setSpacing(8)

        lbl_cust_title = QLabel("Lượng khách hàng")

        lbl_cust_title.setFont(
            QFont("Segoe UI", 13, QFont.Weight.Bold)
        )

        lbl_cust_title.setStyleSheet("color: #1E2D3D;")

        cust_layout.addWidget(lbl_cust_title)

        lbl_cust_count = QLabel(
            f"{len(all_paid)} lượt khách"
        )

        lbl_cust_count.setStyleSheet(
            "color: #888; font-size: 12px;"
        )

        cust_layout.addWidget(lbl_cust_count)

        # Tabs
        self.cust_tab_btns = {}
        self.cust_mode = "hour"

        cust_tab_row = QHBoxLayout()

        for mode, label in [
            ("hour", "Theo giờ"),
            ("day", "Theo ngày"),
            ("weekday", "Theo thứ")
        ]:
            btn = QPushButton(label)

            btn.setFixedHeight(30)

            btn.setCheckable(True)

            btn.clicked.connect(
                lambda checked, m=mode:
                self._switch_cust_chart(m)
            )

            self.cust_tab_btns[mode] = btn

            cust_tab_row.addWidget(btn)

        cust_tab_row.addStretch()

        cust_layout.addLayout(cust_tab_row)

        self.cust_fig = Figure(
            figsize=(8, 2.8),
            facecolor='white'
        )

        self.cust_canvas = FigureCanvas(self.cust_fig)

        self.cust_canvas.setMinimumHeight(240)

        cust_layout.addWidget(self.cust_canvas)

        charts_col.addWidget(cust_card)

        main_row.addWidget(charts_widget, 4)

        # =========================================================
        # FEED
        # =========================================================
        # ── ACTIVITY FEED (phải) ──────────────────────────────────────

        feed_card = QWidget()
        feed_card.setStyleSheet("""
            background: white;
            border-radius: 12px;
        """)

        feed_layout = QVBoxLayout(feed_card)
        feed_layout.setContentsMargins(16, 14, 16, 14)
        feed_layout.setSpacing(8)

        # Header
        feed_header = QHBoxLayout()

        lbl_feed = QLabel("🔔 Hoạt động gần đây")
        lbl_feed.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_feed.setStyleSheet("color: #1E2D3D;")

        feed_header.addWidget(lbl_feed)
        feed_header.addStretch()

        feed_layout.addLayout(feed_header)

        # Scroll area
        feed_scroll = QScrollArea()
        feed_scroll.setWidgetResizable(True)

        feed_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }

            QScrollBar:vertical {
                background: #F0F4FA;
                width: 5px;
                border-radius: 2px;
            }

            QScrollBar::handle:vertical {
                background: #B0C8E8;
                border-radius: 2px;
            }
        """)

        feed_content = QWidget()
        feed_content.setStyleSheet("background: transparent;")

        feed_content_layout = QVBoxLayout(feed_content)
        feed_content_layout.setContentsMargins(0, 0, 0, 0)
        feed_content_layout.setSpacing(0)

        # =========================
        # DATA
        # =========================

        from models.order import Order, OrderStatus
        from models.payment import Payment
        from datetime import datetime

        recent_payments = (
            self.session.query(Order, Payment)
            .join(Payment, Payment.order_id == Order.id)
            .filter(Order.status == OrderStatus.PAID)
            .order_by(Order.created_at.desc())
            .limit(20)
            .all()
        )

        icons = ["☕", "🧋", "🍵", "🥤", "🍓", "🧃", "🍦"]

        # =========================
        # ITEMS
        # =========================

        for idx, (order, payment) in enumerate(recent_payments):

            item_w = QWidget()

            item_w.setStyleSheet(f"""
                QWidget {{
                    background: {'#F8FAFF' if idx % 2 == 0 else 'white'};
                    border-radius: 8px;
                    border-bottom: 1px solid #F0F4FA;
                }}
            """)

            item_l = QHBoxLayout(item_w)
            item_l.setContentsMargins(8, 10, 8, 10)
            item_l.setSpacing(10)

            # ── ICON ─────────────────────────

            icon_lbl = QLabel(icons[idx % len(icons)])

            icon_lbl.setFixedSize(36, 36)

            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon_lbl.setStyleSheet("""
                background: #E3F2FD;
                border-radius: 18px;
                font-size: 16px;
            """)

            # ── CONTENT ──────────────────────

            content = QVBoxLayout()
            content.setSpacing(2)

            table_name = (
                order.table.name
                if order.table
                else "Không rõ"
            )

            staff_name = (
                order.user.full_name
                if order.user
                else "Nhân viên"
            )

            items_count = sum(i.quantity for i in order.items)

            item_names = []

            for it in order.items[:2]:
                item_names.append(it.product_name)

            items_str = ", ".join(item_names)

            if len(order.items) > 2:
                items_str += f" +{len(order.items) - 2} món"

            lbl_main = QLabel(
                f"<b>Cafe POS</b> đã bán "
                f"<b>{items_count} món</b> "
                f"tại <b>{table_name}</b>"
            )

            lbl_main.setStyleSheet("""
                color: #1E2D3D;
                font-size: 12px;
                border: none;
            """)

            lbl_main.setWordWrap(True)

            lbl_sub = QLabel(
                f"NV: {staff_name}  •  {items_str}"
            )

            lbl_sub.setStyleSheet("""
                color: #90A4AE;
                font-size: 10px;
                border: none;
            """)

            lbl_sub.setWordWrap(True)

            content.addWidget(lbl_main)
            content.addWidget(lbl_sub)

            # ── RIGHT ────────────────────────

            right = QVBoxLayout()

            right.setSpacing(2)

            right.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

            lbl_amount = QLabel(
                f"{payment.total_amount:,}₫"
            )

            lbl_amount.setStyleSheet("""
                color: #1565C0;
                font-size: 13px;
                font-weight: bold;
                border: none;
            """)

            lbl_amount.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

            # Time

            now = datetime.now()

            diff = now - order.created_at

            if diff.seconds < 60:
                time_str = "Vừa xong"

            elif diff.seconds < 3600:
                time_str = f"{diff.seconds // 60} phút trước"

            elif diff.days == 0:
                time_str = f"{diff.seconds // 3600} giờ trước"

            elif diff.days == 1:
                time_str = "Hôm qua"

            else:
                time_str = order.created_at.strftime(
                    "%d/%m %H:%M"
                )

            lbl_time = QLabel(time_str)

            lbl_time.setStyleSheet("""
                color: #B0BEC5;
                font-size: 10px;
                border: none;
            """)

            lbl_time.setAlignment(
                Qt.AlignmentFlag.AlignRight
            )

            right.addWidget(lbl_amount)
            right.addWidget(lbl_time)

            # ── ADD ──────────────────────────

            item_l.addWidget(icon_lbl)

            item_l.addLayout(content, 1)

            item_l.addLayout(right)

            feed_content_layout.addWidget(item_w)

        feed_content_layout.addStretch()

        feed_scroll.setWidget(feed_content)

        feed_layout.addWidget(feed_scroll)

        # thêm vào main row
        main_row.addWidget(feed_card, 2)
        layout.addLayout(main_row)
        # =========================================================
        # BOTTOM ROW
        # =========================================================
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        # =========================================================
        # PIE CHART
        # =========================================================
        pie_card = QWidget()

        pie_card.setStyleSheet("""
            background: white;
            border-radius: 12px;
        """)

        pie_layout = QVBoxLayout(pie_card)

        pie_layout.setContentsMargins(16, 14, 16, 14)

        lbl_pie = QLabel("Hiệu quả thực đơn")

        lbl_pie.setFont(
            QFont("Segoe UI", 13, QFont.Weight.Bold)
        )

        lbl_pie.setStyleSheet("color: #1E2D3D;")

        pie_layout.addWidget(lbl_pie)

        self.pie_fig = Figure(
            figsize=(4, 3.5),
            facecolor='white'
        )

        self.pie_canvas = FigureCanvas(self.pie_fig)

        self.pie_canvas.setMinimumHeight(300)

        pie_layout.addWidget(self.pie_canvas)

        bottom_row.addWidget(pie_card, 2)

        # =========================================================
        # TOP PRODUCTS
        # =========================================================
        # Top sản phẩm
        top_card = QWidget()
        top_card.setStyleSheet("""
            background: white;
            border-radius: 12px;
        """)

        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(16, 14, 16, 14)
        top_layout.setSpacing(6)

        # Header
        top_header = QHBoxLayout()

        lbl_top_title = QLabel("Top món bán chạy")
        lbl_top_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_top_title.setStyleSheet("color: #1E2D3D;")

        top_header.addWidget(lbl_top_title)
        top_header.addStretch()

        top_layout.addLayout(top_header)

        # Header cột
        col_h = QWidget()
        col_h.setStyleSheet("""
            background: #F5F8FF;
            border-radius: 6px;
        """)

        col_h_layout = QHBoxLayout(col_h)
        col_h_layout.setContentsMargins(8, 4, 8, 4)

        headers = [
            ("#", 35),
            ("Tên món", 0),
            ("SL", 70),
            ("Doanh thu", 110)
        ]

        for text, width in headers:
            lbl = QLabel(text)
            lbl.setStyleSheet("""
                color: #78909C;
                font-size: 11px;
                font-weight: bold;
                border: none;
            """)

            if width:
                lbl.setFixedWidth(width)
                lbl.setAlignment(Qt.AlignmentFlag.AlignRight)

            col_h_layout.addWidget(lbl, 0 if width else 1)

        top_layout.addWidget(col_h)

        # Dữ liệu top sản phẩm
        top_products = stat.get_top_products(limit=10)

        rank_colors = [
            "#1565C0",
            "#2E7D32",
            "#EF6C00",
            "#6A1B9A",
            "#C62828",
            "#00838F",
            "#5D4037",
            "#455A64",
            "#7B1FA2",
            "#546E7A"
        ]

        for idx, (name, qty, revenue) in enumerate(top_products):
            row_w = QWidget()
            row_w.setFixedHeight(40)

            row_w.setStyleSheet(f"""
                QWidget {{
                    background: {'#F8FAFF' if idx % 2 == 0 else 'white'};
                    border-radius: 6px;
                }}
            """)

            row_l = QHBoxLayout(row_w)
            row_l.setContentsMargins(8, 0, 8, 0)
            row_l.setSpacing(8)

            # STT
            lbl_rank = QLabel(str(idx + 1))
            lbl_rank.setFixedSize(22, 22)
            lbl_rank.setAlignment(Qt.AlignmentFlag.AlignCenter)

            lbl_rank.setStyleSheet(f"""
                background: {rank_colors[idx % len(rank_colors)]};
                color: white;
                border-radius: 11px;
                font-size: 11px;
                font-weight: bold;
            """)

            # Tên món
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("""
                color: #1E2D3D;
                font-size: 12px;
                font-weight: 600;
                border: none;
            """)

            # Số lượng
            lbl_qty = QLabel(f"{qty:,}")
            lbl_qty.setFixedWidth(70)
            lbl_qty.setAlignment(Qt.AlignmentFlag.AlignRight)

            lbl_qty.setStyleSheet("""
                color: #455A64;
                font-size: 12px;
                border: none;
            """)

            # Doanh thu
            lbl_rev = QLabel(f"{revenue:,}₫")
            lbl_rev.setFixedWidth(110)
            lbl_rev.setAlignment(Qt.AlignmentFlag.AlignRight)

            lbl_rev.setStyleSheet("""
                color: #1565C0;
                font-size: 12px;
                font-weight: bold;
                border: none;
            """)

            row_l.addWidget(lbl_rank)
            row_l.addWidget(lbl_name, 1)
            row_l.addWidget(lbl_qty)
            row_l.addWidget(lbl_rev)

            top_layout.addWidget(row_w)

        top_layout.addStretch()

        bottom_row.addWidget(top_card, 3)
        layout.addLayout(bottom_row)   # ← THÊM DÒNG NÀY



        # =========================================================
        # DRAW CHARTS
        # =========================================================
        self._draw_rev_chart("hour")

        self._draw_cust_chart("hour")

        self._draw_pie_chart()

        self._update_rev_tab_style("hour")

        self._update_cust_tab_style("hour")

        # =========================================================
        # FINAL
        # =========================================================
        scroll.setWidget(widget)

        scroll.verticalScrollBar().setSingleStep(20)

        outer_layout.addWidget(scroll)

        return outer


    # ── CHART METHODS ─────────────────────────────────────────────
    def _switch_rev_chart(self, mode: str):
        self.rev_mode = mode
        self._draw_rev_chart(mode)
        self._update_rev_tab_style(mode)

    def _switch_cust_chart(self, mode: str):
        self.cust_mode = mode
        self._draw_cust_chart(mode)
        self._update_cust_tab_style(mode)

    def _tab_style(self, active: bool) -> str:
        if active:
            return """
                QPushButton {
                    background: #1565C0; color: white;
                    border: none; border-radius: 6px;
                    font-size: 11px; font-weight: bold;
                    padding: 0 12px;
                }
            """
        return """
            QPushButton {
                background: #F0F4FA; color: #555;
                border: none; border-radius: 6px;
                font-size: 11px; padding: 0 12px;
            }
            QPushButton:hover { background: #E3F2FD; color: #1565C0; }
        """

    def _update_rev_tab_style(self, active: str):
        for mode, btn in self.rev_tab_btns.items():
            btn.setStyleSheet(self._tab_style(mode == active))

    def _update_cust_tab_style(self, active: str):
        for mode, btn in self.cust_tab_btns.items():
            btn.setStyleSheet(self._tab_style(mode == active))

    def _draw_rev_chart(self, mode: str):
        from services.statistic_service import StatisticService
        stat = StatisticService(self.session)

        self.rev_fig.clear()
        ax = self.rev_fig.add_subplot(111)
        ax.set_facecolor('white')
        self.rev_fig.patch.set_facecolor('white')

        color = '#5B9BD5'

        if mode == "hour":
            data = stat.get_revenue_by_hour()
            if data:
                hours, vals = zip(*data)
                labels = [f"{h:02d}h" for h in hours]
                ax.bar(range(len(labels)), [v / 1000 for v in vals],
                       color=color, width=0.6, zorder=3)
                ax.set_xticks(range(len(labels)))
                ax.set_xticklabels(labels, fontsize=7, rotation=45)
            ax.set_ylabel("Nghìn ₫", fontsize=8)

        elif mode == "day":
            data = stat.get_revenue_by_day(days=7)
            if data:
                dates, vals = zip(*data)
                ax.bar(range(len(dates)), [v / 1000 for v in vals],
                       color=color, width=0.6, zorder=3)
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels(dates, fontsize=7, rotation=45)
            ax.set_ylabel("Nghìn ₫", fontsize=8)

        elif mode == "weekday":
            data = stat.get_revenue_by_weekday()
            if data:
                days_lbl, vals = zip(*data)
                ax.bar(range(len(days_lbl)), [v / 1000 for v in vals],
                       color=color, width=0.6, zorder=3)
                ax.set_xticks(range(len(days_lbl)))
                ax.set_xticklabels(days_lbl, fontsize=8)
            ax.set_ylabel("Nghìn ₫", fontsize=8)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(axis='y', alpha=0.3, zorder=0)
        ax.tick_params(axis='both', labelsize=8)
        self.rev_fig.tight_layout(pad=0.5)
        self.rev_canvas.draw()

    def _draw_cust_chart(self, mode: str):
        from services.statistic_service import StatisticService
        stat = StatisticService(self.session)

        self.cust_fig.clear()
        ax = self.cust_fig.add_subplot(111)
        ax.set_facecolor('white')
        self.cust_fig.patch.set_facecolor('white')

        color = '#5B9BD5'

        if mode == "hour":
            data = stat.get_customers_by_hour()
            hours_all = list(range(24))
            vals = [0] * 24
            for h, c in data:
                vals[h] = c
            labels = [f"{h:02d}h" for h in hours_all]
            ax.fill_between(hours_all, vals, alpha=0.25, color=color)
            ax.plot(hours_all, vals, color=color, linewidth=2)
            ax.set_xticks([0, 5, 10, 15, 20, 23])
            ax.set_xticklabels(
                ["05:00", "07:00", "10:00", "13:00", "17:00", "20:00"],
                fontsize=7
            )

        elif mode == "day":
            data = stat.get_customers_by_day(days=7)
            if data:
                dates, vals = zip(*data)
                ax.fill_between(range(len(dates)), vals, alpha=0.25, color=color)
                ax.plot(range(len(dates)), vals, color=color, linewidth=2, marker='o', markersize=4)
                ax.set_xticks(range(len(dates)))
                ax.set_xticklabels(dates, fontsize=7, rotation=45)

        elif mode == "weekday":
            data = stat.get_customers_by_weekday()
            if data:
                days_lbl, vals = zip(*data)
                ax.fill_between(range(len(days_lbl)), vals, alpha=0.25, color=color)
                ax.plot(range(len(days_lbl)), vals, color=color, linewidth=2, marker='o', markersize=4)
                ax.set_xticks(range(len(days_lbl)))
                ax.set_xticklabels(days_lbl, fontsize=8)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(alpha=0.3)
        ax.tick_params(axis='both', labelsize=8)
        self.cust_fig.tight_layout(pad=0.5)
        self.cust_canvas.draw()

    def _draw_pie_chart(self):
        from services.statistic_service import StatisticService
        stat = StatisticService(self.session)

        self.pie_fig.clear()
        ax = self.pie_fig.add_subplot(111)
        ax.set_facecolor('white')
        self.pie_fig.patch.set_facecolor('white')

        data = stat.get_revenue_by_category()

        if not data:
            ax.text(0.5, 0.5, "Chưa có dữ liệu",
                    ha='center', va='center', transform=ax.transAxes,
                    color='#888', fontsize=10)
        else:
            labels = [d[0] for d in data]
            values = [d[1] for d in data]
            colors = ['#1565C0', '#2E7D32', '#E65100', '#6A1B9A', '#C62828',
                      '#00838F', '#F57F17', '#4527A0'][:len(labels)]

            wedges, texts, autotexts = ax.pie(
                values,
                labels=None,
                colors=colors,
                autopct='%1.0f%%',
                pctdistance=0.75,
                startangle=90,
                wedgeprops=dict(width=0.6)  # donut style
            )
            for t in autotexts:
                t.set_fontsize(8)
                t.set_color('white')

            ax.legend(
                wedges, labels,
                loc="lower center",
                ncol=3,
                fontsize=7,
                frameon=False,
                bbox_to_anchor=(0.5, -0.15)
            )

        self.pie_fig.tight_layout(pad=0.3)
        self.pie_canvas.draw()
    # ── TAB 1: USERS ──────────────────────────────────────────
    def _build_users(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background: #F0F4FA;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()
        self.user_search = QLineEdit()
        self.user_search.setPlaceholderText("🔍  Tìm người dùng...")
        self.user_search.setFixedHeight(38)
        self.user_search.setStyleSheet("""
            QLineEdit {
                background: white; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px; font-size: 13px;
            }
            QLineEdit:focus { border: 1.5px solid #1565C0; }
        """)
        self.user_search.textChanged.connect(self._load_users)

        btn_add_user = QPushButton("➕  Thêm người dùng")
        btn_add_user.setFixedHeight(38)
        btn_add_user.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px;
                padding: 0 16px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn_add_user.clicked.connect(self._on_add_user)

        toolbar.addWidget(self.user_search, 1)
        toolbar.addWidget(btn_add_user)
        layout.addLayout(toolbar)

        # Table
        self.user_table = QTableWidget()
        self.user_table.setColumnCount(5)
        self.user_table.setHorizontalHeaderLabels(
            ["ID", "Họ tên", "Username", "Role", "Thao tác"]
        )
        self.user_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.user_table.setStyleSheet("""
            QTableWidget {
                background: white; border-radius: 12px;
                gridline-color: #EEF2F8; font-size: 13px;
            }
            QHeaderView::section {
                background: #F5F8FF; color: #555;
                font-weight: bold; font-size: 12px;
                border: none; padding: 8px;
            }
            QTableWidget::item { padding: 8px; border: none; }
            QTableWidget::item:selected { background: #E3F2FD; color: #1E2D3D; }
        """)
        self.user_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.user_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.user_table.verticalHeader().setVisible(False)
        layout.addWidget(self.user_table)

        self._load_users()
        return widget

    def _load_users(self):
        from repositories.user_repository import UserRepository
        repo = UserRepository(self.session)
        users = repo.get_all()

        keyword = self.user_search.text().lower() if hasattr(self, 'user_search') else ""
        if keyword:
            users = [u for u in users if keyword in u.full_name.lower()
                     or keyword in u.username.lower()]

        self.user_table.setRowCount(len(users))
        for row, user in enumerate(users):
            self.user_table.setItem(row, 0, QTableWidgetItem(str(user.id)))
            self.user_table.setItem(row, 1, QTableWidgetItem(user.full_name))
            self.user_table.setItem(row, 2, QTableWidgetItem(user.username))

            role_item = QTableWidgetItem(user.role.value)
            colors = {"ADMIN": "#D32F2F", "MANAGER": "#1565C0", "STAFF": "#2E7D32"}
            role_item.setForeground(QColor(colors.get(user.role.value, "#333")))
            self.user_table.setItem(row, 3, role_item)

            # Thao tác
            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(6)

            btn_edit = QPushButton("✏ Sửa")
            btn_edit.setFixedHeight(28)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background: #1565C0; color: white;
                    border: none; border-radius: 6px;
                    font-size: 11px; padding: 0 10px;
                }
                QPushButton:hover { background: #1976D2; }
            """)
            btn_edit.clicked.connect(
                lambda checked, u=user: self._on_edit_user(u)
            )

            btn_del = QPushButton("🗑 Xóa")
            btn_del.setFixedHeight(28)
            btn_del.setStyleSheet("""
                QPushButton {
                    background: #E53935; color: white;
                    border: none; border-radius: 6px;
                    font-size: 11px; padding: 0 10px;
                }
                QPushButton:hover { background: #C62828; }
            """)
            btn_del.clicked.connect(
                lambda checked, u=user: self._on_delete_user(u)
            )

            btn_layout.addWidget(btn_edit)
            btn_layout.addWidget(btn_del)
            self.user_table.setCellWidget(row, 4, btn_widget)
            self.user_table.setRowHeight(row, 44)

    def _on_add_user(self):
        from ui.dialogs.user_dialog import UserDialog
        dialog = UserDialog(session=self.session, parent=self)
        if dialog.exec():
            self._load_users()

    def _on_edit_user(self, user):
        from ui.dialogs.user_dialog import UserDialog
        dialog = UserDialog(session=self.session, user=user, parent=self)
        if dialog.exec():
            self._load_users()

    def _on_delete_user(self, user):
        reply = QMessageBox.question(
            self, "Xác nhận",
            f"Xóa tài khoản '{user.username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from repositories.user_repository import UserRepository
            repo = UserRepository(self.session)
            repo.delete(user.id)
            self.session.commit()
            self._load_users()

    # ── TAB 2: PRODUCTS ───────────────────────────────────────
    def _build_products(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background: #F0F4FA;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Toolbar
        toolbar = QHBoxLayout()
        self.prod_search = QLineEdit()
        self.prod_search.setPlaceholderText("🔍  Tìm sản phẩm...")
        self.prod_search.setFixedHeight(38)
        self.prod_search.setStyleSheet("""
            QLineEdit {
                background: white; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px; font-size: 13px;
            }
            QLineEdit:focus { border: 1.5px solid #1565C0; }
        """)
        self.prod_search.textChanged.connect(self._load_products)

        if self.user.role == Role.ADMIN:
            btn_add = QPushButton("➕  Thêm sản phẩm")
            btn_add.setFixedHeight(38)
            btn_add.setStyleSheet("""
                QPushButton {
                    background: #1565C0; color: white;
                    border: none; border-radius: 8px;
                    padding: 0 16px; font-weight: bold;
                }
                QPushButton:hover { background: #1976D2; }
            """)
            btn_add.clicked.connect(self._on_add_product)
            toolbar.addWidget(self.prod_search, 1)
            toolbar.addWidget(btn_add)
        else:
            toolbar.addWidget(self.prod_search, 1)

        layout.addLayout(toolbar)

        # Table
        self.prod_table = QTableWidget()
        self.prod_table.setColumnCount(6)
        self.prod_table.setHorizontalHeaderLabels(
            ["ID", "Tên sản phẩm", "Danh mục", "Giá", "Size", "Thao tác"]
        )
        self.prod_table.horizontalHeader().setSectionResizeMode(
            1, QHeaderView.ResizeMode.Stretch
        )
        self.prod_table.setStyleSheet("""
            QTableWidget {
                background: white; border-radius: 12px;
                gridline-color: #EEF2F8; font-size: 13px;
            }
            QHeaderView::section {
                background: #F5F8FF; color: #555;
                font-weight: bold; font-size: 12px;
                border: none; padding: 8px;
            }
            QTableWidget::item { padding: 8px; border: none; }
            QTableWidget::item:selected { background: #E3F2FD; color: #1E2D3D; }
        """)
        self.prod_table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        self.prod_table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self.prod_table.verticalHeader().setVisible(False)
        layout.addWidget(self.prod_table)

        self._load_products()
        return widget

    def _load_products(self):
        from repositories.product_repository import ProductRepository
        repo = ProductRepository(self.session)
        keyword = self.prod_search.text().strip() if hasattr(self, 'prod_search') else ""
        products = repo.search(keyword) if keyword else repo.get_all()

        self.prod_table.setRowCount(len(products))
        for row, p in enumerate(products):
            self.prod_table.setItem(row, 0, QTableWidgetItem(str(p.id)))
            self.prod_table.setItem(row, 1, QTableWidgetItem(p.name))
            self.prod_table.setItem(row, 2, QTableWidgetItem(
                p.category.name if p.category else "—"
            ))
            self.prod_table.setItem(row, 3, QTableWidgetItem(f"{p.base_price:,}₫"))
            self.prod_table.setItem(row, 4, QTableWidgetItem(
                "✅ Có" if p.has_size else "❌ Không"
            ))

            btn_widget = QWidget()
            btn_layout = QHBoxLayout(btn_widget)
            btn_layout.setContentsMargins(4, 2, 4, 2)
            btn_layout.setSpacing(6)

            btn_edit = QPushButton("✏ Sửa")
            btn_edit.setFixedHeight(28)
            btn_edit.setStyleSheet("""
                QPushButton {
                    background: #1565C0; color: white;
                    border: none; border-radius: 6px;
                    font-size: 11px; padding: 0 10px;
                }
            """)
            btn_edit.clicked.connect(
                lambda checked, prod=p: self._on_edit_product(prod)
            )
            btn_layout.addWidget(btn_edit)

            if self.user.role == Role.ADMIN:
                btn_del = QPushButton("🗑 Ẩn")
                btn_del.setFixedHeight(28)
                btn_del.setStyleSheet("""
                    QPushButton {
                        background: #E53935; color: white;
                        border: none; border-radius: 6px;
                        font-size: 11px; padding: 0 10px;
                    }
                """)
                btn_del.clicked.connect(
                    lambda checked, prod=p: self._on_hide_product(prod)
                )
                btn_layout.addWidget(btn_del)

            self.prod_table.setCellWidget(row, 5, btn_widget)
            self.prod_table.setRowHeight(row, 44)

    def _on_add_product(self):
        QMessageBox.information(self, "Thông báo", "Chức năng thêm sản phẩm đang phát triển!")

    def _on_edit_product(self, product):
        QMessageBox.information(self, "Thông báo", f"Sửa: {product.name}")

    def _on_hide_product(self, product):
        reply = QMessageBox.question(
            self, "Xác nhận", f"Ẩn sản phẩm '{product.name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from repositories.product_repository import ProductRepository
            repo = ProductRepository(self.session)
            repo.delete(product.id)
            self.session.commit()
            self._load_products()

    # ── TAB 3: REPORTS ────────────────────────────────────────
    def _build_reports(self) -> QWidget:
        from services.statistic_service import StatisticService
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
        from matplotlib.figure import Figure

        stat = StatisticService(self.session)

        outer = QWidget()
        outer.setStyleSheet("background: #F0F4FA;")
        outer_layout = QVBoxLayout(outer)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("""
            QScrollArea { border: none; background: #F0F4FA; }
            QScrollBar:vertical { background: #E8EEF8; width: 8px; border-radius: 4px; }
            QScrollBar::handle:vertical { background: #B0C4DE; border-radius: 4px; }
        """)

        widget = QWidget()
        widget.setStyleSheet("background: #F0F4FA;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 16, 20, 20)
        layout.setSpacing(16)

        # ── STAT CARDS ────────────────────────────────────────────
        today_rev = stat.get_today_revenue()
        week_rev = stat.get_week_revenue()
        month_rev = stat.get_month_revenue()
        pred_rev = stat.moving_average_prediction()

        def fmt_money(v):
            v = int(v)
            if v == 0:
                return "0đ"
            return f"{v:,}đ"

        # So sánh hôm nay vs TB ngày trong tuần
        avg_day = week_rev / 7 if week_rev else 0
        if avg_day > 0:
            diff_pct = ((today_rev - avg_day) / avg_day) * 100
            trend_today = f"{'▲' if diff_pct >= 0 else '▼'} {abs(diff_pct):.0f}% so với TB tuần"
            trend_color_today = "#2E7D32" if diff_pct >= 0 else "#E53935"
        else:
            trend_today = "Chưa có dữ liệu so sánh"
            trend_color_today = "#888"

        # Lấy doanh thu tuần trước để so sánh
        from datetime import datetime, timedelta
        last_week_start = datetime.now().date() - timedelta(days=14)
        last_week_end = datetime.now().date() - timedelta(days=7)
        from models.order import Order, OrderStatus
        from models.payment import Payment
        from sqlalchemy import func
        last_week_rev = self.session.query(
            func.sum(Payment.total_amount)
        ).join(Order, Order.id == Payment.order_id).filter(
            Order.status == OrderStatus.PAID,
            func.date(Order.created_at) >= last_week_start,
            func.date(Order.created_at) < last_week_end
        ).scalar() or 0

        if last_week_rev > 0:
            diff_week = ((week_rev - last_week_rev) / last_week_rev) * 100
            trend_week = f"{'▲' if diff_week >= 0 else '▼'} {abs(diff_week):.0f}% so với tuần trước"
            trend_color_week = "#2E7D32" if diff_week >= 0 else "#E53935"
        else:
            trend_week = "Chưa có dữ liệu tuần trước"
            trend_color_week = "#888"

        cards_widget = QWidget()
        cards_widget.setStyleSheet("background: transparent;")
        cards_row = QHBoxLayout(cards_widget)
        cards_row.setContentsMargins(0, 0, 0, 0)
        cards_row.setSpacing(14)

        card_data = [
            {
                "icon": "📅",
                "label": "Hôm nay",
                "value": fmt_money(today_rev),
                "trend": trend_today,
                "trend_color": trend_color_today,
                "color": "#2E7D32",
                "bg": "#F1F8E9",
            },
            {
                "icon": "7️⃣",
                "label": "Tuần này",
                "value": fmt_money(week_rev),
                "trend": trend_week,
                "trend_color": trend_color_week,
                "color": "#1565C0",
                "bg": "#E3F2FD",
            },
            {
                "icon": "📆",
                "label": "Tháng này",
                "value": fmt_money(month_rev),
                "trend": f"{datetime.now().strftime('%m/%Y')}",
                "trend_color": "#888",
                "color": "#6A1B9A",
                "bg": "#F3E5F5",
            },
            {
                "icon": "🎯",
                "label": "Dự đoán ngày mai",
                "value": fmt_money(pred_rev),
                "trend": "Moving Average 7 ngày",
                "trend_color": "#888",
                "color": "#E65100",
                "bg": "#FFF3E0",
            },
        ]

        for cd in card_data:
            card = QWidget()
            card.setMinimumHeight(130)
            card.setStyleSheet(f"""
                QWidget {{
                    background: white;
                    border-radius: 14px;
                    border-top: 5px solid {cd['color']};
                }}
            """)
            cl = QVBoxLayout(card)
            cl.setContentsMargins(18, 14, 18, 14)
            cl.setSpacing(6)

            # Icon + label row
            top_row = QHBoxLayout()
            top_row.setSpacing(8)

            icon_badge = QLabel(cd["icon"])
            icon_badge.setFixedSize(36, 36)
            icon_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_badge.setStyleSheet(f"""
                background: {cd['bg']};
                border-radius: 10px;
                font-size: 18px;
            """)

            lbl_label = QLabel(cd["label"])
            lbl_label.setStyleSheet(
                "color: #78909C; font-size: 12px; font-weight: bold; border: none;"
            )

            top_row.addWidget(icon_badge)
            top_row.addWidget(lbl_label, 1)
            cl.addLayout(top_row)

            # Value
            lbl_val = QLabel(cd["value"])
            lbl_val.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
            lbl_val.setStyleSheet(f"color: {cd['color']}; border: none;")
            cl.addWidget(lbl_val)

            # Trend / sub
            lbl_trend = QLabel(cd["trend"])
            lbl_trend.setStyleSheet(
                f"color: {cd['trend_color']}; font-size: 11px; border: none;"
            )
            cl.addWidget(lbl_trend)

            cards_row.addWidget(card)

        layout.addWidget(cards_widget)

        # ── REVENUE BAR CHART 7 NGÀY ──────────────────────────────
        rev7_card = QWidget()
        rev7_card.setStyleSheet("background: white; border-radius: 12px;")
        rev7_layout = QVBoxLayout(rev7_card)
        rev7_layout.setContentsMargins(16, 14, 16, 14)
        rev7_layout.setSpacing(8)

        lbl_r7 = QLabel("Doanh thu 7 ngày gần nhất")
        lbl_r7.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_r7.setStyleSheet("color: #1E2D3D;")
        rev7_layout.addWidget(lbl_r7)

        data7 = stat.get_revenue_by_day(days=7)
        fig7 = Figure(figsize=(8, 2.8), facecolor='white')
        ax7 = fig7.add_subplot(111)
        ax7.set_facecolor('white')

        if data7:
            dates7, vals7 = zip(*data7)
            bars = ax7.bar(range(len(dates7)),
                           [v / 1_000 for v in vals7],
                           color='#90CAF9', width=0.55, zorder=3)
            # Giá trị trên cột
            for bar, val in zip(bars, vals7):
                if val > 0:
                    ax7.text(bar.get_x() + bar.get_width() / 2,
                             bar.get_height() + max(vals7) * 0.01,
                             f"{int(val / 1000)}k",
                             ha='center', va='bottom', fontsize=7, color='#1565C0')
            ax7.set_xticks(range(len(dates7)))
            ax7.set_xticklabels(dates7, fontsize=9)
        ax7.set_ylabel("Nghìn ₫", fontsize=9)
        ax7.spines['top'].set_visible(False)
        ax7.spines['right'].set_visible(False)
        ax7.grid(axis='y', alpha=0.3, zorder=0)
        ax7.tick_params(axis='both', labelsize=9)
        fig7.tight_layout(pad=0.5)

        canvas7 = FigureCanvas(fig7)
        canvas7.setMinimumHeight(220)
        rev7_layout.addWidget(canvas7)
        layout.addWidget(rev7_card)

        # ── BOTTOM ROW: PIE + TOP PRODUCTS ───────────────────────
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(12)

        # PIE CHART
        pie_card = QWidget()
        pie_card.setStyleSheet("background: white; border-radius: 12px;")
        pie_layout = QVBoxLayout(pie_card)
        pie_layout.setContentsMargins(16, 14, 16, 14)
        pie_layout.setSpacing(8)

        lbl_pie = QLabel("Tỷ trọng danh mục")
        lbl_pie.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_pie.setStyleSheet("color: #1E2D3D;")
        pie_layout.addWidget(lbl_pie)

        pie_data = stat.get_revenue_by_category()
        fig_pie = Figure(figsize=(4, 3.5), facecolor='white')
        ax_pie = fig_pie.add_subplot(111)
        ax_pie.set_facecolor('white')

        if pie_data:
            labels_p = [d[0] for d in pie_data]
            vals_p = [d[1] for d in pie_data]
            colors_p = ['#1565C0', '#2E7D32', '#E65100', '#6A1B9A',
                        '#C62828', '#00838F', '#F57F17', '#4527A0']
            wedges, _, autotexts = ax_pie.pie(
                vals_p, labels=None,
                colors=colors_p[:len(vals_p)],
                autopct='%1.0f%%', pctdistance=0.75,
                startangle=90,
                wedgeprops=dict(width=0.6)
            )
            for t in autotexts:
                t.set_fontsize(8)
                t.set_color('white')
            ax_pie.legend(wedges, labels_p,
                          loc="lower center", ncol=2,
                          fontsize=7, frameon=False,
                          bbox_to_anchor=(0.5, -0.18))
        else:
            ax_pie.text(0.5, 0.5, "Chưa có dữ liệu",
                        ha='center', va='center',
                        transform=ax_pie.transAxes,
                        color='#888', fontsize=10)

        fig_pie.tight_layout(pad=0.3)
        canvas_pie = FigureCanvas(fig_pie)
        canvas_pie.setMinimumHeight(280)
        pie_layout.addWidget(canvas_pie)
        bottom_row.addWidget(pie_card, 2)

        # TOP PRODUCTS với progress bar
        top_card = QWidget()
        top_card.setStyleSheet("background: white; border-radius: 12px;")
        top_layout = QVBoxLayout(top_card)
        top_layout.setContentsMargins(16, 14, 16, 14)
        top_layout.setSpacing(6)

        # Header + tab
        top_header = QHBoxLayout()
        lbl_top_title = QLabel("Top món bán chạy")
        lbl_top_title.setFont(QFont("Segoe UI", 13, QFont.Weight.Bold))
        lbl_top_title.setStyleSheet("color: #1E2D3D;")
        top_header.addWidget(lbl_top_title)
        top_header.addStretch()

        self.report_top_mode = "revenue"
        self.report_top_btns = {}
        self.report_top_layout = top_layout

        for mode, label in [("revenue", "Doanh thu"), ("qty", "Số lượng")]:
            btn = QPushButton(label)
            btn.setFixedHeight(28)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, m=mode: self._switch_report_top(m)
            )
            self.report_top_btns[mode] = btn
            top_header.addWidget(btn)

        top_layout.addLayout(top_header)

        # Container để load lại
        self.report_top_container = QVBoxLayout()
        self.report_top_container.setSpacing(4)
        top_layout.addLayout(self.report_top_container)
        top_layout.addStretch()

        bottom_row.addWidget(top_card, 3)
        layout.addLayout(bottom_row)

        # Load lần đầu
        self._load_report_top("revenue")
        self._update_report_top_style("revenue")

        scroll.setWidget(widget)
        outer_layout.addWidget(scroll)
        return outer

    def _switch_report_top(self, mode: str):
        self.report_top_mode = mode
        self._load_report_top(mode)
        self._update_report_top_style(mode)

    def _update_report_top_style(self, active: str):
        for mode, btn in self.report_top_btns.items():
            if mode == active:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #1565C0; color: white;
                        border: none; border-radius: 14px;
                        font-size: 11px; font-weight: bold;
                        padding: 0 12px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #F0F4FA; color: #555;
                        border: none; border-radius: 14px;
                        font-size: 11px; padding: 0 12px;
                    }
                    QPushButton:hover { background: #E3F2FD; }
                """)

    def _load_report_top(self, mode: str):
        from services.statistic_service import StatisticService
        stat = StatisticService(self.session)

        # Xóa cũ
        while self.report_top_container.count():
            item = self.report_top_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        products = stat.get_top_products(limit=8)
        if not products:
            return

        if mode == "revenue":
            products.sort(key=lambda x: x[2], reverse=True)
            max_val = products[0][2] if products else 1
        else:
            products.sort(key=lambda x: x[1], reverse=True)
            max_val = products[0][1] if products else 1

        rank_colors = [
            "#1565C0", "#2E7D32", "#E65100", "#6A1B9A",
            "#C62828", "#00838F", "#F57F17", "#455A64"
        ]

        for idx, (name, qty, revenue) in enumerate(products):
            row_w = QWidget()
            row_w.setStyleSheet("background: transparent;")
            row_l = QVBoxLayout(row_w)
            row_l.setContentsMargins(4, 4, 4, 2)
            row_l.setSpacing(3)

            # Tên + giá trị
            info_row = QHBoxLayout()
            info_row.setSpacing(8)

            lbl_rank = QLabel(str(idx + 1))
            lbl_rank.setFixedSize(20, 20)
            lbl_rank.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_rank.setStyleSheet(f"""
                background: {rank_colors[idx % len(rank_colors)]};
                color: white; border-radius: 10px;
                font-size: 10px; font-weight: bold;
            """)

            lbl_name = QLabel(name)
            lbl_name.setStyleSheet("color: #1E2D3D; font-size: 12px; font-weight: 600;")

            val = revenue if mode == "revenue" else qty
            val_str = f"{revenue:,}₫" if mode == "revenue" else f"{qty} ly"
            lbl_val = QLabel(val_str)
            lbl_val.setStyleSheet(f"color: {rank_colors[idx % len(rank_colors)]}; font-size: 12px; font-weight: bold;")
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignRight)

            info_row.addWidget(lbl_rank)
            info_row.addWidget(lbl_name, 1)
            info_row.addWidget(lbl_val)
            row_l.addLayout(info_row)

            # Progress bar
            bar_bg = QWidget()
            bar_bg.setFixedHeight(5)
            bar_bg.setStyleSheet("background: #EEF2F8; border-radius: 2px;")
            bar_bg_l = QHBoxLayout(bar_bg)
            bar_bg_l.setContentsMargins(0, 0, 0, 0)
            bar_bg_l.setSpacing(0)

            pct = val / max_val if max_val > 0 else 0
            bar_fill = QWidget()
            bar_fill.setFixedHeight(5)
            bar_fill.setStyleSheet(f"""
                background: {rank_colors[idx % len(rank_colors)]};
                border-radius: 2px;
            """)
            bar_fill.setFixedWidth(int(pct * 300))

            bar_bg_l.addWidget(bar_fill)
            bar_bg_l.addStretch()
            row_l.addWidget(bar_bg)

            self.report_top_container.addWidget(row_w)
    # ── TAB 4: SETTINGS ───────────────────────────────────────
    def _build_settings(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background: #F0F4FA;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        card = QWidget()
        card.setStyleSheet("background: white; border-radius: 14px;")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(12)

        lbl = QLabel("⚙️  Cấu hình hệ thống")
        lbl.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl.setStyleSheet("color: #1E2D3D;")
        card_layout.addWidget(lbl)

        for label, value in [
            ("Tên quán:", "Cafe POS"),
            ("Phiên bản:", "1.0.0"),
            ("Giảm giá nhân viên:", "20%"),
            ("Số bàn:", "40"),
        ]:
            row = QHBoxLayout()
            lbl_key = QLabel(label)
            lbl_key.setFixedWidth(180)
            lbl_key.setStyleSheet("color: #888; font-size: 13px;")
            lbl_val = QLabel(value)
            lbl_val.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold;"
            )
            row.addWidget(lbl_key)
            row.addWidget(lbl_val)
            row.addStretch()
            card_layout.addLayout(row)

        layout.addWidget(card)
        return widget

    # ── TAB 5: POS SUPPORT ────────────────────────────────────
    def _build_pos_support(self) -> QWidget:
        from ui.screens.pos_screen import PosScreen
        return PosScreen(self.user)

    # ── LOGOUT ────────────────────────────────────────────────
    def _on_logout(self):
        reply = QMessageBox.question(
            self, "Đăng xuất", "Bạn có muốn đăng xuất không?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            from main import restart_to_login
            restart_to_login(self)

    def _on_add_product(self):
        from ui.dialogs.product_edit_dialog import ProductEditDialog
        dialog = ProductEditDialog(session=self.session, parent=self)
        if dialog.exec():
            self._load_products()

    def _on_edit_product(self, product):
        from ui.dialogs.product_edit_dialog import ProductEditDialog
        dialog = ProductEditDialog(
            session=self.session,
            product=product,
            parent=self
        )
        if dialog.exec():
            self._load_products()

    def _show_admin_menu(self):
        from PyQt6.QtWidgets import QMenu, QWidgetAction
        from PyQt6.QtGui import QAction

        menu = QMenu(self)
        menu.setStyleSheet("""
            QMenu {
                background: white;
                border: 1px solid #E0E8F5;
                border-radius: 12px;
                padding: 6px;
                font-size: 13px;
            }
            QMenu::item {
                padding: 10px 20px 10px 12px;
                border-radius: 8px;
                color: #1E2D3D;
                min-width: 220px;
            }
            QMenu::item:selected {
                background: #EBF5FF;
                color: #1565C0;
            }
            QMenu::separator {
                height: 1px;
                background: #EEF2F8;
                margin: 4px 8px;
            }
        """)

        # ── Header ────────────────────────────────────────────────
        header_action = QWidgetAction(menu)
        header_w = QWidget()
        header_w.setStyleSheet("background: #F0F4FA; border-radius: 8px;")
        header_l = QHBoxLayout(header_w)
        header_l.setContentsMargins(12, 10, 12, 10)
        header_l.setSpacing(10)

        avatar = QLabel("👑")
        avatar.setFixedSize(42, 42)
        avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        avatar.setStyleSheet("""
            background: #0D47A1;
            border-radius: 21px;
            font-size: 20px;
        """)

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_name = QLabel(self.user.full_name)
        lbl_name.setStyleSheet("font-weight: bold; font-size: 13px; color: #1E2D3D;")
        lbl_role = QLabel(f"🔴  {self.user.role.value}  —  Toàn quyền hệ thống")
        lbl_role.setStyleSheet("font-size: 11px; color: #888;")
        info.addWidget(lbl_name)
        info.addWidget(lbl_role)

        header_l.addWidget(avatar)
        header_l.addLayout(info)
        header_action.setDefaultWidget(header_w)
        menu.addAction(header_action)
        menu.addSeparator()

        # ── Tài khoản ─────────────────────────────────────────────
        act_info = QAction("👤  Thông tin tài khoản", self)
        act_info.triggered.connect(self._show_account_info)
        menu.addAction(act_info)

        act_pwd = QAction("🔒  Đổi mật khẩu", self)
        act_pwd.triggered.connect(self._show_change_password)
        menu.addAction(act_pwd)

        menu.addSeparator()

        # ── Hệ thống ──────────────────────────────────────────────
        act_sys = QAction("🖥️  Thông tin hệ thống", self)
        act_sys.triggered.connect(self._show_system_info)
        menu.addAction(act_sys)

        act_export = QAction("📤  Xuất báo cáo Excel", self)
        act_export.triggered.connect(self._export_report)
        menu.addAction(act_export)

        menu.addSeparator()

        act_logout = QAction("🚪  Đăng xuất", self)
        act_logout.triggered.connect(self._on_logout)
        menu.addAction(act_logout)

        # Hiện menu tại vị trí nút
        from PyQt6.QtCore import QPoint
        pos = self.admin_menu_btn.mapToGlobal(
            self.admin_menu_btn.rect().bottomRight()
        )
        menu.exec(pos - QPoint(menu.sizeHint().width(), 0))

    def _show_account_info(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout

        d = QDialog(self)
        d.setWindowTitle("Thông tin tài khoản")
        d.setFixedWidth(360)
        d.setStyleSheet("background: white;")

        layout = QVBoxLayout(d)
        layout.setContentsMargins(0, 0, 0, 0)

        header = QWidget()
        header.setFixedHeight(90)
        header.setStyleSheet("background: #0D47A1;")
        h = QVBoxLayout(header)
        h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_av = QLabel("👑")
        lbl_av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_av.setStyleSheet("font-size: 36px;")
        lbl_n = QLabel(self.user.full_name)
        lbl_n.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_n.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
        h.addWidget(lbl_av)
        h.addWidget(lbl_n)
        layout.addWidget(header)

        body = QWidget()
        body.setStyleSheet("background: white;")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(24, 16, 24, 20)
        body_l.setSpacing(12)

        for label, value in [
            ("Tên đăng nhập", self.user.username),
            ("Vai trò", f"👑 {self.user.role.value}"),
            ("Trạng thái", "🟢 Đang hoạt động"),
            ("Quyền hạn", "Toàn quyền hệ thống"),
        ]:
            row = QHBoxLayout()
            lbl_k = QLabel(label + ":")
            lbl_k.setFixedWidth(120)
            lbl_k.setStyleSheet("color: #888; font-size: 13px;")
            lbl_v = QLabel(value)
            lbl_v.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold;"
            )
            row.addWidget(lbl_k)
            row.addWidget(lbl_v, 1)
            body_l.addLayout(row)

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(40)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn_close.clicked.connect(d.accept)
        body_l.addSpacing(8)
        body_l.addWidget(btn_close)

        layout.addWidget(body)
        d.exec()

    def _show_change_password(self):
        import hashlib
        from PyQt6.QtWidgets import QDialog, QVBoxLayout

        d = QDialog(self)
        d.setWindowTitle("Đổi mật khẩu")
        d.setFixedWidth(360)
        d.setStyleSheet("background: white;")

        layout = QVBoxLayout(d)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(12)

        lbl_title = QLabel("🔒  Đổi mật khẩu Admin")
        lbl_title.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_title.setStyleSheet("color: #0D47A1;")
        layout.addWidget(lbl_title)

        inp_style = """
            QLineEdit {
                background: #F5F8FF; border: 1.5px solid #DDEAF8;
                border-radius: 8px; padding: 0 12px;
                height: 40px; font-size: 13px;
            }
            QLineEdit:focus { border: 1.5px solid #1565C0; }
        """

        def make_input(placeholder):
            from PyQt6.QtWidgets import QLineEdit
            inp = QLineEdit()
            inp.setEchoMode(QLineEdit.EchoMode.Password)
            inp.setPlaceholderText(placeholder)
            inp.setStyleSheet(inp_style)
            return inp

        for lbl_text in ["Mật khẩu hiện tại:", "Mật khẩu mới:", "Xác nhận mật khẩu mới:"]:
            lbl = QLabel(lbl_text)
            lbl.setStyleSheet("color: #555; font-size: 12px; font-weight: bold;")
            layout.addWidget(lbl)

        inp_old = make_input("Nhập mật khẩu cũ...")
        inp_new = make_input("Nhập mật khẩu mới...")
        inp_confirm = make_input("Nhập lại mật khẩu mới...")

        layout.addWidget(inp_old)
        layout.addWidget(inp_new)
        layout.addWidget(inp_confirm)

        lbl_err = QLabel("")
        lbl_err.setStyleSheet("""
            color: #E53935; font-size: 12px;
            background: #FFEBEE; border-radius: 6px; padding: 6px;
        """)
        lbl_err.setVisible(False)
        layout.addWidget(lbl_err)

        def on_save():
            old = inp_old.text().strip()
            new = inp_new.text().strip()
            confirm = inp_confirm.text().strip()

            if not old or not new or not confirm:
                lbl_err.setText("⚠  Vui lòng nhập đầy đủ!")
                lbl_err.setVisible(True)
                return
            if self.user.password_hash != hashlib.sha256(old.encode()).hexdigest():
                lbl_err.setText("⚠  Mật khẩu hiện tại không đúng!")
                lbl_err.setVisible(True)
                return
            if new != confirm:
                lbl_err.setText("⚠  Mật khẩu mới không khớp!")
                lbl_err.setVisible(True)
                return
            if len(new) < 6:
                lbl_err.setText("⚠  Mật khẩu phải ít nhất 6 ký tự!")
                lbl_err.setVisible(True)
                return

            self.user.password_hash = hashlib.sha256(new.encode()).hexdigest()
            self.session.commit()
            QMessageBox.information(d, "✅ Thành công", "Đổi mật khẩu thành công!")
            d.accept()

        btn_save = QPushButton("💾  Lưu mật khẩu mới")
        btn_save.setFixedHeight(42)
        btn_save.setStyleSheet("""
            QPushButton {
                background: #0D47A1; color: white;
                border: none; border-radius: 8px;
                font-size: 13px; font-weight: bold;
            }
            QPushButton:hover { background: #1565C0; }
        """)
        btn_save.clicked.connect(on_save)
        layout.addWidget(btn_save)
        d.exec()

    def _show_system_info(self):
        from PyQt6.QtWidgets import QDialog, QVBoxLayout
        from models.order import Order, OrderStatus
        from models.product import Product
        from models.user import User
        from datetime import datetime

        d = QDialog(self)
        d.setWindowTitle("Thông tin hệ thống")
        d.setFixedWidth(400)
        d.setStyleSheet("background: white;")

        layout = QVBoxLayout(d)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        hdr = QWidget()
        hdr.setFixedHeight(70)
        hdr.setStyleSheet("background: #1565C0;")
        hdr_l = QVBoxLayout(hdr)
        hdr_l.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_h = QLabel("🖥️  Thông tin hệ thống")
        lbl_h.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_h.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_h.setStyleSheet("color: white;")
        hdr_l.addWidget(lbl_h)
        layout.addWidget(hdr)

        body = QWidget()
        body.setStyleSheet("background: white;")
        body_l = QVBoxLayout(body)
        body_l.setContentsMargins(24, 16, 24, 20)
        body_l.setSpacing(10)

        # Lấy số liệu
        total_orders = self.session.query(Order).count()
        paid_orders = self.session.query(Order).filter(Order.status == OrderStatus.PAID).count()
        total_products = self.session.query(Product).filter(Product.is_active == True).count()
        total_users = self.session.query(User).filter(User.is_active == True).count()

        from config.settings import DB_CONFIG
        db_info = f"{DB_CONFIG.host}:{DB_CONFIG.port}/{DB_CONFIG.database}"

        info_rows = [
            ("🏷️  Tên ứng dụng", "Cafe POS"),
            ("📦  Phiên bản", "1.0.0"),
            ("🐍  Python", "3.11"),
            ("🗄️  Database", db_info),
            ("📋  Tổng orders", f"{total_orders:,}"),
            ("✅  Đã thanh toán", f"{paid_orders:,}"),
            ("🍹  Sản phẩm", f"{total_products:,}"),
            ("👥  Người dùng", f"{total_users:,}"),
            ("🕐  Thời gian hiện tại", datetime.now().strftime("%d/%m/%Y %H:%M:%S")),
        ]

        for label, value in info_rows:
            card = QWidget()
            card.setStyleSheet("""
                QWidget {
                    background: #F8FAFF;
                    border-radius: 8px;
                    border: 1px solid #E8EEF8;
                }
            """)
            card.setFixedHeight(36)
            row = QHBoxLayout(card)
            row.setContentsMargins(12, 0, 12, 0)
            lbl_k = QLabel(label)
            lbl_k.setStyleSheet("color: #888; font-size: 12px; border: none;")
            lbl_k.setFixedWidth(160)
            lbl_v = QLabel(value)
            lbl_v.setStyleSheet(
                "color: #1E2D3D; font-size: 12px; font-weight: bold; border: none;"
            )
            row.addWidget(lbl_k)
            row.addWidget(lbl_v, 1)
            body_l.addWidget(card)

        btn_close = QPushButton("Đóng")
        btn_close.setFixedHeight(40)
        btn_close.setStyleSheet("""
            QPushButton {
                background: #1565C0; color: white;
                border: none; border-radius: 8px; font-weight: bold;
            }
            QPushButton:hover { background: #1976D2; }
        """)
        btn_close.clicked.connect(d.accept)
        body_l.addSpacing(4)
        body_l.addWidget(btn_close)

        layout.addWidget(body)
        d.exec()

    def _export_report(self):
        from PyQt6.QtWidgets import QFileDialog, QDialog, QVBoxLayout
        from services.statistic_service import StatisticService
        from datetime import datetime

        # Hỏi chọn nơi lưu
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Xuất báo cáo Excel",
            f"BaoCao_CafePOS_{datetime.now().strftime('%d%m%Y')}.csv",
            "CSV Files (*.csv)"
        )
        if not file_path:
            return

        try:
            stat = StatisticService(self.session)
            top_products = stat.get_top_products(limit=50)

            with open(file_path, 'w', encoding='utf-8-sig') as f:
                # Header báo cáo
                f.write(f"BÁO CÁO DOANH THU - CAFE POS\n")
                f.write(f"Xuất lúc:,{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                f.write(f"Doanh thu hôm nay:,{stat.get_today_revenue():,}₫\n")
                f.write(f"Doanh thu tuần:,{stat.get_week_revenue():,}₫\n")
                f.write(f"Doanh thu tháng:,{stat.get_month_revenue():,}₫\n")
                f.write(f"Dự đoán ngày mai:,{stat.moving_average_prediction():,.0f}₫\n")
                f.write("\n")
                f.write("STT,Tên sản phẩm,Số lượng bán,Doanh thu (₫)\n")
                for idx, (name, qty, revenue) in enumerate(top_products, 1):
                    f.write(f"{idx},{name},{qty},{revenue}\n")

            QMessageBox.information(
                self, "✅ Xuất thành công",
                f"Đã xuất báo cáo ra:\n{file_path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "❌ Lỗi", f"Không thể xuất file:\n{str(e)}")