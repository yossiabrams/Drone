import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import requests
from streamlit_lottie import st_lottie
from googleapiclient.errors import HttpError

allowed_usernames = ["123", "evi", "ziv"]

st.set_page_config(
    page_title="ארון ציוד",
    page_icon="https://cdn-icons-png.flaticon.com/128/1013/1013307.png",
    # Replace with the URL or local file path of your icon
    layout="wide",
    initial_sidebar_state="expanded",  # or "collapsed"

)
# background_color = "#FDF0BF"
custom_style = """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300&display=swap');
        body {
            margin-top: 0;
            padding: 0;
            font-family: 'Open Sans', sans-serif;
            color: #6A4326; 
            font-family: 'Open Sans', sans-serif;
            direction: rtl !important;

        }
        h1 {
            color: #6A4326; /* Custom color for h1 */
            font-size: 36px;
            font-family: 'Open Sans', sans-serif;
        }
        h2 {
            color: #6A4326; /* Custom color for h2 */
            font-size: 24px;
            font-family: 'Open Sans', sans-serif;
        }
        p {
            font-size: 16px;
            font-family: 'Open Sans', sans-serif;
        }
        .stButton>button {
            color: #ffffff; /* Custom color for button text */
            background-color: #4F280B; /* Custom background color for button */
        }
        .stButton>button:hover {
            background-color: #7C614D; /* Custom background color for button on hover */
        }
    </style>
"""
st.markdown(custom_style, unsafe_allow_html=True)

json_keyfile_path = "key-sign-405213-52c8e94ac293.json"
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
spreadsheet_id = "1_v-rcNL39CJwpsqA-Wa5c6uO1iiAEGH4A4ce5cw4xvY"  # Replace with your actual spreadsheet ID

credentials = service_account.Credentials.from_service_account_file(
    json_keyfile_path, scopes=scopes
)

service = build("sheets", "v4", credentials=credentials)


def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def get_worksheet(product_type):
    try:
        service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        range_name = f"{product_type}!A:C"
        result = service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        values = result.get("values", [])
        return values
    except RefreshError as e:
        st.error(f"Error refreshing credentials: {e}")
        raise
    except HttpError as err:
        st.error(f"HTTP error occurred: {err.resp.status} - {err._get_reason()}")
        st.error(f"Error details: {err.content}")
        if err.resp.status == 403:
            st.error("Make sure the service account has the necessary permissions to access the spreadsheet.")
        elif err.resp.status == 404:
            st.error("Spreadsheet not found. Double-check the spreadsheet_id.")
        raise


def update_taken_status(product_type, product_name, product_number, username):
    try:
        product_data = get_worksheet(product_type)

        if any(item[0] == product_name and item[1] == product_number and item[2] == "Taken" for item in product_data if
               len(item) > 2):
            st.warning(f"המוצר:  {product_name} {product_number} is already taken.")
        else:
            matching_items = [(i, item) for i, item in enumerate(product_data) if
                              item and item[0] == product_name and item[1] == product_number]

            if matching_items:
                row_index, _ = matching_items[0]
                range_name = f"{product_type}!C{row_index + 1}"
                update_body = {"values": [[f"נלקח על ידי {username}"]]}
                service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name, body=update_body,
                                                       valueInputOption="RAW").execute()
                st.success(f"המוצר:' {product_name} {product_number}' מסומן כ  'נלקח על ידי {username}'")
            else:
                st.warning(f"המוצר  {product_name} {product_number} לא נמצא")

    except RefreshError as e:
        st.error(f"Error refreshing credentials: {e}")
        raise
def update_return_status(product_type, product_name, product_number, username):
    try:
        product_data = get_worksheet(product_type)

        matching_items = [(i, item) for i, item in enumerate(product_data) if
                          item and item[0] == product_name and item[1] == product_number]

        if matching_items:
            row_index, _ = matching_items[0]
            range_name = f"{product_type}!C{row_index + 1}"
            update_body = {"values": [[f"הוחזר על ידי {username}"]]}
            service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name, body=update_body,
                                                   valueInputOption="RAW").execute()
            st.success(f"המוצר:' {product_name} {product_number}' מסומן כ  'הוחזר על ידי {username}'")
        else:
            st.warning(f"המוצר {product_name} {product_number} לא קיים")

    except RefreshError as e:
        st.error(f"Error refreshing credentials: {e}")
        raise


hide_st_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

logo_path = "https://i.ibb.co/GcR8sGH/Digital-Systems-logo.png"
st.image(logo_path, use_column_width=False, width=85)

lottie = load_lottieurl("https://lottie.host/6e9b893f-3edc-4f6f-84b3-93b659348d26/ABvaiqZlRk.json")
st_lottie(lottie,height=300,key="cc")

st.title("ארון ציוד")
password = st.text_input(" הכנס את שם המשתמש:", type="password")

match password:
    case "123":
        username = "יוסי אברמס"
    case "evi":
        username = "אביתר כהן"
    case "ziv":
        username ="זיו"

product_types = ["רחפן", "סוללה", "מטען", "שלט"]

if password in allowed_usernames:
    for product_type in product_types:
        st.header(product_type)

        with st.spinner(f'טוען {product_type}...'):
            product_data = get_worksheet(product_type)

        unique_product_names = list(set(item[0] for item in product_data if item))
        product_numbers = [item[1] for item in product_data if item]

        selected_product_name = st.selectbox(f"בחר דגם {product_type}:", unique_product_names,
                                             key=f"{product_type}_product_name")

        selected_product_number = st.text_input(f"בחר מספר {product_type}:", key=f"{product_type}_product_number")


        if selected_product_name and selected_product_number:
            st.write(f"המוצר הנבחר: {selected_product_name} {selected_product_number}")
            if st.button(f"לקחת {product_type}"):
                update_taken_status(product_type, selected_product_name, selected_product_number, username)

            if st.button(f"להחזיר {product_type}"):
                update_return_status(product_type, selected_product_name, selected_product_number, username)


else:
    st.warning("Incorrect username. Access denied.")
st.markdown("""
    <div style="margin-top: 20px; padding: 20px;  color: #281100; text-align: center;">
        <p>פותח על ידי יוסי אברמס עבור 'חשיפה ודיגיטל' </p>
    </div>
""", unsafe_allow_html=True)
