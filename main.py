import sys

# تعيين الترميز إلى UTF-8
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QListWidget, QDialog, QGridLayout, QScrollArea, QFrame, QHBoxLayout, QTableWidget, QTableWidgetItem, QHeaderView, QSpacerItem, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QPainterPath, QColor, QFont
import pyodbc
import os
from datetime import datetime

class ProfileDialog(QDialog):
    def __init__(self, record_data, parent=None):
        super().__init__(parent)
        self.database_path = r'D:\Data1\sh1.accdb'  # مسار قاعدة البيانات
        self.images_path = r'D:\Data1\PIC'  # مسار مجلد الصور
        self.setFont(QFont('Tahoma'))  # تغيير نوع الخط
        self.setWindowTitle('الملف الشخصي')
        self.setGeometry(200, 200, 400, 600)
        
        # الحصول على أسماء الأعمدة العربية من النافذة الرئيسية
        self.column_names = parent.column_names if parent else {}
        
        # إنشاء تخطيط رئيسي
        main_layout = QVBoxLayout()
        main_layout.setSpacing(5)  # تقليل التباعد العام
        main_layout.setContentsMargins(10, 10, 10, 10)  # تقليل الهوامش
        
        # إضافة زر العودة
        back_button = QPushButton("العودة")
        back_button.setStyleSheet('''
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: 5px;
                font-size: 14px;
                margin-bottom: 5px;  # تقليل المسافة أسفل الزر
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')
        back_button.clicked.connect(self.close)
        
        # إطار الصورة
        image_frame = QFrame()
        image_frame.setStyleSheet('''
            QFrame {
                background-color: #f8f9fa;
                border-radius: 15px;
                padding: 5px;  # تقليل الحشو الداخلي
                margin-bottom: 5px;  # تقليل المسافة أسفل الإطار
            }
        ''')
        image_layout = QVBoxLayout()
        image_layout.setAlignment(Qt.AlignCenter)
        
        # إضافة الصورة
        image_label = QLabel()
        pixmap = self.load_image(record_data.get('ID', ''))
        if 'Photo' in record_data:
            try:
                pixmap.loadFromData(record_data['Photo'])
            except:
                pass
        
        # تحويل الصورة إلى شكل دائري
        size = 120
        rounded_pixmap = QPixmap(size, size)
        rounded_pixmap.fill(Qt.transparent)
        
        scaled_pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        
        painter = QPainter(rounded_pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        path = QPainterPath()
        path.addEllipse(0, 0, size, size)
        painter.setClipPath(path)
        painter.drawPixmap(0, 0, scaled_pixmap)
        painter.end()
        
        image_label.setPixmap(rounded_pixmap)
        image_label.setAlignment(Qt.AlignCenter)
        image_layout.addWidget(image_label)
        
        # إضافة مسافة لتحريك الدائرة إلى اليمين
        spacer = QSpacerItem(20, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)
        image_layout.addItem(spacer)  # إضافة المسافة قبل الدائرة
        
        # إضافة دائرة صغيرة لتوضيح حالة الاتصال
        status_label = QLabel()  # إنشاء QLabel للدائرة
        if record_data.get('continue') == 'مستمر':  # تحقق من حالة الاتصال
            status_label.setStyleSheet('background-color: green; border-radius: 10px;')  # دائرة خضراء
        else:
            status_label.setStyleSheet('background-color: red; border-radius: 10px;')  # دائرة حمراء
        status_label.setFixedSize(20, 20)  # تعيين حجم الدائرة
        image_layout.addWidget(status_label)  # إضافة الدائرة إلى التخطيط
        
        image_frame.setLayout(image_layout)
        
        # إطار المعلومات
        info_frame = QFrame()
        info_frame.setStyleSheet('''
            QFrame {
                background-color: #ffffff;
                border-radius: 15px;
                padding: 5px;  # تقليل الحشو الداخلي
            }
        ''')
        
        # إنشاء جدول للمعلومات
        table = QTableWidget()
        table.setColumnCount(2)
        table.setStyleSheet('''
            QTableWidget {
                border: none;
                background-color: transparent;
                gridline-color: #e0e0e0;
            }
            QTableWidget::item {
                padding: 5px;
                border-bottom: 1px solid #e0e0e0;
                font-size: 12px;
                text-align: left;
            }
            QTableWidget::item:selected {
                color: #3498db;  /* لون أزرق للنص عند تحديد الخلية */
            }
        ''')
        
        # إخفاء رأس الجدول
        table.horizontalHeader().setVisible(False)
        table.verticalHeader().setVisible(False)
        
        # إضافة البيانات للجدول
        filtered_data = [(k, v) for k, v in record_data.items() if k != 'Photo']
        table.setRowCount(len(filtered_data))
        print(f'عدد السجلات: {len(filtered_data)}')  # رسالة تسجيل عدد السجلات
        
        for i, (key, value) in enumerate(filtered_data):
            # استخدام الاسم العربي إذا كان متوفراً
            arabic_key = self.column_names.get(key, key)
            if key == 'Phone':  # إذا كان العمود هو رقم الهاتف
                if isinstance(value, str) and value.isdigit() and len(value) >= 7:  # تحقق من أن القيمة رقمية وطولها مناسب
                    phone_label = QLabel(f'<a href="tel:{value}">{value}</a>')
                    phone_label.setTextInteractionFlags(Qt.TextBrowserInteraction)  # السماح بالتفاعل مع النص
                    phone_label.setOpenExternalLinks(True)  # السماح بفتح الروابط
                    phone_label.setStyleSheet('font-size: 16px; text-align: right;')  # تكبير حجم الخط ومحاذاة النص لليمين
                    table.setCellWidget(i, 1, phone_label)  # تعيين QLabel في الخلية المناسبة
                else:
                    phone_label = QLabel('رقم هاتف غير صالح')  # في حال كانت القيمة غير صالحة
                    phone_label.setStyleSheet('font-size: 16px; text-align: right;')  # تكبير حجم الخط ومحاذاة النص لليمين
                    table.setCellWidget(i, 1, phone_label)  # تعيين QLabel في الخلية المناسبة
            else:
                key_item = QTableWidgetItem(str(arabic_key))
                value_item = QTableWidgetItem(str(value))
                
                # تعيين محاذاة النص إلى اليسار
                key_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                value_item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)
                
                # تنسيق العناوين
                key_item.setBackground(QColor('#e8f5e9'))  # لون أخضر فاتح
                key_item.setFont(QFont('Arial', 12, QFont.Bold))  # تعيين خط يدعم الكتابة العربية
                value_item.setFont(QFont('Arial', 12))  # تعيين خط يدعم الكتابة العربية
                key_item.setFlags(key_item.flags() & ~Qt.ItemIsEditable)  # جعل العناوين غير قابلة للتحرير
                
                table.setItem(i, 0, key_item)
                table.setItem(i, 1, value_item)
        
        # تعديل حجم الأعمدة
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        
        # تعطيل إمكانية تحديد النص في الجدول
        table.setSelectionBehavior(QTableWidget.SelectRows)  # تحديد الصفوف
        table.setEditTriggers(QTableWidget.NoEditTriggers)  # تعطيل التحرير
        
        # إضافة الجدول إلى إطار المعلومات
        info_layout = QVBoxLayout()
        info_layout.addWidget(table)
        info_frame.setLayout(info_layout)
        
        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidget(info_frame)
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet('''
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                border: none;
                background-color: #f1f1f1;
                width: 8px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                background-color: #888;
                border-radius: 4px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #555;
            }
        ''')
        
        # إضافة كل شيء إلى التخطيط الرئيسي
        main_layout.addWidget(back_button)
        main_layout.addWidget(image_frame)
        main_layout.addWidget(scroll_area)
        
        phone_number = record_data.get('Phone', '')
        if isinstance(phone_number, str) and phone_number.isdigit():  # التأكد من أن القيمة رقمية
            phone_label = QLabel(f'<a href="tel:{phone_number}">{phone_number}</a>')
            phone_label.setTextInteractionFlags(Qt.TextBrowserInteraction)  # السماح بالتفاعل مع النص
            phone_label.setOpenExternalLinks(True)  # السماح بفتح الروابط
            phone_label.setTextFormat(Qt.RichText)  # السماح بعرض النص بتنسيق HTML
        else:
            phone_label = QLabel('الهاتف: غير متوفر')  # في حال لم تكن القيمة رقمية
        main_layout.addWidget(phone_label)
        
        self.setLayout(main_layout)
        
        self.setStyleSheet('''
            QDialog {
                background-color: #ffffff;
            }
        ''')

    def load_image(self, id_value):
        """تحميل الصورة بناءً على قيمة ID"""
        image_path = os.path.join(self.images_path, f'{id_value}.jpg')  # تعديل مسار الصورة
        default_image_path = os.path.join(self.images_path, 'default.jpg')  # تعديل مسار الصورة الافتراضية

        if os.path.exists(image_path):
            print(f'تم تحميل الصورة بنجاح من: {image_path}')  # رسالة تسجيل
            return QPixmap(image_path)
        else:
            print(f'الصورة غير موجودة، تم تحميل الصورة الافتراضية من: {default_image_path}')  # رسالة تسجيل
            return QPixmap(default_image_path)

class DatabaseApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setFont(QFont('Tahoma'))  # تغيير نوع الخط
        self.setWindowTitle('تطبيق قاعدة البيانات')
        self.setGeometry(100, 100, 400, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        self.full_records = {}
        self.column_names = {}  # قاموس لتخزين أسماء الأعمدة العربية
        
        # تعيين أسماء الأعمدة العربية
        self.load_arabic_column_names()
        
        # إنشاء الواجهة الرئيسية
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignRight)
        main_widget.setLayout(layout)
        
        # عنوان التطبيق
        title_label = QLabel('تطبيق قاعدة البيانات')
        title_label.setStyleSheet('font-size: 24px; margin: 10px;')
        title_label.setAlignment(Qt.AlignRight)
        
        # حقل البحث
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText('ابحث عن اسم...')
        self.search_input.setStyleSheet('''
            QLineEdit {
                padding: 10px;
                font-size: 18px;
                border: 1px solid #ccc;
                border-radius: 5px;
            }
        ''')
        self.search_input.setAlignment(Qt.AlignRight)
        
        # زر البحث
        search_button = QPushButton('بحث')
        search_button.setStyleSheet('''
            QPushButton {
                padding: 10px;
                font-size: 18px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        ''')
        search_button.clicked.connect(self.search_database)
        
        # عنوان النتائج
        results_label = QLabel('النتائج:')
        results_label.setStyleSheet('font-size: 18px; margin-top: 10px;')
        results_label.setAlignment(Qt.AlignRight)
        
        # قائمة النتائج
        self.results_list = QListWidget()
        self.results_list.setStyleSheet('''
            QListWidget {
                font-size: 16px;
                padding: 5px;
                border: 1px solid #ccc;
                border-radius: 5px;
                text-align: right;
            }
            QListWidget::item {
                padding: 5px;
                text-align: right;
            }
            QListWidget::item:hover {
                background-color: #e0e0e0;
            }
        ''')
        self.results_list.itemClicked.connect(self.show_profile)
        
        # إضافة العناصر إلى التخطيط
        layout.addWidget(title_label)
        layout.addWidget(self.search_input)
        layout.addWidget(search_button)
        layout.addWidget(results_label)
        layout.addWidget(self.results_list)
        
        print('بدء تحميل البيانات...')  # رسالة تسجيل
        self.load_data()
    
    def connect_to_database(self):
        try:
            conn_str = (
                r'DRIVER={Microsoft Access Driver (*.mdb, *.accdb)};'
                r'DBQ=' + r'D:\Data1\sh1.accdb' + ';'
            )
            conn = pyodbc.connect(conn_str)
            print('تم الاتصال بقاعدة البيانات بنجاح.')  # رسالة تسجيل
            return conn
        except Exception as e:
            print(f"خطأ في الاتصال بقاعدة البيانات: {e}")
            return None
    
    def load_arabic_column_names(self):
        """تعيين أسماء الأعمدة العربية"""
        self.setFont(QFont('Verdana'))  # تغيير نوع الخط إلى Verdana عند تحميل أسماء الأعمدة
        # تعيين الأسماء العربية للأعمدة
        self.column_names = {
            'ID': 'المعرف',
            'NoIhsaay': 'الرقم',
            'Rank': 'الرتبة',
            'Name_1': 'الاسم',
            'Company_Now': 'الوحدة',
            'Mansb': 'المنصب',
            'Phone': 'الهاتف',
            'Mobashara': 'المباشرة',
            'continue': 'الحالة'
        }
    
    def load_data(self):
        print('بدء تحميل البيانات...')  # رسالة تسجيل
        conn = self.connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM main")
                
                columns = [column[0] for column in cursor.description]
                self.full_records.clear()
                self.results_list.clear()
                
                for row in cursor.fetchall():
                    record_data = dict(zip(columns, row))
                    mobashara_date = record_data.get('Mobashara', '')
                    if isinstance(mobashara_date, str):
                        mobashara_date = mobashara_date.split(' ')[0]  # استخراج التاريخ فقط
                    elif isinstance(mobashara_date, datetime):
                        mobashara_date = mobashara_date.strftime('%Y-%m-%d')  # تنسيق التاريخ
                    record_data['Mobashara'] = mobashara_date  # تحديث القيمة في record_data
                    name = str(record_data.get('Name_1', ''))  
                    self.full_records[name] = record_data  
                    self.results_list.addItem(name)  
                
                cursor.close()
                conn.close()
                print(f'تم تحميل {len(self.full_records)} سجل بنجاح.')  # رسالة تسجيل عدد السجلات المحملة
            except Exception as e:
                print(f"Error loading data: {e}")
    
    def search_database(self):
        search_term = self.search_input.text().strip()
        conn = self.connect_to_database()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT * FROM main WHERE Name_1 LIKE ?",
                    (f"%{search_term}%",)
                )
                
                columns = [column[0] for column in cursor.description]
                self.full_records.clear()
                self.results_list.clear()
                
                for row in cursor.fetchall():
                    record_data = dict(zip(columns, row))
                    mobashara_date = record_data.get('Mobashara', '')
                    if isinstance(mobashara_date, str):
                        mobashara_date = mobashara_date.split(' ')[0]  # استخراج التاريخ فقط
                    elif isinstance(mobashara_date, datetime):
                        mobashara_date = mobashara_date.strftime('%Y-%m-%d')  # تنسيق التاريخ
                    record_data['Mobashara'] = mobashara_date  # تحديث القيمة في record_data
                    name = str(record_data.get('Name_1', ''))  
                    self.full_records[name] = record_data  
                    self.results_list.addItem(name)  
                
                cursor.close()
                conn.close()
                print(f'تم تحميل {len(self.full_records)} سجل بنجاح.')  # رسالة تسجيل عدد السجلات المحملة
            except Exception as e:
                print(f"خطأ في البحث: {e}")
    
    def show_profile(self, item):
        record_data = self.full_records.get(item.text(), {})
        if record_data:
            dialog = ProfileDialog(record_data, self)
            dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    window = DatabaseApp()
    window.show()
    sys.exit(app.exec_())
