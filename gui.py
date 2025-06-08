import os 
import streamlit as st 
import db_func as func
import datetime

# This will get all the stock tickers from the database 
tick_retrival = func.get_tickers()
ticker_display = [ticker for ticker, _ in tick_retrival]
ticker_display.insert(0,"No Selection") # adds a no selection button to the options 

today = datetime.date.today()
end_date = today - datetime.timedelta(days=1)
portfolio_start_date = os.getenv("PORTFOILIO_STARTDATE")
portfolio_start_date = datetime.datetime.strptime(portfolio_start_date, "%Y-%m-%d").date()

def handle_date_input_change():
    date_input = st.session_state.get("date_input", None)
    if isinstance(date_input, tuple) and len(date_input) == 2:
        start, end = date_input
        if start > end: 
            st.warning ('Start date must be before the end date.')
            return 
        if start < portfolio_start_date:
            st.warning(f"Start date cannot be earlier than {portfolio_start_date}")

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

def load_stock():
    ticker = st.session_state.get("ticker_selectbox") # This gets the stock selection 
    if ticker is None or ticker == "No Selection":
        st.session_state["exchange"] = "None"
        return

    # Otherwise, find matching exchange
    for tick, exch in tick_retrival:
        if ticker == tick:
            st.session_state["exchange"] = exch # This controls the badge colour
            return


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
        on_change=handle_date_selection_change                           # this
    )   

    start_date, end_date = st.date_input(
        "",
        value=(datetime.date.today() - datetime.timedelta(days=30), datetime.date.today()),
        # value=st.session_state["date_input"],
        label_visibility="collapsed",
        key="date_input",
        on_change=handle_date_input_change
    )

    
    