import streamlit as st
import pandas as pd
from bs4 import BeautifulSoup

# 設置網頁標題
st.set_page_config(page_title="直航必有因 Flight Analysis", page_icon="✈️")

st.title("✈️ 直航必有因：精確數據提取器 V3.1")
st.subheader("針對 ROR/帛琉 結構優化版")

html_data = st.text_area("請貼上網頁原始碼 (HTML)", height=250, placeholder="在此貼上原始碼...")

if st.button("開始提取數據"):
    if html_data:
        try:
            soup = BeautifulSoup(html_data, 'html.parser')
            
            # 【核心修正 1】直接定位到目的地清單區塊
            # FlightConnections 的直飛清單一定會放在 id="destination-list" 裡面
            dest_container = soup.find(id="destination-list")
            
            if not dest_container:
                # 備用方案：尋找主要的側邊導覽欄
                dest_container = soup.find(id="sidebar")

            if dest_container:
                # 【核心修正 2】只在該容器內尋找帶有 data-c (IATA Code) 的連結
                links = dest_container.find_all('a', attrs={'data-c': True})
                
                route_data = []
                for link in links:
                    iata = link.get('data-c', '').upper()
                    
                    # 抓取圖片的 alt 屬性來取得「目的地, 國家」
                    img_tag = link.find('img')
                    alt_text = img_tag.get('alt', '') if img_tag else ""
                    
                    if iata and alt_text:
                        # 處理國家名稱：取最後一個逗號後面的內容
                        country = alt_text.split(',')[-1].strip() if ',' in alt_text else "Unknown"
                        
                        route_data.append({
                            "Destination": iata,
                            "Country": country
                        })
                
                # 轉為 DataFrame 並去除重複
                df = pd.DataFrame(route_data).drop_duplicates().reset_index(drop=True)
                
                if not df.empty:
                    st.success(f"✅ 精確過濾完成！共找到 {len(df)} 條直飛航線。")
                    st.dataframe(df, use_container_width=True)
                    
                    # CSV 下載
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    st.download_button("📥 下載 CSV", data=csv, file_name='direct_flights.csv')
                else:
                    st.warning("在目的地清單中找不到航線，請確認原始碼是否正確。")
            else:
                st.error("❌ 找不到直飛清單容器 (id='destination-list')。請確保您是從該機場的專屬頁面複製原始碼。")
                
        except Exception as e:
            st.error(f"發生錯誤: {e}")
    else:
        st.error("請先貼上內容。")

with st.sidebar:
    st.markdown("""
    ### 為什麼這次會準？
    之前的版本會在整個網頁（包括頁首、導覽列、頁尾）亂抓。
    新版本會像**手術刀**一樣，直接切入 `#destination-list` 區塊，忽略所有無關的 SEO 連結。
    """)