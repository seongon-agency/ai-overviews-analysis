from functions.fetchKeywords import fetchKeywords
from functions.apiToDataFrame import apiToDataFrame
from functions.analyzeDataFrame import analyzeDataFrame
import streamlit as st
import pandas as pd
import json
import io
import plotly.express as px
import plotly.graph_objects as go

# SET PAGE CONFIG
st.set_page_config(
    page_title="Google AI Overviews Analysis",
    layout=None
)

st.title("AI Overviews Analysis Tool")
st.markdown("Phân tích dữ liệu Google AI Overviews trên 1 bộ từ khóa nhất định cho doanh nghiệp và phân tích đối thủ.")

# DEFINING MODES
route = st.radio(
    "Chọn chế độ:",
    ["Fetch Keywords", "Upload JSON"],
    captions=[
        "Lấy dữ liệu từ khóa trực tiếp",
        "Tải lên file API (json) có sẵn",
    ],
)

dataframe = None

# ROUTING FOR DIFFERENT MODES

## 1. FETCH KEYWORDS MODE
if route == "Fetch Keywords":
    st.subheader("Live API Fetch")

    with st.form("keyword_form"):
        keywords_input = st.text_area(
            "Điền từ khóa (mỗi dòng 1 từ, hoặc ngăn cách bằng dấu phẩy):",
            placeholder="seo là gì\nseo trong marketing\nai trong seo"
        )
        col1, col2 = st.columns(2)
        with col1:
            location_code = st.text_input("Mã địa điểm (4 chữ số):", placeholder="2740")
        with col2:
            language_code = st.text_input("Mã ngôn ngữ:", placeholder="vi")

        submit_button = st.form_submit_button("Lấy Data")

    ## IF ALL THE NECESSARY INPUTS ARE NOT EMPTY
    if submit_button and keywords_input and location_code and language_code:
        # Process keywords
        keywords = [k.strip() for k in keywords_input.replace('\n', ',').split(',') if k.strip()]

        if keywords:
            with st.spinner(f"Fetching data for {len(keywords)} keywords..."):
                try:
                    api_result = fetchKeywords(keywords, location_code, language_code)
                    dataframe = apiToDataFrame(api_result)
                    st.success(f"Successfully fetched data for {len(keywords)} keywords")
                except Exception as e:
                    st.error(f"Error fetching data: {str(e)}")

## 2. UPLOAD JSON MODE
elif route == "Upload JSON":
    st.subheader("Tải JSON File")

    uploaded_file = st.file_uploader(
        "Tải lên file JSON",
        type=['json'],
        help="Tải file JSON có sẵn"
    )

    ### if uploaded file is not empty
    if uploaded_file is not None:
        try:
            # Read the uploaded JSON file
            data = json.load(uploaded_file)
            dataframe = data
            st.success("Tải lên file thành công")
        except Exception as e:
            st.error(f"Lỗi loading JSON file: {str(e)}")

# Analysis section
if dataframe is not None:
    st.subheader("Kết quả phân tích")

    with st.form("analysis_form"):
        col1, col2 = st.columns(2)
        with col1:
            brand_name = st.text_input("Tên brand:", placeholder="SEONGON")
        with col2:
            brand_domain = st.text_input("Domain brand:", placeholder="seongon.com")

        analyze_button = st.form_submit_button("Phân tích Data")

    if analyze_button and brand_name and brand_domain:
        with st.spinner("Đang phân tích data..."):
            try:
                # Debug: Show data structure info
                if isinstance(dataframe, pd.DataFrame):
                    # Show a sample of the data structure
                    if not dataframe.empty:
                        st.json({"sample_data_structure": str(type(dataframe.iloc[0, 0]))})

                # Pass the brand info as globals
                import builtins
                builtins.brand_name_input = brand_name
                builtins.brand_domain_input = brand_domain

                result = analyzeDataFrame(dataframe)

                if result is not None and isinstance(result, dict) and result.get('status') == 'success':
                    # Display analysis summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Số từ khóa", result.get('keywords_analyzed', 0))
                    with col2:
                        st.metric("Số AI Overviews", result.get('ai_overviews_found', 0))
                    with col3:
                        st.metric("Số đối thủ cạnh tranh", result.get('competitors_identified', 0))

                    # Get the DataFrames
                    keywords_df = result.get('keywords_df')
                    competitors_df = result.get('competitors_df')

                    # Display results in tabs
                    tab1, tab2 = st.tabs(["Phân tích từ khóa", "Phân tích đối thủ"])

                    with tab1:
                        st.subheader("Kết quả của phân tích trên từng từ khóa")
                        if keywords_df is not None and not keywords_df.empty:
                            # Show only readable format
                            display_df = keywords_df.drop(columns=['aio_references']) if 'aio_references' in keywords_df.columns else keywords_df
                            if 'aio_references_display' in display_df.columns:
                                display_df = display_df.rename(columns={'aio_references_display': 'aio_references'})

                            st.dataframe(display_df, use_container_width=True)

                            # Download button
                            csv_keywords = keywords_df.to_csv(index=False)
                            st.download_button(
                                label="Tải file",
                                data=csv_keywords,
                                file_name="keywords_analysis.csv",
                                mime="text/csv",
                                key="download_keywords"
                            )
                        else:
                            st.warning("Không có data từ khóa")

                    with tab2:
                        st.subheader("Kết quả phân tích đối thủ cạnh tranh tổng quan")
                        if competitors_df is not None and not competitors_df.empty:
                            # Add explanation of the combined metrics
                            st.info("""
                            **Chú thích**
                            - **Citations**: Số lần được làm nguồn trích dẫn trong AI Overviews
                            - **Mentions**: Số lần được AI Overviews brand mention
                            """)

                            # Display key metrics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                total_citations = competitors_df['cited_count'].sum()
                                st.metric("Tổng số trích dẫn", total_citations)
                            with col2:
                                total_mentions = competitors_df['mentioned'].sum()
                                st.metric("Tổng số Brand Mention", total_mentions)
                            with col3:
                                avg_citation_rate = competitors_df['prompt_cited_rate'].mean()
                                st.metric("Tỉ lệ trích dẫn trung bình", f"{avg_citation_rate:.1%}")
                            with col4:
                                avg_mention_rate = competitors_df['mention_rate'].mean()
                                st.metric("Tỉ lệ Brand Mention trung bình", f"{avg_mention_rate:.1%}")

                            # Create visualization
                            st.subheader("Biểu đồ trực quan hóa danh sách thương hiệu được trích nguồn và mention trên AI Overviews")

                            # Prepare data for visualization
                            viz_df = competitors_df.copy()
                            viz_df['total_engagement'] = viz_df['cited_count'] + viz_df['mentioned']

                            # Find user's brand and separate it
                            user_brand_row = viz_df[viz_df['brand'].str.lower() == brand_name.lower()]
                            other_brands = viz_df[viz_df['brand'].str.lower() != brand_name.lower()]

                            # Take top 15 other brands for readability
                            other_brands_top = other_brands.head(15)

                            # Combine user brand (at top) with other top brands
                            if not user_brand_row.empty:
                                chart_data = pd.concat([user_brand_row, other_brands_top]).reset_index(drop=True)
                                # Add star to user brand name for extra visibility
                                chart_data.loc[0, 'brand'] = f"{chart_data.loc[0, 'brand']}"
                            else:
                                chart_data = other_brands_top

                            # Create colors: highlight user brand
                            colors = []
                            for brand in chart_data['brand']:
                                if brand.lower() == brand_name.lower():
                                    colors.append('#FF6B6B')  # Red for user brand
                                else:
                                    colors.append('#4ECDC4')  # Teal for competitors

                            # Create colors for highlighting user brand
                            citation_colors = []
                            mention_colors = []
                            text_colors = []

                            for brand in chart_data['brand']:
                                if brand.lower() == brand_name.lower():
                                    # Your brand - bright, distinctive colors
                                    citation_colors.append('#FFD700')  # Gold for citations
                                    mention_colors.append('#FF6B35')   # Orange for mentions
                                    text_colors.append('black')
                                else:
                                    # Competitors - muted colors
                                    citation_colors.append('#87CEEB')  # Light blue
                                    mention_colors.append('#F08080')  # Light coral
                                    text_colors.append('white')

                            # Create horizontal bar chart
                            fig = go.Figure()

                            # Add bars for mentions with individual colors (first, so they appear below)
                            fig.add_trace(go.Bar(
                                name='Mentions',
                                y=chart_data['brand'],
                                x=chart_data['mentioned'],
                                orientation='h',
                                marker_color=mention_colors,
                                marker_line=dict(
                                    color=['#CC5500' if brand.lower() == brand_name.lower() else '#E57373'
                                           for brand in chart_data['brand']],
                                    width=[3 if brand.lower() == brand_name.lower() else 1
                                           for brand in chart_data['brand']]
                                ),
                                text=chart_data['mentioned'],
                                textposition='auto',
                                textfont=dict(
                                    color=['black' if brand.lower() == brand_name.lower() else 'white'
                                           for brand in chart_data['brand']],
                                    size=[14 if brand.lower() == brand_name.lower() else 12
                                          for brand in chart_data['brand']]
                                )
                            ))

                            # Add bars for citations with individual colors (second, so they appear above)
                            fig.add_trace(go.Bar(
                                name='Citations',
                                y=chart_data['brand'],
                                x=chart_data['cited_count'],
                                orientation='h',
                                marker_color=citation_colors,
                                marker_line=dict(
                                    color=['#B8860B' if brand.lower() == brand_name.lower() else '#5DADE2'
                                           for brand in chart_data['brand']],
                                    width=[3 if brand.lower() == brand_name.lower() else 1
                                           for brand in chart_data['brand']]
                                ),
                                text=chart_data['cited_count'],
                                textposition='auto',
                                textfont=dict(
                                    color=['black' if brand.lower() == brand_name.lower() else 'white'
                                           for brand in chart_data['brand']],
                                    size=[14 if brand.lower() == brand_name.lower() else 12
                                          for brand in chart_data['brand']]
                                )
                            ))

                            # Update layout
                            fig.update_layout(
                                title=f"Competitor Citations vs Mentions (Your Brand: {brand_name})",
                                xaxis_title="Count",
                                yaxis_title="Brands",
                                barmode='group',
                                height=max(400, len(chart_data) * 40),
                                showlegend=True,
                                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                                yaxis=dict(
                                    tickfont=dict(size=12),
                                    categoryorder='array',
                                    categoryarray=list(reversed(chart_data['brand']))
                                )
                            )

                            # Highlight user brand with different styling
                            if not user_brand_row.empty:
                                user_brand_index = chart_data[chart_data['brand'].str.lower() == brand_name.lower()].index[0]
                                fig.add_shape(
                                    type="rect",
                                    x0=-max(chart_data['cited_count'].max(), chart_data['mentioned'].max()) * 0.05,
                                    y0=user_brand_index - 0.4,
                                    x1=max(chart_data['cited_count'].max(), chart_data['mentioned'].max()) * 1.05,
                                    y1=user_brand_index + 0.4,
                                    line=dict(color="#FFD700", width=3),
                                    fillcolor="rgba(255, 215, 0, 0.1)"
                                )

                            st.plotly_chart(fig, use_container_width=True)

                            # Chart interpretation
                            if not user_brand_row.empty:
                                user_citations = user_brand_row['cited_count'].iloc[0]
                                user_mentions = user_brand_row['mentioned'].iloc[0]
                                user_rank = competitors_df[competitors_df['brand'].str.lower() == brand_name.lower()].index[0] + 1

                                st.info(f"""
                                **Your Brand Performance:**
                                - **{brand_name}** ranks #{user_rank} overall among all competitors
                                - Citations: {user_citations} | Mentions: {user_mentions}
                                - Your brand is highlighted in gold in the chart above
                                """)

                            # Display the comprehensive dataframe
                            st.subheader("Detailed Data Table")
                            st.dataframe(competitors_df, use_container_width=True)

                            # Download button
                            csv_competitors = competitors_df.to_csv(index=False)
                            st.download_button(
                                label="Download Comprehensive Competitor Analysis CSV",
                                data=csv_competitors,
                                file_name="comprehensive_competitor_analysis.csv",
                                mime="text/csv",
                                key="download_competitors"
                            )
                        else:
                            st.warning("No competitor data available")

                    # Summary download - all files in one
                    st.subheader("Download toàn bộ file")
                    col1, col2 = st.columns(2)

                    with col1:
                        # Create a summary of all results
                        if all(df is not None and not df.empty for df in [keywords_df, competitors_df]):
                            # Calculate summary stats
                            total_citations = competitors_df['cited_count'].sum()
                            total_mentions = competitors_df['mentioned'].sum()
                            top_competitor = competitors_df.iloc[0] if not competitors_df.empty else None

                            # Create formatted strings for rates
                            citation_rate = f"{top_competitor['prompt_cited_rate']:.1%}" if top_competitor is not None else 'N/A'
                            mention_rate = f"{top_competitor['mention_rate']:.1%}" if top_competitor is not None else 'N/A'

                            # Combine summary stats
                            summary_text = f"""
AI Overviews Analysis Summary
Brand: {brand_name} ({brand_domain})
====================================

Keywords Analyzed: {result.get('keywords_analyzed', 0)}
AI Overviews Found: {result.get('ai_overviews_found', 0)}
Competitors Identified: {result.get('competitors_identified', 0)}

Total Citations Across All Competitors: {total_citations}
Total Mentions Across All Competitors: {total_mentions}

Top Competitor by Total Engagement:
{top_competitor['brand'] if top_competitor is not None else 'No data'}
- Citations: {top_competitor['cited_count'] if top_competitor is not None else 'N/A'}
- Mentions: {top_competitor['mentioned'] if top_competitor is not None else 'N/A'}
- Citation Rate: {citation_rate}
- Mention Rate: {mention_rate}

Top 5 Competitors Summary:
{competitors_df[['brand', 'cited_count', 'mentioned', 'prompt_cited_rate', 'mention_rate']].head().to_string(index=False) if not competitors_df.empty else 'No data'}
                            """

                            st.download_button(
                                label="Tải xuống",
                                data=summary_text,
                                file_name="analysis_summary.txt",
                                mime="text/plain",
                                key="download_summary"
                            )

                else:
                    st.warning("Analysis completed but no results were generated. Check the error messages above.")

            except Exception as e:
                st.error(f"Unexpected error during analysis: {str(e)}")
                st.error("Please check your data format and try again.")

# Sidebar with instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    **Bước 1:** Chọn chế độ
    - **Fetch Keywords**: Lấy dữ liệu từ khóa trong thời gian thực
    - **Upload JSON**: Dùng file JSON API đã tải về từ trước
                
    --------

    **Bước 2:** (Cho chế độ 1) Tùy chỉnh các thông tin để lấy dữ liệu từ khóa
    - Điền các từ khóa
    - Điền mã địa điểm và mã ngôn ngữ
    
    --------

    **Step 3:** Phân tích kết quả
    - Điền tên thương hiệu và domain
    - Tạo các bảng phân tích chi tiết

    ---------
                
    **Mã địa điểm thông dụng:** Tra "<tên quốc gia> numeric location code" trên Google và thêm số 2 ở đầu
    - Vietnam: 704 -> 2704
                
    ---------
                
    **Mã ngôn ngữ:**
    - en: English
    - vi: Vietnamese
    """)
    

    st.header("Các file tải về")
    st.markdown("""
    - `keywords.csv`: Kết quả phân tích từ khóa
    - `competitor.csv`: Kết quả phân tích đối thủ
    """)