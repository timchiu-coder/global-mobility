import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re

# 設置網頁標題 / Set Page Config
st.set_page_config(page_title="直航必有因 Flight Analysis", page_icon="✈️")

# 1. 雙語 UI 標題 / Bilingual UI Header
st.title("✈️ 直航必有因 / Direct Flight Analysis")
st.subheader("機場航線數據提取器 / Airport Route Extractor")

st.markdown("""
**[ZH]** 請將 FlightConnections 網頁的原始碼貼在下方。為了取得 **英文國家名稱**，建議從 [FlightConnections English Version](https://www.flightconnections.com/) 複製原始碼。  
**[EN]** Please paste the FlightConnections source code below. To get **English country names**, it is recommended to copy the source from the English version of the site.
""")

# 2. 使用者輸入區域 / User Input Area
label_text = "請貼上網頁原始碼 (HTML) / Paste HTML Source Code Here"
html_data = st.text_area(label_text, height=250, placeholder="<html>...</html>")

# 3. 執行按鈕 / Action Button
button_text = "開始提取數據 / Extract Data"
if st.button(button_text):
    if html_data:
        try:
            soup = BeautifulSoup(html_data, 'html.parser')
            route_list = []
            
            # 尋找所有包含航線資訊的連結 / Finding route links
            links = soup.find_all('a', attrs={'data-a': True})
            
            for link in links:
                # 提取 IATA Code
                data_a = link.get('data-a', '')
                code_match = re.search(r'\((.*?)\)', data_a)
                iata_code = code_match.group(1).upper() if code_match else None
                
                # 提取目的地與國家 / Extract Destination & Country
                img_tag = link.find('img')
                raw_dest = img_tag.get('alt', '') if img_tag else ""
                
                # 邏輯精進：拆分 城市 與 國家
                # 通常格式為 "Tokyo (NRT), Japan" 或 "東京 (NRT), 日本"
                if iata_code and raw_dest:
                    if "," in raw_dest:
                        parts = raw_dest.split(",")
                        dest_name = parts[0].strip()
                        country_name = parts[1].strip()
                    else:
                        dest_name = raw_dest
                        country_name = "Unknown"

                    route_list.append({
                        "IATA Code": iata_code,
                        "Destination (城市/機場)": dest_name,
                        "Country (國家)": country_name
                    })
            
            if route_list:
                df = pd.DataFrame(route_list)
                df = df.drop_duplicates().reset_index(drop=True)
                
                st.success(f"✅ 成功提取 {len(df)} 條航線！ / Successfully extracted {len(df)} routes!")
                
                # 顯示數據表格 / Show Data Table
                st.dataframe(df, use_container_width=True)
                
                # 下載 CSV / Download CSV
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載 CSV / Download CSV",
                    data=csv,
                    file_name='airport_routes_bilingual.csv',
                    mime='text/csv',
                )
            else:
                st.warning("未能解析出數據。 / No data found.")
                
        except Exception as e:
            st.error(f"錯誤 / Error: {e}")
    else:
        st.error("請提供原始碼。 / Please provide source code.")

# 側邊欄說明 / Sidebar Info
with st.sidebar:
    st.header("教學重點 / Teaching Points")
    st.info("""
    **1. 直航必有因 (Direct Flight Analysis):**
    觀察航線分布，探討背後的政治、經濟與文化聯繫。
    Explore the political, economic, and cultural ties behind flight routes.

    **2. 數據標準化 (Data Standardization):**
    使用 IATA Code (如 TPE, FCO) 進行全球統一標註。
    Use IATA codes for global standardization.

    **3. 英文國家名稱 (English Country Names):**
    接軌國際地理數據與 Python 地圖庫 (如 Folium)。
    Compatible with international geographic data and map libraries.
    """)