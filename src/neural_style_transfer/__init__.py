import streamlit as st
from filters import run_filter_1


# https://raw.githubusercontent.com/whitphx/streamlit-webrtc-example/main/app.py

def main():
    filter_1 = 'Filter 1'

    app_mode = st.sidebar.selectbox(
        "Choose a neural filter",
        [
            filter_1,
        ],
    )
    st.subheader(app_mode)

    if app_mode == filter_1:
        run_filter_1()
    else:
        pass  # do stuff


if __name__ == '__main__':
    main()
