from functions.fetchKeywords import fetchKeywords
from functions.apiToDataFrame import apiToDataFrame
from functions.analyzeDataFrame import analyzeDataFrame
import streamlit as st
import pandas as pd
import json
import io

# Set page config
st.set_page_config(
    page_title="AI Overviews Analysis",
    layout=None
)

st.title("AI Overviews Analysis Tool")
st.markdown("Analyze Google AI Overview results across keywords for brand analysis and competitor research.")

# Choose mode
route = st.radio(
    "Choose analysis mode:",
    ["Fetch Keywords", "Upload JSON"],
    captions=[
        "Live fetch with SEO API request",
        "Upload an available JSON file",
    ],
)

dataframe = None

if route == "Fetch Keywords":
    st.subheader("Live API Fetch")

    with st.form("keyword_form"):
        keywords_input = st.text_area(
            "Enter keywords (one per line or comma-separated):",
            placeholder="AI tools\nmachine learning\nartificial intelligence"
        )
        col1, col2 = st.columns(2)
        with col1:
            location_code = st.text_input("Location code (4 digits):", placeholder="2840")
        with col2:
            language_code = st.text_input("Language code:", placeholder="en")

        submit_button = st.form_submit_button("Fetch Data")

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

elif route == "Upload JSON":
    st.subheader("Upload JSON File")

    uploaded_file = st.file_uploader(
        "Choose a JSON file:",
        type=['json'],
        help="Upload a previously saved API result file"
    )

    if uploaded_file is not None:
        try:
            # Read the uploaded JSON file
            data = json.load(uploaded_file)
            dataframe = data
            st.success("JSON file loaded successfully")
            st.info(f"Loaded {len(dataframe) if isinstance(dataframe, list) else 'data'} records")
        except Exception as e:
            st.error(f"Error loading JSON file: {str(e)}")

# Analysis section
if dataframe is not None:
    st.subheader("Analysis Results")

    with st.form("analysis_form"):
        col1, col2 = st.columns(2)
        with col1:
            brand_name = st.text_input("Your brand name:", placeholder="OpenAI")
        with col2:
            brand_domain = st.text_input("Your brand domain:", placeholder="openai.com")

        analyze_button = st.form_submit_button("Analyze Data")

    if analyze_button and brand_name and brand_domain:
        with st.spinner("Analyzing data..."):
            try:
                # Debug: Show data structure info
                if isinstance(dataframe, pd.DataFrame):
                    st.info(f"Data info: DataFrame with {len(dataframe)} rows and columns: {list(dataframe.columns)}")
                    # Show a sample of the data structure
                    if not dataframe.empty:
                        st.json({"sample_data_structure": str(type(dataframe.iloc[0, 0]))})
                else:
                    st.info(f"Data info: {type(dataframe)} with {len(dataframe) if hasattr(dataframe, '__len__') else 'unknown'} items")

                # Pass the brand info as globals
                import builtins
                builtins.brand_name_input = brand_name
                builtins.brand_domain_input = brand_domain

                result = analyzeDataFrame(dataframe)

                if result is not None and isinstance(result, dict) and result.get('status') == 'success':
                    st.success("✅ Analysis completed successfully!")

                    # Display analysis summary
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Keywords Analyzed", result.get('keywords_analyzed', 0))
                    with col2:
                        st.metric("AI Overviews Found", result.get('ai_overviews_found', 0))
                    with col3:
                        st.metric("Competitors Identified", result.get('competitors_identified', 0))

                    # Get the DataFrames
                    keywords_df = result.get('keywords_df')
                    competitors_df = result.get('competitors_df')

                    # Display results in tabs
                    tab1, tab2 = st.tabs(["📊 Keywords Analysis", "🏢 Competitor Analysis"])

                    with tab1:
                        st.subheader("Keywords Analysis Results")
                        if keywords_df is not None and not keywords_df.empty:
                            # Show only readable format
                            display_df = keywords_df.drop(columns=['aio_references']) if 'aio_references' in keywords_df.columns else keywords_df
                            if 'aio_references_display' in display_df.columns:
                                display_df = display_df.rename(columns={'aio_references_display': 'aio_references'})

                            st.dataframe(display_df, use_container_width=True)

                            # Add explanation
                            st.info("💡 **Reference Format**: Numbers show citation ranking (1=first cited, 2=second, etc.) followed by domain")

                            # Download button
                            csv_keywords = keywords_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Keywords CSV",
                                data=csv_keywords,
                                file_name="keywords_analysis.csv",
                                mime="text/csv",
                                key="download_keywords"
                            )
                        else:
                            st.warning("No keywords data available")

                    with tab2:
                        st.subheader("Comprehensive Competitor Analysis")
                        if competitors_df is not None and not competitors_df.empty:
                            # Add explanation of the combined metrics
                            st.info("""
                            **Combined Analysis includes:**
                            - **Citations**: References in AI overview source lists
                            - **Mentions**: Brand name appearances in AI overview text content
                            - **Engagement Metrics**: Citation rates, mention rates, and domain analysis
                            """)

                            # Display key metrics
                            col1, col2, col3, col4 = st.columns(4)
                            with col1:
                                total_citations = competitors_df['cited_count'].sum()
                                st.metric("Total Citations", total_citations)
                            with col2:
                                total_mentions = competitors_df['mentioned'].sum()
                                st.metric("Total Mentions", total_mentions)
                            with col3:
                                avg_citation_rate = competitors_df['prompt_cited_rate'].mean()
                                st.metric("Avg Citation Rate", f"{avg_citation_rate:.1%}")
                            with col4:
                                avg_mention_rate = competitors_df['mention_rate'].mean()
                                st.metric("Avg Mention Rate", f"{avg_mention_rate:.1%}")

                            # Display the comprehensive dataframe
                            st.dataframe(competitors_df, use_container_width=True)

                            # Download button
                            csv_competitors = competitors_df.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Comprehensive Competitor Analysis CSV",
                                data=csv_competitors,
                                file_name="comprehensive_competitor_analysis.csv",
                                mime="text/csv",
                                key="download_competitors"
                            )
                        else:
                            st.warning("No competitor data available")

                    # Summary download - all files in one
                    st.subheader("📦 Download All Results")
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
                                label="📄 Download Analysis Summary",
                                data=summary_text,
                                file_name="analysis_summary.txt",
                                mime="text/plain",
                                key="download_summary"
                            )

                    with col2:
                        st.info("💡 **Tip**: Use the tabs above to explore each analysis result in detail.")

                else:
                    st.warning("Analysis completed but no results were generated. Check the error messages above.")

            except Exception as e:
                st.error(f"Unexpected error during analysis: {str(e)}")
                st.error("Please check your data format and try again.")

# Sidebar with instructions
with st.sidebar:
    st.header("Instructions")
    st.markdown("""
    **Step 1:** Choose your data source
    - **Fetch Keywords**: Use live API to get fresh data
    - **Upload JSON**: Use previously saved results

    **Step 2:** Configure your search
    - Enter keywords to analyze
    - Set location and language codes

    **Step 3:** Analyze results
    - Enter your brand name and domain
    - Generate comprehensive analysis reports

    **Location Codes:**
    - 2840: United States
    - 2826: United Kingdom
    - 2704: Vietnam

    **Language Codes:**
    - en: English
    - vi: Vietnamese
    """)

    st.header("Output Files")
    st.markdown("""
    - `keywords.csv`: Keyword analysis results
    - `competitor.csv`: Competitor citation analysis
    - `brand-mention-summary.csv`: Brand mention tracking
    """)