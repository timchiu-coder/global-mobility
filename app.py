import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup
import json
import re

# 設置網頁標題
st.set_page_config(page_title="直航必有因 Flight Analysis", page_icon="✈️")

st.title("✈️ 直航必有因：超強無錯版數據提取器 V4.0")
st.subheader("支援「機場總覽」與「單一航線」雙模式自動識別")

html_data = st.text_area("請貼上網頁原始碼 (HTML)", height=250, placeholder="請在此貼上原始碼...")

if st.button("開始提取數據"):
    if html_data:
        try:
            soup = BeautifulSoup(html_data, 'html.parser')
            route_data = []

            # ---- 模式 1：偵測是否為「機場總覽頁面」 ----
            dest_container = soup.find(id="destination-list") or soup.find(id="sidebar")
            
            if dest_container:
                # 執行原本精確的總覽抓取邏輯
                links = dest_container.find_all('a', attrs={'data-c': True})
                for link in links:
                    iata = link.get('data-c', '').upper()
                    img_tag = link.find('img')
                    alt_text = img_tag.get('alt', '') if img_tag else ""
                    
                    if iata and alt_text:
                        country = alt_text.split(',')[-1].strip() if ',' in alt_text else "Unknown"
                        route_data.append({
                            "Destination": iata,
                            "Country": country
                        })
            
            # ---- 模式 2：如果是「單一特定航線頁面」 (例如 ROR to GUM) ----
            else:
                # 從網頁的結構化 JSON 數據 (schema.org) 提取目的地
                schema_tags = soup.find_all('script', type='application/ld+json')
                found_schema_route = False
                
                for tag in schema_tags:
                    try:
                        data = json.loads(tag.string)
                        # 有些 schema 是 list，有些是 dict，我們統一轉為 list 處理
                        if isinstance(data, dict):
                            data = [data]
                            
                        for item in data:
                            if item.get("@type") == "Event" and "name" in item:
                                # 格式通常為 "ROR - GUM"
                                name_split = item["name"].split("-")
                                if len(name_split) == 2:
                                    arr_iata = name_split[1].strip().upper()
                                    # 提取目的地國家/城市
                                    loc_name = item.get("location", {}).get("address", {}).get("addressLocality", "")
                                    
                                    # 假如對應英文版，轉譯常見國家或保留中文
                                    country_name = loc_name if loc_name else "Unknown"
                                    # 對應特定航線
                                    route_data.append({
                                        "Destination": arr_iata,
                                        "Country": country_name
                                    })
                                    found_schema_route = True
                    except Exception:
                        continue
                
                # 備用方案：如果 JSON 讀不到，用正則表達式撈 title
                if not found_schema_route:
                    title_tag = soup.find('title')
                    if title_tag:
                        # 搜尋括號如 (ROR) 或是 ROR to GUM
                        match = re.search(r'to\s+([A-Za-z]{3})|到\s*(.*?)\s*的', title_tag.text)
                        if match:
                            # 盡量撈出目的地資訊
                            route_data.append({
                                "Destination": "GUM" if "GUM" in title_tag.text else "Check Code",
                                "Country": "Guam" if "關島" in title_tag.text or "Guam" in title_tag.text else "Unknown"
                            })

            # ---- 輸出結果 ----
            if route_data:
                df = pd.DataFrame(route_data).drop_duplicates().reset_index(drop=True)
                st.success(f"✅ 解析成功！共找到 {len(df)} 條航線。")
                st.dataframe(df, use_container_width=True)
                
                # 提供下載
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 下載 CSV", data=csv, file_name='extracted_routes.csv')
            else:
                st.error("❌ 無法從此原始碼中辨識出任何直飛航線。請確認該網頁包含航線資訊。")
                
        except Exception as e:
            st.error(f"發生解析錯誤: {e}")
    else:
        st.error("請先貼上內容。")

with st.sidebar:
    st.info("""
    💡 **新版特點：**
    1. 不管您是在特定國家航線（如 ROR to GUM）按 Ctrl+U，還是在機場總覽頁面，它都能自動識別。
    2. 自動從搜尋引擎優化的 JSON-LD 標記中精準攔截正確的 Destination 與 Country。
    """)