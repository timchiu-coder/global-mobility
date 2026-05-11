import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import re

# 設置網頁標題
st.set_page_config(page_title="直航必有因：航線數據提取器 V2", page_icon="✈️")

st.title("✈️ 直航必有因：航線數據提取器")
st.subheader("使用 BeautifulSoup 穩定解析版")

st.markdown("""
將 FlightConnections 網頁的原始碼貼在下方。此版本會自動配對機場代碼與國家，更精確穩定。
""")

# 使用者輸入區域
html_data = st.text_area("請貼上網頁原始碼 (HTML)", height=300, placeholder="<html>...</html>")

if st.button("開始提取數據"):
    if html_data:
        try:
            # 初始化 BeautifulSoup
            soup = BeautifulSoup(html_data, 'html.parser')
            
            route_list = []
            
            # FlightConnections 的規律：航線通常在 <a> 標籤中，且帶有 data-a 屬性
            # 內含 <img> 標籤，其 alt 屬性為目的地名稱
            links = soup.find_all('a', attrs={'data-a': True})
            
            for link in links:
                # 1. 提取機場代碼 (從 data-a="... (TPE)" 中擷取)
                data_a = link.get('data-a', '')
                code_match = re.search(r'\((.*?)\)', data_a)
                airport_code = code_match.group(1).upper() if code_match else None
                
                # 2. 提取目的地名稱 (從 <img> 的 alt 屬性中擷取)
                img_tag = link.find('img')
                destination = img_tag.get('alt', '') if img_tag else ""
                
                # 如果兩者都有抓到，才加入清單
                if airport_code and destination:
                    route_list.append({
                        "機場代碼": airport_code,
                        "目的地與國家": destination
                    })
            
            if route_list:
                df = pd.DataFrame(route_list)
                # 去除重複項
                df = df.drop_duplicates().reset_index(drop=True)
                
                st.success(f"✅ 成功提取 {len(df)} 條配對正確的航線！")
                
                # 數據預覽
                st.dataframe(df, use_container_width=True)
                
                # 下載 CSV 功能
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 下載資料為 CSV",
                    data=csv,
                    file_name='airport_routes_bs4.csv',
                    mime='text/csv',
                )
            else:
                st.warning("未能從原始碼中解析出航線。請確認是否為正確的 FlightConnections 機場頁面原始碼。")
                
        except Exception as e:
            st.error(f"解析過程中發生錯誤: {e}")
    else:
        st.error("請先貼上內容！")

with st.expander("為什麼這個版本更穩定？"):
    st.write("""
    1. **物件導向解析**：不再只是盲目搜尋字串，而是尋找真實的 HTML 連結元件。
    2. **屬性綁定**：保證 `data-a` (代碼) 是從同一個 `<a>` 標籤中跟 `alt` (名稱) 一起抓出來的，不會發生錯位。
    3. **容錯性高**：即使 HTML 標籤中間多了換行或空格，BeautifulSoup 也能正確識別。
    """)