import streamlit as st
from google.oauth2 import service_account
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError
import requests
from streamlit_lottie import st_lottie
from PIL import Image

# page_style = """
#     <style>
#     [data-testid="stAppViewContainer"]{
#     background-color:red;
#
#     }
#
#     </style>
# """
# st.markdown(page_style, unsafe_allow_html=True)
# Define the allowed usernames
allowed_usernames = ["yossi", "edi"]

st.set_page_config(
    page_title="ארון ציוד",
    page_icon="https://cdn-icons-png.flaticon.com/128/1013/1013307.png",  # Replace with the URL or local file path of your icon
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

# Connect to Google Sheets
json_keyfile_path = "key-sign-405213-52c8e94ac293.json"
scopes = ["https://www.googleapis.com/auth/spreadsheets"]
spreadsheet_id = "1_v-rcNL39CJwpsqA-Wa5c6uO1iiAEGH4A4ce5cw4xvY"  # Replace with your actual spreadsheet ID

# Load credentials
credentials = service_account.Credentials.from_service_account_file(
    json_keyfile_path, scopes=scopes
)

# Build the Sheets API client
service = build("sheets", "v4", credentials=credentials)

def load_lottieurl(url):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()
def get_worksheet(product_type):
    try:
        # Make a dummy request to force token refresh if needed
        service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        range_name = f"{product_type}!A:C"
        return service.spreadsheets().values().get(spreadsheetId=spreadsheet_id, range=range_name).execute().get(
            "values", [])
    except RefreshError as e:
        st.error(f"Error refreshing credentials: {e}")
        raise


def update_taken_status(product_type, product_name, product_number, username):
    try:
        # Retrieve the data for the selected product type
        product_data = get_worksheet(product_type)

        # Check if the product is already taken
        if any(item[0] == product_name and item[1] == product_number and item[2] == "Taken" for item in product_data if len(item) > 2):
            st.warning(f"המוצר:  {product_name} {product_number} is already taken.")
        else:
            # Find the row index of the product_name and product_number
            matching_items = [(i, item) for i, item in enumerate(product_data) if item and item[0] == product_name and item[1] == product_number]

            if matching_items:
                # Update the 'Taken' status and username in column C for the first matching item
                row_index, _ = matching_items[0]
                range_name = f"{product_type}!C{row_index + 1}"
                update_body = {"values": [[f"Taken by {username}"]]}
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
        # Retrieve the data for the selected product type
        product_data = get_worksheet(product_type)

        # Find the row index of the product_name and product_number
        matching_items = [(i, item) for i, item in enumerate(product_data) if item and item[0] == product_name and item[1] == product_number]

        if matching_items:
            # Update the 'Returned' status and username in column C for the first matching item
            row_index, _ = matching_items[0]
            range_name = f"{product_type}!C{row_index + 1}"
            update_body = {"values": [[f"Returned by {username}"]]}
            service.spreadsheets().values().update(spreadsheetId=spreadsheet_id, range=range_name, body=update_body,
                                                   valueInputOption="RAW").execute()
            st.success(f"המוצר:' {product_name} {product_number}' מסומן כ  'הוחזר על ידי {username}'")
        else:
            st.warning(f"המוצר {product_name} {product_number} לא קיים")

    except RefreshError as e:
        st.error(f"Error refreshing credentials: {e}")
        raise



# Streamlit app


hide_st_style = """
            <style>
            MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


# script_directory = os.path.dirname(os.path.abspath(__file__))
# logo_path = Image.open(os.path.join(script_directory, "Digital_Systems_logo.png"))

# st.image(logo_path, use_column_width=False, width=50)

lottie = load_lottieurl("https://lottie.host/6e9b893f-3edc-4f6f-84b3-93b659348d26/ABvaiqZlRk.json")


st_lottie(lottie,height=300,key="cc")


st.title("              ארון ציוד         ")
password = st.text_input(" הכנס את שם המשתמש:", type="password")

# Product Types
product_types = ["רחפן", "סוללה", "מטען", "שלט"]


# Check if the password is in the list of allowed usernames
if password in allowed_usernames:
    # Display sections for each product type
    for product_type in product_types:
        st.header(product_type)

        # Retrieve product data for the selected product type
        product_data = get_worksheet(product_type)

        # Extract unique product names and product numbers
        unique_product_names = list(set(item[0] for item in product_data if item))
        product_numbers = [item[1] for item in product_data if item]

        # Create a dropdown for unique product names
        selected_product_name = st.selectbox("בחר דגם רחפן:", unique_product_names, key=f"{product_type}_product_name")

        # Create an edit line to select the product number
        selected_product_number = st.text_input("בחר מספר רחפן:", key=f"{product_type}_product_number")

        # Display selected product
        if selected_product_name and selected_product_number:
            st.write(f"המוצר הנבחר: {selected_product_name} {selected_product_number}")

            # Add a button to mark the product as 'Taken'
            if st.button(f"לקחת {product_type}"):
                update_taken_status(product_type, selected_product_name, selected_product_number, password)

            # Add a button to mark the product as 'Returned'
            if st.button(f"להחזיר {product_type}"):
                update_return_status(product_type, selected_product_name, selected_product_number, password)
else:
    st.warning("Incorrect username. Access denied.")
