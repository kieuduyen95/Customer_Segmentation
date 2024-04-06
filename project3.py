#IMPORT LIBRARIES
import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly
import plotly.express as px
import squarify
#from datetime import datetime
#from sklearn.feature_extraction.text import TfidfVectorizer
#from underthesea import word_tokenize, pos_tag, sent_tokenize
#import jieba
#import re
#import string


# LOADING DATA
df_raw = pd.read_csv('data/OnlineRetail.csv', sep=",", encoding='latin')
df_id = df_raw.copy()
df_fix = pd.read_csv('data/OnlineRetail_fix.csv', sep=",", encoding='latin')
cust_rfm = pd.read_csv('data/Customer_RFM.csv')
cust_seg = pd.read_csv('data/Customer_Segmentation.csv')
df_rfm = pd.read_csv('data/OnlineRetail_RFM.csv')
#df_cust = pd.read_csv('data/df_cust.csv')
rfm_agg = pd.read_csv('data/rfm_agg.csv')
#rfm_agg2 = pd.read_csv('data/rfm_agg2.csv')

df_id['InvoiceDate'] = pd.to_datetime(df_id['InvoiceDate'], format='%d-%m-%Y %H:%M')
df_id['CustomerID'] = df_id['CustomerID'].astype(str)
df_fix['GrossSale'] =  df_fix['Quantity']*df_fix['UnitPrice']
df_fix = df_fix.loc[(df_fix['InvoiceNo'].str[0] != 'A') & (df_fix['InvoiceNo'].str[0] != 'C')
                                & (df_fix['UnitPrice'] != 0) & (df_fix['CustomerID'] != '10000.0')]
df_new = df_fix.groupby(['InvoiceNo', 'InvoiceDate', 'CustomerID', 'Country'])['GrossSale'].sum().reset_index()
df_new['CustomerID'] = df_new['CustomerID'].apply(lambda x: str(x).replace('.0',''))
cust_rfm['CustomerID'] = cust_rfm['CustomerID'].apply(lambda x: str(x).replace('.0',''))
df_cust = df_fix.loc[(df_fix['Quantity'] > 0) & (df_fix['UnitPrice'] > 0)]
df_cust['CustomerID'] = df_cust['CustomerID'].apply(lambda x: str(x).replace('.0',''))




# USING MENU
st.title("Customer Segmentation")
menu = ["Trang chủ", "Tổng quan kinh doanh", "Công cụ phân nhóm", "Phân tích khách hàng"]
choice = st.sidebar.selectbox('Trang chủ', menu)
if choice == "Trang chủ":
    st.image('data/pics/Customer-Segmentation.jpg')

elif choice =='Tổng quan kinh doanh':
    st.image('data/pics/customer-segmentation.webp')
    st.subheader("TỔNG QUAN TÌNH HÌNH KINH DOANH ONLINE")
    st.write("##### 1. Tổng quan đơn hàng:")
    
    # Đếm số lượng đơn hàng
    a = len(df_raw['InvoiceNo'].unique())
    b = len(df_raw.loc[df_raw['Quantity'] <= 0]['InvoiceNo'].unique())
    c = len(df_raw.loc[df_raw['UnitPrice'] <= 0]['InvoiceNo'].unique())
    st.dataframe(pd.DataFrame({'Đơn hàng': ['Tổng', 'Bị trả','Bị điều chỉnh hoặc sale', 'Thực tế'], 'Số lượng': [a,b,c,a-b-c]}))
    
    # Khách hàng vãng lai
    bill_vanglai = len(df_raw.loc[df_raw['CustomerID'].isna()]['InvoiceNo'].unique())*100/len(df_raw['InvoiceNo'].unique())
    st.write("Tỷ lệ đơn hàng từ KH vãng lai: ",round(bill_vanglai,2),"%")
    st.write("Tỷ lệ đơn hàng từ KH định danh: ",100 - round(bill_vanglai,2),"%")
    st.write('Giao dịch được tổng hợp từ {} đến {}'.format(df_fix['InvoiceDate'].min(), df_fix['InvoiceDate'].max()))
    st.write('Trong đó số lượng KH được định danh là {:,} '.format(len(df_fix['CustomerID'].unique())))
    
    # Thống kê đơn hàng theo quốc gia
    #
    df_country = df_cust.groupby('Country').agg({'CustomerID': lambda x: len(x.unique()), 'InvoiceNo': lambda x: len(x.unique())}).reset_index()
    df_country.columns = ['Country', 'Số lượng KH', 'Số lượng đơn hàng']
    df_country.sort_values(by = 'Số lượng KH', ascending = False, inplace = True)
    df_country.reset_index(drop=True, inplace=True)
    st.write('Thống kê đơn hàng theo quốc gia:')
    #st.dataframe(df_country.head())

    df_bar = df_country.head()
    colors = ['salmon', 'limegreen','gold', 'pink','skyblue']
    sorted_indices = sorted(range(len(df_bar['Số lượng KH'])), key=lambda i: df_bar['Số lượng đơn hàng'][i], reverse=False)
    sorted_countries = [df_bar['Country'][i] for i in sorted_indices]
    sorted_num_countries = [df_bar['Số lượng KH'][i] for i in sorted_indices]
    st.dataframe(df_country.head())

    # Hiển thị biểu đồ cột
    plt.figure(figsize=(10, 6))
    plt.barh(df_bar['Country'], df_bar['Số lượng KH'], color=colors)
    plt.xlabel('Số lượng KH')
    plt.ylabel('Country')
    plt.title('Top 5 quốc gia có nhiều khách hàng nhất')
    plt.tight_layout()
    st.pyplot(plt)

   

    






elif choice == "Công cụ phân nhóm":
    st.image('data/pics/cust.png')
    st.write('### Manual Segmentation')
    st.write("""Customer Segmentation là một công cụ mạnh mẽ giúp doanh nghiệp hiểu sâu hơn về khách hàng của họ và cách tùy chỉnh chiến lược tiếp thị
                            Đây là một bước không thể thiếu để đảm bảo rằng bạn đang tiếp cận và phục vụ mọi nhóm khách hàng một cách hiệu quả""")
    st.write("""Tiêu chí phân loại Khách hàng:""")
    st.write("""
             + VIPs: Khách hàng có lượng chi tiêu lớn, tần suất tiêu thụ thường xuyên, và vừa shopping gần đây
             
            + BIG Spender: Khách hàng chi tiêu lớn, nhưng khác VIPs ở điểm không tiêu thụ thường xuyên bằng
             
            + LOYAL: Khách hàng thường đến, và vẫn đang acitve (đến gần đây), mức độ chi tiêu kém hơn VIPs
             
            + NEWCUST: Khách hàng mới đến gần đây, chưa quan tâm đến mức độ chi tiêu
             
            + LIGHT: Khách hàng có lượng chi tiêu ít nhất trong nhóm đang active, nhưng vẫn thường đến
             
            + LOST: Khách hàng quá lâu chưa đến, và thường chi tiêu ít
             
            + REGULARS: Nhóm còn lại, thường ở mức trung bình ở 3 khía cạnh M, F, R
            """)
    st.write('### Dataframe gốc')
    st.dataframe(df_raw.head())
    st.write('### Dataframe sau khi xử lý Manual Segmentation')
    st.dataframe(rfm_agg)
    st.write('### TreeMap')
    st.image('data/RFM Segments.png')
    st.write('### Scatter Plot (RFM)')
    st.image('data/Scatter Segments.png')

elif choice=='Phân tích khách hàng':
    st.image('data/pics/seg.png')
    st.subheader("PHÂN TÍCH KHÁCH HÀNG")
    st.write("##### 1. Nhập thông tin khách hàng")
    type = st.radio("Nhập thông tin khách hàng", options=["Mã khách hàng", "Thông tin mua sắm của khách hàng"])
    if type == "Mã khách hàng":
        # Nếu người dùng chọn nhập mã khách hàng
        #'14911.0', '17841.0', '15311.0', ..., '12409.0', '16738.0', '16446.0'
        st.subheader("Mã khách hàng")
        # Tạo điều khiển để người dùng nhập mã khách hàng
        customer_id = st.text_input("Mã khách hàng")
        if customer_id in df_new['CustomerID'].values:
        #customer_id = '17850.0'
            #user_input = st.text_input("Tên nhà hàng là:")
            # Convert InvoiceDate from object to datetime format
            st.write(f"Thông tin Khách hàng {customer_id}:")
            df_cust_id = df_cust.loc[df_cust['CustomerID'] == customer_id]
            st.write("Đã từng mua sắm ở:")
            st.dataframe(df_cust_id['Country'].value_counts())
            st.write("Số lần mua hàng:", df_cust_id['InvoiceNo'].nunique())
            st.write("Chi tiêu trong khoảng từ ($)", round(df_cust_id['GrossSale'].min(),0), "đến", df_cust_id['GrossSale'].max())
            st.write("Tổng chi:", round(df_cust_id['GrossSale'].sum(),2))
            st.write("Thông tin mua hàng sắp xếp theo lần gần nhất: ", )
            st.dataframe(df_cust_id.sort_values(['InvoiceDate'], ascending= False, ignore_index= True))
            
            # Đề xuất khách hàng thuộc cụm nào
            df_cust_rfm = cust_rfm.loc[cust_rfm['CustomerID'] == customer_id]
            st.write(f"KH {customer_id} thuộc nhóm")
            st.dataframe(df_cust_rfm)

                       
        else:
            # Không có khách hàng
            st.write(f"Invalid Customer ID!")


    elif type == "Thông tin mua sắm của khách hàng":

        # Nếu người dùng chọn nhập thông tin khách hàng vào dataframe có 3 cột là Recency, Frequency, Monetary
        st.write("##### 2. Thông tin khách hàng")
        # Tạo điều khiển table để người dùng nhập thông tin khách hàng trực tiếp trên table
        st.write("Nhập thông tin khách hàng")

        # Loop to get input from the user for each customer
            # Get input using sliders
        # Tạo DataFrame rỗng
        df_customer = pd.DataFrame(columns=["Recency", "Frequency", "Monetary"])

        # Lặp qua 5 khách hàng
        for i in range(2):
            st.write(f"Khách hàng {i+1}")
            
            # Sử dụng sliders để nhập giá trị cho Recency, Frequency và Monetary
            recency = st.slider("Recency", 1, 365, 100, key=f"recency_{i}")
            frequency = st.slider("Frequency", 1, 50, 5, key=f"frequency_{i}")
            monetary = st.slider("Monetary", 1, 1000, 100, key=f"monetary_{i}")
            
            # Thêm dữ liệu nhập vào DataFrame
            df_customer = df_customer.append({"Recency": recency, "Frequency": frequency, "Monetary": monetary}, ignore_index=True)

        # Hiển thị DataFrame
        st.dataframe(df_customer)
                    
        # Create labels for Recency, Frequency, Monetary
        r_labels = range(4, 0, -1) #số ngày tính từ lần cuối mua hàng lớn thì gán nhãn nhỏ, ngược lại thì nhãn lớn
        f_labels = range(1, 5)
        m_labels = range(1, 5)

        # Assign these labels to 4 equal percentile groups
        r_groups = pd.qcut(df_customer['Recency'].rank(method = 'first'), q = 4, labels = r_labels)
        f_groups = pd.qcut(df_customer['Frequency'].rank(method = 'first'), q = 4, labels = f_labels)
        m_groups = pd.qcut(df_customer['Monetary'].rank(method = 'first'), q = 4, labels = m_labels)

        # Create new columns R, F, M
        df_customer = df_customer.assign(R = r_groups.values, F = f_groups.values, M = m_groups.values)
        def join_rfm(x): return str(int(x['R'])) + str(int(x['F'])) + str(int(x['M']))
        df_customer['RFM_Segment'] = df_customer.apply(join_rfm, axis=1)
        # Calculate RFM_Score
        df_customer['RFM_Score'] = df_customer[['R', 'F', 'M']].sum(axis=1)

        def rfm_level(df):
        # Check for special "STARS" and "NEW" condition first
            if df['RFM_Score'] == 12:
                return "VIPs"
        # Then check for other conditons
            elif df['M'] == 4 and df['F'] != 4 and df['R'] != 4: # F=4 & R=4 --> VIPs
                return "BIG SPENDER"
            elif df['F'] >= 3 and df['R'] >= 3: # KH thường đến, ko quan tâm M lớn nhỏ
                return "LOYAL"
            elif df['R'] == 4 and df['F'] == 1: # KH mới đến lần đầu, ko quan tâm M
                return "NEWCUST"
            elif df['M'] < 3 and df['R'] != 1 and df['F'] < 3: #nếu R = 1 thì thành LOST
                return "LIGTH"
            elif df['R'] == 1 and df['M'] == 1: # mua xa nhưng chi nhiều thì k đưa về nhóm lost
                return "LOST"
            else:
                return "REGULARS"

        # Create a new column RFM_Level
        df_customer['RFM_Level'] = df_customer.apply(rfm_level, axis=1)
        st.dataframe(df_customer)










