import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re

# 設置網頁標題 / Set Page Config
st.set_page_config(page_title="直航必有因 Flight Analysis", page_icon="✈️")

# 雙語 UI 標題 / Bilingual UI Header
st.title("✈️ 直航必有因 / Direct Flight Analysis")
st.subheader("機場航線數據提取器 V2.2 / Airport Route Extractor V2.2")

st.markdown("""
**[ZH]** 已修正國家顯示為 Unknown 的問題。請務必從 [FlightConnections 英文版](https://www.flightconnections.com/) 複製原始碼以確保國家名為英文。  
**[EN]** Fixed the "Unknown" country issue. Please ensure you copy the source from the [English version](https://www.flightconnections.com/) for English data.
""")

# 使用者輸入區域 / User Input Area
html_data = st.text_area("請貼上網頁原始碼 (HTML) / Paste HTML Source Code Here", height=250)

if st.button("開始提取數據 / Extract Data"):
    if html_data:
        try:
            soup = BeautifulSoup(html_data, 'html.parser')
            route_list = []
            
            # 定位航線連結：FlightConnections 的航線連結通常帶有 data-c (IATA代碼)
            links = soup.find_all('a', attrs={'data-c': True})
            
            # 如果找不到 data-c，則退回搜尋 data-a 標籤
            if not links:
                links = soup.find_all('a', attrs={'data-a': True})

            for link in links:
                # 1. 提取 IATA Code (優先使用 data-c 屬性)
                iata_code = link.get('data-c', '').upper()
                
                # 如果 data-c 為空，則從 data-a 提取括號內的代碼
                if not iata_code:
                    data_a = link.get('data-a', '')
                    code_match = re.search(r'\((.*?)\)', data_a)
                    iata_code = code_match.group(1).upper() if code_match else ""

                # 2. 提取完整描述 (從 img 的 alt 屬性)
                img_tag = link.find('img')
                raw_alt = img_tag.get('alt', '') if img_tag else ""
                
                if iata_code:
                    # 國家拆分邏輯精進 / Advanced Splitting Logic
                    # 範例格式: "Manila (MNL), Philippines"
                    if "," in raw_alt:
                        parts = raw_alt.split(",")
                        country_name = parts[-1].strip() # 取得最後一個逗號後的內容 (國家)
                    else:
                        # 處理沒逗號的異常情況，嘗試從 data-a 猜測或標記
                        country_name = "Check Source Language" 

                    # 依照使用者要求設定欄位名稱與內容
                    # Destination 直接顯示代碼 (如 MNL)，Country 顯示國家
                    route_list.append({
                        "Destination": iata_code,
                        "City (城市)": link.get('data-as', iata_code), # 保留城市名供參考
                        "Country": country_name
                    })
            
            if route_list:
                df = pd.DataFrame(route_list).drop_duplicates().reset_index(drop=True)
                
                # 只顯示使用者需要的欄位 / Display only requested columns
                display_df = df[["Destination", "Country"]]
                
                st.success(f"✅ 成功提取 {len(df)} 條航線！ / Successfully extracted {len(df)} routes!")
                st.dataframe(display_df, use_container_width=True)
                
                # 下載 CSV 功能
                csv = display_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載 CSV / Download CSV",
                    data=csv,
                    file_name='airport_routes_fixed.csv',
                    mime='text/csv',
                )
            else:
                st.warning("找不到數據，請確認原始碼內容是否正確。 / No data found.")
                
        except Exception as e:
            st.error(f"解析錯誤 / Error: {e}")
    else:
        st.error("請提供原始碼。 / Please provide source code.")

# 側邊欄提醒
with st.sidebar:
    st.info("💡 **提示 (Tip):** 如果國家仍顯示不正確，請檢查網頁是否已切換至 **English** 語系再複製原始碼。")