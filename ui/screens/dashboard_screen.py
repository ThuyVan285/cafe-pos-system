# FILE: ui/screens/dashboard_screen.py
# Thêm import ở đầu file
import matplotlib
matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QPushButton, QStackedWidget, QScrollArea,
    QGridLayout, QFrame, QTableWidget, QTableWidgetItem,
    QHeaderView, QLineEdit, QComboBox, QMessageBox,
    QDialog, QFormLayout, QCheckBox
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
                ("⚙️", "Cấu hình",       4),
            ]
        else:  # MANAGER
            menus = [
                ("📊", "Tổng quan",      0),
                ("🍹", "Sản phẩm",       2),
                ("📈", "Báo cáo",        3),
                ("🪑", "Hỗ trợ bán hàng", 5),
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
        hb.setContentsMargins(20, 0, 20, 0)

        self.header_title = QLabel("📊  Tổng quan")
        self.header_title.setFont(
            QFont("Segoe UI", 14, QFont.Weight.Bold)
        )
        self.header_title.setStyleSheet("color: #1E2D3D;")
        hb.addWidget(self.header_title)
        hb.addStretch()

        layout.addWidget(self.header_bar)

        # Stack
        self.stack = QStackedWidget()
        self.stack.addWidget(self._build_overview())    # 0
        self.stack.addWidget(self._build_users())       # 1
        self.stack.addWidget(self._build_products())    # 2
        self.stack.addWidget(self._build_reports())     # 3
        self.stack.addWidget(self._build_settings())    # 4
        self.stack.addWidget(self._build_pos_support()) # 5

        layout.addWidget(self.stack, 1)

        # Chọn tab đầu tiên
        if self.sidebar_btns:
            first_btn = self.sidebar_btns[0][0]
            first_btn.set_active(True)

        return widget

    def _switch_tab(self, index, clicked_btn):
        self.stack.setCurrentIndex(index)
        titles = {
            0: "📊  Tổng quan",
            1: "👥  Quản lý người dùng",
            2: "🍹  Quản lý sản phẩm",
            3: "📈  Báo cáo doanh thu",
            4: "⚙️  Cấu hình hệ thống",
            5: "🪑  Hỗ trợ bán hàng",
        }
        self.header_title.setText(titles.get(index, ""))
        for btn, _ in self.sidebar_btns:
            btn.set_active(btn == clicked_btn)

    # ── TAB 0: OVERVIEW ───────────────────────────────────────
    def _build_overview(self) -> QWidget:
        widget = QWidget()
        widget.setStyleSheet("background: #F0F4FA;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        from services.statistic_service import StatisticService
        from models.order import Order, OrderStatus
        from models.table import TableStatus
        stat = StatisticService(self.session)

        today_rev = stat.get_today_revenue()
        prediction = stat.moving_average_prediction()

        # Số hóa đơn hôm nay
        from datetime import datetime
        today = datetime.now().date()
        all_paid = self.session.query(Order).filter(
            Order.status == OrderStatus.PAID
        ).all()
        today_orders = [o for o in all_paid if o.created_at.date() == today]
        today_count = len(today_orders)

        # Bàn đang dùng
        from models.table import CafeTable
        total_tables = self.session.query(CafeTable).count()
        using_tables = self.session.query(CafeTable).filter(
            CafeTable.status == TableStatus.USING
        ).count()

        # Đơn đang phục vụ
        active_orders = self.session.query(Order).filter(
            Order.status == OrderStatus.ACTIVE
        ).count()

        # ── CARD ROW ──────────────────────────────────────────────
        card_widget = QWidget()
        card_widget.setStyleSheet("""
            background: white;
            border-radius: 14px;
        """)
        card_layout = QGridLayout(card_widget)
        card_layout.setContentsMargins(20, 16, 20, 16)
        card_layout.setSpacing(0)

        def make_card(top_text, main_value, main_color, sub_text=""):
            w = QWidget()
            w.setStyleSheet("border: none; background: transparent;")
            v = QVBoxLayout(w)
            v.setContentsMargins(12, 8, 12, 8)
            v.setSpacing(2)

            lbl_top = QLabel(top_text)
            lbl_top.setStyleSheet("color: #888; font-size: 12px;")

            lbl_main = QLabel(main_value)
            lbl_main.setFont(QFont("Segoe UI", 26, QFont.Weight.Bold))
            lbl_main.setStyleSheet(f"color: {main_color};")

            v.addWidget(lbl_top)
            v.addWidget(lbl_main)

            if sub_text:
                lbl_sub = QLabel(sub_text)
                lbl_sub.setStyleSheet("color: #555; font-size: 13px;")
                v.addWidget(lbl_sub)

            return w

        # Format doanh thu dạng "836 nghìn"
        def fmt_rev(amount):
            if amount >= 1_000_000:
                return f"{amount / 1_000_000:.1f} triệu"
            elif amount >= 1_000:
                return f"{int(amount / 1_000)} nghìn"
            return f"{amount}₫"

        card_layout.addWidget(
            make_card(f"{today_count} hóa đơn", fmt_rev(today_rev), "#1565C0"), 0, 0
        )

        # Separator dọc
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.Shape.VLine)
        sep1.setStyleSheet("color: #EEF2F8;")
        card_layout.addWidget(sep1, 0, 1)

        active_rev = sum(
            o.subtotal for o in self.session.query(Order).filter(
                Order.status == OrderStatus.ACTIVE
            ).all()
        )
        card_layout.addWidget(
            make_card(f"{active_orders} đơn đang phục vụ", fmt_rev(active_rev), "#2E7D32"), 0, 2
        )

        # Separator ngang
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #EEF2F8;")
        card_layout.addWidget(sep2, 1, 0, 1, 3)

        card_layout.addWidget(
            make_card("Bàn đang sử dụng", f"{using_tables} / {total_tables}", "#1E2D3D"), 2, 0
        )
        card_layout.addWidget(sep1, 2, 1)
        card_layout.addWidget(
            make_card("Khách đang phục vụ", str(active_orders), "#1E2D3D"), 2, 2
        )

        layout.addWidget(card_widget)

        # ── BIỂU ĐỒ DOANH THU ────────────────────────────────────
        rev_widget = QWidget()
        rev_widget.setStyleSheet("background: white; border-radius: 14px;")
        rev_layout = QVBoxLayout(rev_widget)
        rev_layout.setContentsMargins(16, 14, 16, 14)
        rev_layout.setSpacing(8)

        # Title + tab
        title_row = QHBoxLayout()
        lbl_rev = QLabel("Doanh thu")
        lbl_rev.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_rev.setStyleSheet("color: #1E2D3D;")
        title_row.addWidget(lbl_rev)
        title_row.addStretch()
        rev_layout.addLayout(title_row)

        # Tab Giờ/Ngày/Thứ
        tab_row = QHBoxLayout()
        tab_row.setSpacing(4)
        self.rev_mode = "hour"
        self.rev_tab_btns = {}

        for mode, label in [("hour", "Giờ"), ("day", "Ngày"), ("weekday", "Thứ")]:
            btn = QPushButton(label)
            btn.setFixedHeight(32)
            btn.setFixedWidth(70)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, m=mode: self._switch_rev_chart(m)
            )
            self.rev_tab_btns[mode] = btn
            tab_row.addWidget(btn)

        tab_row.addStretch()
        rev_layout.addLayout(tab_row)

        # Canvas
        self.rev_fig = Figure(figsize=(6, 2.5), facecolor='white')
        self.rev_canvas = FigureCanvas(self.rev_fig)
        rev_layout.addWidget(self.rev_canvas)
        layout.addWidget(rev_widget)

        # ── BIỂU ĐỒ KHÁCH HÀNG ───────────────────────────────────
        cust_widget = QWidget()
        cust_widget.setStyleSheet("background: white; border-radius: 14px;")
        cust_layout = QVBoxLayout(cust_widget)
        cust_layout.setContentsMargins(16, 14, 16, 14)

        lbl_cust = QLabel("Số lượng khách hàng")
        lbl_cust.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_cust.setStyleSheet("color: #1E2D3D;")
        cust_layout.addWidget(lbl_cust)

        self.cust_fig = Figure(figsize=(6, 2.2), facecolor='white')
        self.cust_canvas = FigureCanvas(self.cust_fig)
        cust_layout.addWidget(self.cust_canvas)
        layout.addWidget(cust_widget)

        # Vẽ chart lần đầu
        self._draw_rev_chart("hour")
        self._draw_cust_chart()
        self._update_rev_tab_style("hour")

        return widget

    def _switch_rev_chart(self, mode: str):
        self.rev_mode = mode
        self._draw_rev_chart(mode)
        self._update_rev_tab_style(mode)

    def _update_rev_tab_style(self, active_mode: str):
        for mode, btn in self.rev_tab_btns.items():
            if mode == active_mode:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #1565C0; color: white;
                        border: none; border-radius: 16px;
                        font-weight: bold; font-size: 12px;
                    }
                """)
                btn.setChecked(True)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #F0F4FA; color: #555;
                        border: none; border-radius: 16px;
                        font-size: 12px;
                    }
                    QPushButton:hover { background: #E3F2FD; }
                """)
                btn.setChecked(False)

    def _draw_rev_chart(self, mode: str):
        from services.statistic_service import StatisticService
        stat = StatisticService(self.session)

        self.rev_fig.clear()
        ax = self.rev_fig.add_subplot(111)
        ax.set_facecolor('white')
        self.rev_fig.patch.set_facecolor('white')

        if mode == "hour":
            data = stat.get_revenue_by_hour()
            labels = [f"{h}:00" for h, _ in data]
            values = [v for _, v in data]
            ax.bar(range(len(labels)), [v / 1000 for v in values],
                   color='#90CAF9', width=0.6)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, fontsize=8, rotation=45)
            ax.set_ylabel("Nghìn ₫", fontsize=9)

        elif mode == "day":
            data = stat.get_revenue_by_day(days=7)
            labels = [d for d, _ in data]
            values = [v for _, v in data]
            ax.bar(range(len(labels)), [v / 1000 for v in values],
                   color='#90CAF9', width=0.6)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, fontsize=8, rotation=45)
            ax.set_ylabel("Nghìn ₫", fontsize=9)

        elif mode == "weekday":
            data = stat.get_revenue_by_weekday()
            labels = [d for d, _ in data]
            values = [v for _, v in data]
            ax.bar(range(len(labels)), [v / 1000 for v in values],
                   color='#90CAF9', width=0.6)
            ax.set_xticks(range(len(labels)))
            ax.set_xticklabels(labels, fontsize=8)
            ax.set_ylabel("Nghìn ₫", fontsize=9)

        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='both', labelsize=8)
        self.rev_fig.tight_layout()
        self.rev_canvas.draw()

    def _draw_cust_chart(self):
        from services.statistic_service import StatisticService
        stat = StatisticService(self.session)

        self.cust_fig.clear()
        ax = self.cust_fig.add_subplot(111)
        ax.set_facecolor('white')
        self.cust_fig.patch.set_facecolor('white')

        data = stat.get_customers_by_hour()
        hours = list(range(24))
        values = [0] * 24
        for h, count in data:
            values[h] = count

        ax.plot(hours, values, color='#5B9BD5', linewidth=2)
        ax.fill_between(hours, values, alpha=0.15, color='#5B9BD5')
        ax.set_xticks([0, 5, 10, 15, 20, 23])
        ax.set_xticklabels(
            ["0:00", "5:00", "10:00", "15:00", "20:00", "23:00"],
            fontsize=8
        )
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.tick_params(axis='both', labelsize=8)
        self.cust_fig.tight_layout()
        self.cust_canvas.draw()

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
        widget = QWidget()
        widget.setStyleSheet("background: #F0F4FA;")
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(14)

        from services.statistic_service import StatisticService
        stat = StatisticService(self.session)

        # Cards doanh thu
        cards = QGridLayout()
        cards.setSpacing(14)
        today = stat.get_today_revenue()
        week = stat.get_week_revenue()
        month = stat.get_month_revenue()
        pred = stat.moving_average_prediction()

        for idx, (icon, title, value, color) in enumerate([
            ("📅", "Hôm nay", f"{today:,}₫", "#2E7D32"),
            ("📆", "Tuần này", f"{week:,}₫", "#1565C0"),
            ("🗓", "Tháng này", f"{month:,}₫", "#6A1B9A"),
            ("🤖", "Dự đoán", f"{pred:,.0f}₫", "#E65100"),
        ]):
            cards.addWidget(StatCard(icon, title, value, color), 0, idx)
        layout.addLayout(cards)

        # ── HÀNG BÁN CHẠY ─────────────────────────────────────────
        top_widget = QWidget()
        top_widget.setStyleSheet("background: white; border-radius: 14px;")
        top_layout = QVBoxLayout(top_widget)
        top_layout.setContentsMargins(16, 14, 16, 14)
        top_layout.setSpacing(10)

        # Title + tab
        title_row = QHBoxLayout()
        lbl_top = QLabel("Hàng bán chạy")
        lbl_top.setFont(QFont("Segoe UI", 14, QFont.Weight.Bold))
        lbl_top.setStyleSheet("color: #1E2D3D;")
        title_row.addWidget(lbl_top)
        title_row.addStretch()
        top_layout.addLayout(title_row)

        # Tab doanh thu / số lượng
        tab_row = QHBoxLayout()
        tab_row.setSpacing(4)
        self.top_mode = "revenue"
        self.top_tab_btns = {}

        for mode, label in [("revenue", "Theo doanh thu"), ("qty", "Theo số lượng")]:
            btn = QPushButton(label)
            btn.setFixedHeight(34)
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(
                lambda checked, m=mode: self._switch_top_mode(m)
            )
            self.top_tab_btns[mode] = btn
            tab_row.addWidget(btn)

        tab_row.addStretch()
        top_layout.addLayout(tab_row)

        # List sản phẩm
        self.top_list_layout = QVBoxLayout()
        self.top_list_layout.setSpacing(0)
        top_layout.addLayout(self.top_list_layout)

        layout.addWidget(top_widget, 1)

        self._load_top_products("revenue")
        self._update_top_tab_style("revenue")

        return widget

    def _switch_top_mode(self, mode: str):
        self.top_mode = mode
        self._load_top_products(mode)
        self._update_top_tab_style(mode)

    def _update_top_tab_style(self, active: str):
        for mode, btn in self.top_tab_btns.items():
            if mode == active:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #1565C0; color: white;
                        border: none; border-radius: 17px;
                        font-weight: bold; font-size: 12px;
                        padding: 0 16px;
                    }
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: #F0F4FA; color: #555;
                        border: none; border-radius: 17px;
                        font-size: 12px; padding: 0 16px;
                    }
                    QPushButton:hover { background: #E3F2FD; }
                """)

    def _load_top_products(self, mode: str):
        from services.statistic_service import StatisticService
        stat = StatisticService(self.session)

        # Xóa list cũ
        while self.top_list_layout.count():
            item = self.top_list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        products = stat.get_top_products(limit=10)

        # Sắp xếp theo mode
        if mode == "revenue":
            products.sort(key=lambda x: x[2], reverse=True)
        else:
            products.sort(key=lambda x: x[1], reverse=True)

        for idx, (name, qty, revenue) in enumerate(products):
            row_widget = QWidget()
            row_widget.setStyleSheet("""
                QWidget {
                    border-bottom: 1px solid #EEF2F8;
                    background: transparent;
                }
            """)
            row = QHBoxLayout(row_widget)
            row.setContentsMargins(4, 10, 4, 10)
            row.setSpacing(12)

            # Icon
            icon_lbl = QLabel("☕")
            icon_lbl.setFixedSize(40, 40)
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_lbl.setStyleSheet("""
                background: #E3F2FD;
                border-radius: 8px;
                font-size: 18px;
            """)

            # Tên
            lbl_name = QLabel(name)
            lbl_name.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold; border: none;"
            )

            # Doanh thu + số lượng
            right = QVBoxLayout()
            right.setSpacing(2)
            lbl_rev = QLabel(f"{revenue:,}")
            lbl_rev.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_rev.setStyleSheet(
                "color: #1E2D3D; font-size: 13px; font-weight: bold; border: none;"
            )
            lbl_qty = QLabel(f"Đã bán {qty}")
            lbl_qty.setAlignment(Qt.AlignmentFlag.AlignRight)
            lbl_qty.setStyleSheet("color: #888; font-size: 11px; border: none;")
            right.addWidget(lbl_rev)
            right.addWidget(lbl_qty)

            row.addWidget(icon_lbl)
            row.addWidget(lbl_name, 1)
            row.addLayout(right)

            self.top_list_layout.addWidget(row_widget)

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