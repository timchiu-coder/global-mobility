import streamlit as st
import re
import pandas as pd

# 設置網頁標題
st.set_page_config(page_title="直航必有因：航線數據提取器", page_icon="✈️")

st.title("✈️ 直航必有因：航線數據提取器")
st.markdown("""
將 FlightConnections 網頁的原始碼貼在下方，我會為你提取出所有目的地機場與所屬國家。
""")

# 側邊欄說明
with st.sidebar:
    st.header("使用說明")
    st.write("1. 到 FlightConnections 機場頁面按 Ctrl+U。")
    st.write("2. 全選並複製原始碼。")
    st.write("3. 貼到右側輸入框。")
    st.write("---")
    st.write("💡 *數據反映地緣政治與經濟聯繫*")

# 使用者輸入區域
data = st.text_area("請貼上網頁原始碼 (HTML)", height=300, placeholder="<html>...</html>")

if st.button("開始提取數據"):
    if data:
        # 你的核心正規表示式邏輯
        pattern = r'data-a=".*?\((.*?)\)"'  # 擷取 () 內的機場代碼
        alt_pattern = r'alt="(.*?)"'        # 擷取 alt 中的目的地名稱
        
        matches = [m.group(1) for m in re.finditer(pattern, data)]
        alt_matches = [m.group(1) for m in re.finditer(alt_pattern, data)]
        
        # 確保兩者長度一致，避免 zip 出錯
        min_len = min(len(matches), len(alt_matches))
        
        if min_len > 0:
            # 建立 DataFrame
            df = pd.DataFrame({
                "機場代碼": matches[:min_len],
                "目的地與國家": alt_matches[:min_len]
            })
            
            # 去除重複項 (有些 HTML 標籤會重複出現)
            df = df.drop_duplicates().reset_index(drop=True)
            
            st.success(f"成功提取 {len(df)} 條不重複航線！")
            
            # 顯示表格
            st.dataframe(df, use_container_width=True)
            
            # 下載 CSV 功能
            csv = df.to_csv(index=False).encode('utf-8-sig')
            st.download_button(
                label="📥 下載資料為 CSV",
                data=csv,
                file_name='airport_routes.csv',
                mime='text/csv',
            )
        else:
            st.warning("找不到匹配的數據，請確認原始碼是否正確。")
    else:
        st.error("請先貼上原始碼內容！")