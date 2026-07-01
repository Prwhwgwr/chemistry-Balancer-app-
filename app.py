import streamlit as st
import streamlit.components.v1 as components
import extra_streamlit_components as stx
import datetime
import time
import os
import gspread
from chempy import balance_stoichiometry

# --- Page Configuration ---
# Sidebar is gone, so we set state to 'collapsed'
st.set_page_config(page_title="🧪 Chemical Equation Balancer", page_icon="🧪", layout="centered", initial_sidebar_state="collapsed")

# --- Hide Branding (No Sidebar needed) ---
hide_st_style = """
            <style>
            .stAppDeployButton {display:none !important;}
            .stDeployButton {display:none !important;}
            #MainMenu {display: none !important;}
            [data-testid="stViewerBadge"] {display: none !important;}
            footer {visibility: hidden !important;}
            /* Force hide the sidebar if it tries to exist */
            [data-testid="stSidebar"] {display: none !important;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 1. Initialize Cookie Manager ---
cookie_manager = stx.CookieManager(key="cookie_manager")

# --- Initialize Session States ---
if "is_premium" not in st.session_state:
    st.session_state.is_premium = False
if "daily_balances" not in st.session_state:
    st.session_state.daily_balances = 0
if "history" not in st.session_state:
    st.session_state.history = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- 2. Check for existing cookies EVERY run ---
saved_user = cookie_manager.get(cookie="saved_username")

if saved_user is not None and saved_user != "":
    st.session_state.logged_in = True
    st.session_state.username = saved_user

st.title("🧪 Chemical Equation Balancer")

# --- PHASE 1: LOGIN PORTAL ---
if not st.session_state.logged_in:
    st.write("### 🔑 Account Portal")
    with st.form(key="login_form"):
        user_input_name = st.text_input("Enter Username:")
        keep_signed_in = st.checkbox("Keep me signed in")
        submit_button = st.form_submit_button("🚀 Enter Balancer App")
        
        if submit_button:
            if user_input_name.strip():
                st.session_state.username = user_input_name.strip()
                st.session_state.logged_in = True
                
                if keep_signed_in:
                    expire_date = datetime.datetime.now() + datetime.timedelta(days=30)
                    cookie_manager.set("saved_username", user_input_name.strip(), expires_at=expire_date)
                    
                st.success("🚀 Login successful! Redirecting...")
                components.html("""<script>setTimeout(function() { window.parent.location.reload(); }, 1500);</script>""", height=0)
                st.stop()
            else:
                st.error("Please enter a username!")

# --- PHASE 2: APP INTERFACE ---
if st.session_state.logged_in:
    st.write(f"### 👋 Welcome, {st.session_state.username}")
    
    tab1, tab2, tab3 = st.tabs(["🎛️ Balancer", "📜 History", "ℹ️ Help & Premium"])

    with tab1:
        if not st.session_state.is_premium:
            st.write(f"Daily Usage: {st.session_state.daily_balances} / 5")
            
        user_input = st.text_input("Enter Equation (Reactants -> Products):", value="KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2")

        if st.button("Balance Equation"):
            if not st.session_state.is_premium and st.session_state.daily_balances >= 5:
                st.error("🛑 Daily Limit Reached! Upgrade in the 'Help & Premium' tab.")
            else:
                try:
                    reac_side, prod_side = user_input.split("->")
                    reactants = set(f.strip() for f in reac_side.split("+") if f.strip())
                    products = set(f.strip() for f in prod_side.split("+") if f.strip())
                    reac_c, prod_c = balance_stoichiometry(reactants, products)
                    res = " + ".join([f"{reac_c[r]} {r}" for r in reactants]) + " → " + " + ".join([f"{prod_c[p]} {p}" for p in products])
                    
                    st.session_state.history.insert(0, res)
                    if not st.session_state.is_premium:
                        st.session_state.daily_balances += 1
                    st.success(f"Balanced: {res}")
                except Exception as e:
                    st.error("Format Error! Use '+' between compounds and '->' in the middle.")

    with tab2:
        for item in st.session_state.history:
            st.code(item)

    with tab3:
        st.markdown("### ℹ️ Account & Premium")
        
        # --- LOGOUT BUTTON MOVED HERE ---
        if st.button("🚪 Log Out"):
            cookie_manager.delete("saved_username")
            st.session_state.logged_in = False
            st.session_state.username = ""
            components.html("""<script>setTimeout(function() { window.parent.location.reload(); }, 1000);</script>""", height=0)
            st.stop()
            
        st.markdown("---")
        st.markdown("### 📖 How to Use")
        st.write("1. **Enter Equation:** Use '+' for chemicals and '->' to separate reactants/products.")
        st.write("2. **Example:** `H2 + O2 -> H2O`")
        st.write("3. **Free Tier:** Limited to 5 balances per day.")
        
        st.markdown("---")
        st.markdown("### 👑 Unlock Premium (Unlimited)")
        st.link_button("💬 Contact Me on WhatsApp", "https://wa.me/919123651311?text=Hi!%20I%20want%20to%20buy%20a%20premium%20balancer%20code.")
        
        code = st.text_input("Enter 8-Digit Redeem Code:")
        
        if st.button("Redeem Code"):
            if code.strip() == "":
                st.error("Please enter a code first!")
            else:
                with st.spinner("Checking database..."):
                    try:
                        if os.path.exists('secrets.json'):
                            gc = gspread.service_account(filename='secrets.json')
                        else:
                            credentials = dict(st.secrets["gcp_service_account"])
                            gc = gspread.service_account_from_dict(credentials)
                            
                        sh = gc.open("App Gift cards")
                        worksheet = sh.sheet1
                        cell = worksheet.find(code.strip())
                        
                        if cell and worksheet.cell(cell.row, 2).value.lower() == "unused":
                            worksheet.update_cell(cell.row, 2, 'used')
                            worksheet.update_cell(cell.row, 3, st.session_state.username)
                            st.session_state.is_premium = True
                            st.success("🎉 Premium Activated!")
                            time.sleep(2); st.rerun() 
                        else:
                            st.error("❌ Invalid or already used code.")
                    except Exception as e:
                        st.error("Database error.")

# --- FOOTER ---
st.markdown("---")
st.markdown("<center>CREATED BY ♥ PRANEEL BANERJEE</center>", unsafe_allow_html=True)
