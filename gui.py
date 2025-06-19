import os 
import streamlit as st 
import db_func as func
import pandas as pd 
import datetime
import plotly.express as px 

st.set_page_config(layout="wide")


# This will get all the stock tickers from the database 
tick_retrival = func.get_tickers()
ticker_display = [ticker for ticker, _ in tick_retrival]
ticker_display.insert(0,"No Selection") # adds a no selection button to the options 
# ticker = st.session_state.get("ticker_selectbox")
# summary = func.get_investment_summary(ticker)
# if ticker is None or ticker == "No Selection":
#     st.warning("Please select a ticker to view the investment summary.")
#     st.stop()

today = datetime.date.today()
end_date = today - datetime.timedelta(days=1)
portfolio_start_date = os.getenv("PORTFOILIO_STARTDATE")
portfolio_start_date = datetime.datetime.strptime(portfolio_start_date, "%Y-%m-%d").date()
default_range = (today - datetime.timedelta(days=30), today)

if "date_input" not in st.session_state:
    st.session_state["date_input"] = default_range

if "metrics" not in st.session_state:
    st.session_state["metrics"] = {}

if "graph_data" not in st.session_state:
    st.session_state["graph_data"] = pd.DataFrame()

def handle_date_input_change():
    date_input = st.session_state.get("date_input", None)
    if isinstance(date_input, tuple) and len(date_input) == 2:
        start, end = date_input
        if start > end: 
            st.warning ('Start date must be before the end date.')
            return 
        if start < portfolio_start_date:
            st.warning(f"Start date cannot be earlier than {portfolio_start_date}")
        
        load_stock()

    else:
        st.warning("Please select a valid date range.")

def handle_date_selection_change():
    date_selection = st.session_state.get("seg_selection", None)
    if date_selection =="1M":
        month = today - datetime.timedelta(days=30)
        st.session_state["date_input"] = (month,today)
    if date_selection =="3M":
        month = today - datetime.timedelta(days=90)
        st.session_state["date_input"] = (month,today)
    if date_selection =="1Y":
        month = today - datetime.timedelta(days=365)
        st.session_state["date_input"] = (month,today)
    if date_selection =="TOT":
        month = portfolio_start_date
        st.session_state["date_input"] = (month,today)
    load_stock()

def load_stock():
    ticker = st.session_state.get("ticker_selectbox") # This gets the stock selection 
    if ticker is None or ticker == "No Selection":
        st.session_state["exchange"] = "None"
        return

    # Otherwise, find matching exchange
    for tick, exch in tick_retrival:
        if ticker == tick:
            st.session_state["exchange"] = exch # This controls the badge colour
            break
 
    date1, date2 = st.session_state.get("date_input",{})
    summary = func.get_investment_summary(ticker, date1, date2)
 
    exhchange_state = st.session_state.get("exchange",{})
    if exhchange_state == "USD":
        cb = summary.usd_total
    else: 
        cb = summary.cad_total

    print(f"This is the percent {summary.port_percent}")

    # - put the information into the dict 
    st.session_state["metrics"] = {
        "Shares": summary.total_share,
        "CB": cb ,
        "Div": summary.total_div,
        "Percent": summary.port_percent,
    }

    graph_data = func.get_graph_date(ticker, date1, date2)

    st.session_state["graph_data"] = graph_data


                            #---------- Layout Config ----------#

# -------- LEFT COLUMN --------
col_left, col_right = st.columns([2, 1])  # Adjust width ratio as needed

with col_left: 
    badge_text = st.session_state.get("exchange", "None") # Gets session state and if nothing it will be None 
    title = st.session_state.get("ticker_selectbox", "Ticker") # if nothing present ticker 
    if badge_text == "Cad":
        badge_color = "#d62728"  # red
    elif badge_text == "USD":
        badge_color = "#1f77b4"  # blue
    elif badge_text == "None":
        badge_color = "#888888"  # grey for no selection
    else:
        badge_color = "#888888"

    # This is the spacing and format for the title, selection box and badge
    st.markdown(
            f"""
            <div style="display: flex; align-items: baseline;">
                <h1 style="margin-right: -15px;">{title}</h1>
                <span style="
                    background-color: {badge_color};
                    color: white;
                    padding: 3px 8px;
                    border-radius: 6px;
                    font-weight: bold;
                    font-size: 0.8em;
                    position: relative;
                    top: -7px;
                ">
                    {badge_text}
                </span>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("""
            <style>
                div[data-testid="stSelectbox"] {
                    margin-top: -57px;  /* Adjust this to control vertical spacing */
                }
            </style>
        """, unsafe_allow_html=True)  
     
    option_sb = st.selectbox(
            "",
            options=ticker_display,
            placeholder="No Selection",
            key="ticker_selectbox",
            on_change=load_stock
        )
    
# -------- RIGHT COLUMN --------
with col_right:
    st.markdown("""
        <style>
            .custom-wrapper {
                display: flex;
                flex-direction: column;
                gap: 0px !important;
            }
            div[data-testid="stDateInput"] {
                margin-top: -5px;  /* Move date picker higher */
            }
            div[data-testid="stSegmentedControl"] {
                margin-bottom: -20px;  /* Tighten space under buttons */
            }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="custom-wrapper">', unsafe_allow_html=True)
    options = ["1M", "3M", "1Y", "TOT"]
    selection = st.segmented_control(
        "Choose a stock",
        options,
        label_visibility="collapsed",
        default="TOT",
        key="seg_selection",
        on_change=handle_date_selection_change                           
    )   

    start_date, end_date = st.date_input(
        "",
        # value=(datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()),
        # value=st.session_state["date_input"],
        label_visibility="collapsed",
        key="date_input",
        on_change=handle_date_input_change
    )

# -------- METRICS -------- #
# shares, cost_basis, divd, percent = st.columns(4)   
# shares.metric("# of Shares", "1.345", border=True)
# cost_basis.metric("Cost Basis", "$1234.34", border=True)
# divd.metric("$ Dividends", "$1234.34", border=True)
# percent.metric("% of Portfolio", "23.34%", border=True)

sec_summary = st.session_state.get("metrics")

if sec_summary:
    shares, cost_basis, divd, percent = st.columns(4)

    shares.metric("# of Shares", f"{sec_summary.get('Shares', 'N/A')}", border=True)
    cost_basis.metric("Cost Basis", f"${sec_summary.get('CB', 0):,.2f}", border=True)
    divd.metric("$ Dividends", f"${sec_summary.get('Div', 0):,.2f}", border=True)
    percent.metric("% of Portfolio", f"{sec_summary.get('Percent', 'TBD')}", border=True)
else:
    st.warning("Please select a stock to view its summary.")






# -------- CHART  -------- #
g_coll1, gcol2 = st.columns([3,1])
graph_df = st.session_state.get("graph_data")
print(graph_df.head(5))
# Line Chart - Stock Prices Over Time
st.header("Stock Prices Over Time")

if not graph_df.empty and all(col in graph_df.columns for col in ["Date", "Adj_close"]):
    fig_line = px.line(
        graph_df,
        x="Date",
        y="Adj_close",
        title="Adjusted Close Over Time",
        markers=True
    )
    with g_coll1:
        st.plotly_chart(fig_line, use_container_width=True)


elif (
    st.session_state.get("ticker_selectbox") not in [None, "No Selection"]
    and isinstance(st.session_state.get("date_input"), tuple)
):
    with g_coll1:
        st.info("Loading chart data...")

else:
    with g_coll1:
        st.info("Chart will appear once stock data is loaded.")

with gcol2: 
    # These are place holders 
    st.metric(label="20D Moving Average", value=4, delta=-0.5, delta_color="inverse",border=True)

    st.metric(
        label="20D Volitialy ", value=123, delta=123, delta_color="off", border=True)
    st.metric(label="EXPO moving average", value=4, delta=-0.5, delta_color="inverse",border=True)

   