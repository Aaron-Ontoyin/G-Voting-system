import streamlit as st
import pandas as pd

from database import Vote, engine
from sqlalchemy.orm import sessionmaker


st.set_page_config(page_title="Vote", page_icon=":tada:")
st.markdown(
    """
<style>
    header{visibility:hidden;}
    .main {
        margin-top: -90px;
        padding-top:10px;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""",
    unsafe_allow_html=True,
)


if "votes" not in st.session_state:
    st.session_state["votes"] = {
        "Yes": 0,
        "No": 0,
        "Partial": 0,
        "Indifferent": 0,
        "Other": 0,
    }
if "comments" not in st.session_state:
    st.session_state["comments"] = []
if "other" not in st.session_state:
    st.session_state["other"] = []


st.image(r"bg.webp", use_column_width=True)
st.markdown("""<h5 style="text-align: center;">GRIDCo Senior Staff Association Digital Platform</h5>""", unsafe_allow_html=True)
st.write()

valid_ids = pd.read_csv("staff_ids.csv")["Staffid"].astype(str).to_list()

content_placeholder = st.empty()
with content_placeholder.form(key="login_form"):
    st.text_input("Enter staff ID", key="staffID", type="password")
    st.form_submit_button("Proceed to vote")

staffID = st.session_state["staffID"]
if staffID and staffID not in valid_ids:
    st.error(f"Access Denied! Invalid ID", icon="❌")
    st.stop()

if not staffID:
    st.stop()

with st.spinner("Loading..."):
    Session = sessionmaker(bind=engine)
    session = Session()

if staffID == "admin00":
    pass
elif staffID in [v.staff_id for v in session.query(Vote).all()]:
    session.close()
    st.error(f"Access Denied! You have already voted!", icon="❌")
    st.stop()

content_placeholder.empty()
st.success(f"Access Granted!", icon="✅")

with st.form(key="vote_form"):
    placeholder_for_radio_select = st.empty()
    placeholder_for_other = st.empty()

    comment = st.text_area(
        "Comments (Optional)", placeholder="Enter comments here..."
    )
    submit_button = st.form_submit_button("Submit Vote")

with placeholder_for_radio_select:
    selection = st.radio(
        "In relation to the compensation structure, how do you prefer the consolidation of various elements? Please choose one of the following options:",
        (
            "Yes (I accept full consolidation of all the elements)",
            "No (there should be no consolidation at all)",
            "Partial Consolidation (I accept consolidation of the basic driven elements - basic salary, housing allowance, furnishing allowance, and leave allowance)",
            "Indifferent (whichever direction is fine with me).",
            "Other (State it)",
        ),
        index=4,
    )

with placeholder_for_other:
    if selection == "Other (State it)":
        otherOption = st.text_input("Enter your other option...")

if selection == "Other (State it)" and otherOption == "":
    st.warning("Please enter your other option")
    session.close()
    st.stop()

if submit_button:
    selection = (
        selection if selection != "Other (State it)" else f"Other - {otherOption}"
    )
    success, message = Vote.insert_vote(session, staffID, selection, comment)
    if success or staffID == "admin00":
        st.success(message)

        with st.spinner("Updating..."):
            try:
                db_votes = session.query(Vote).all()
            except:
                session.rollback()
                st.error("Failed to update results!")

            st.session_state["comments"] = [v.comment for v in db_votes if v.comment]
            st.session_state.votes = {
                "Yes": 0,
                "No": 0,
                "Partial": 0,
                "Indifferent": 0,
                "Other": 0,
            }
            for vote in db_votes:
                st.session_state.votes[vote.vote.split()[0]] += 1

            st.session_state.other = [
                vote.vote[8:] for vote in db_votes if vote.vote.startswith("Other")
            ]

        st.write("## Results")
        st.bar_chart(st.session_state.votes)

        with st.expander("Other Options"):
            for option in st.session_state["other"]:
                st.markdown(f"- {option}")

        with st.expander("Comments"):
            for comment in st.session_state["comments"]:
                st.markdown(f"- {comment}")
    else:
        st.warning(message)

session.close()
