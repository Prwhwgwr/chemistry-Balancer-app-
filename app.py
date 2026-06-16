import streamlit as st
import pandas as pd
from chempy import balance_stoichiometry

# --- Page Configuration ---
st.set_page_config(page_title="🧪 Chemical Equation Balancer", page_icon="🧪", layout="centered")

# --- Hide Streamlit Branding ---
hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stDeployButton {display:none;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)

# --- 🛠️ DIRECT GOOGLE SHEET CONNECTOR (Python 3.14 Fix) 🛠️ ---
def read_google_sheet_direct():
    """Reads your public Google Sheet link via pandas to check voucher codes"""
    try:
        sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        if "/edit" in sheet_url:
            base_url = sheet_url.split("/edit")[0]
            csv_url = f"{base_url}/export?format=csv"
        else:
            csv_url = sheet_url
        df = pd.read_csv(csv_url)
        return df
    except Exception:
        st.error("⚠️ Database Sync Failed. Ensure secrets.toml has your spreadsheet link and it is set to public viewer access.")
        return None

# --- Initialize Core Session States ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "is_premium" not in st.session_state:
    st.session_state.is_premium = False
if "daily_balances" not in st.session_state:
    st.session_state.daily_balances = 0
if "history" not in st.session_state:
    st.session_state.history = []

# --- App Header ---
st.title("🧪 Chemical Equation Balancer")

# ==========================================
# PHASE 1: LOGIN PORTAL
# ==========================================
if not st.session_state.logged_in:
    st.write("### 🔑 Account Portal")
    st.write("Welcome! Please log in with a username or email to start tracking your daily limits.")
    
    user_input_name = st.text_input("Enter Username or Email ID:", placeholder="e.g., student123")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🚀 Enter Balancer App", type="primary", use_container_width=True):
            if user_input_name.strip():
                st.session_state.username = user_input_name.strip()
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Please enter a username or email to continue!")

# ==========================================
# PHASE 2: MAIN APPLICATION
# ==========================================
else:
    # --- SIDEBAR SYSTEM ---
    st.sidebar.markdown("### 👤 User Account Profile")
    st.sidebar.write(f"Logged in as: **{st.session_state.username}**")
    
    if st.session_state.is_premium:
        st.sidebar.markdown("👑 **Tier:** `PREMIUM ACCOUNT`")
        st.sidebar.caption("⏳ Unlimited usage active.")
    else:
        st.sidebar.markdown("💡 **Tier:** `FREE ACCOUNT`")
        st.sidebar.write(f"Daily Usage: **{st.session_state.daily_balances} / 5** equations used")

    if st.sidebar.button("🚪 Log Out", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.is_premium = False
        st.session_state.daily_balances = 0
        st.session_state.username = ""
        st.rerun()
        
    # --- TABS SYSTEM ---
    tab1, tab2 = st.tabs(["🎛️ Balancer Engine", "📜 History Log"])

    with tab1:
        # Premium Image Feature block
        if st.session_state.is_premium:
            st.markdown("### 📸 Premium Feature: Upload Equation Screenshot")
            uploaded_file = st.file_uploader("Upload an image of a chemical problem to scan:", type=["png", "jpg", "jpeg"])
            st.markdown("---")
        else:
            st.markdown("### 📸 Upload Equation Screenshot")
            st.warning("🔒 **Premium Feature Locked:** Free accounts cannot upload screenshots.")
            st.button("🚫 Upload Image (Premium Only)", disabled=True)
            st.markdown("---")

        st.write("Type your unbalanced chemical equation below:")
        user_input = st.text_input("Enter Reaction (Use '+' and '->'):", value="KMnO4 + HCl -> KCl + MnCl2 + H2O + Cl2")

        # Paywall is only triggered if a free account hits 5 daily uses
        paywall_blocked = False
        if not st.session_state.is_premium and st.session_state.daily_balances >= 5:
            paywall_blocked = True
            st.error("🛑 **Daily Limit Reached!** Free tier users are limited to 5 equations per day.")

        # ==========================================
        # ONE-TIME USE GAMING REDEEM PAYWALL WITH SOCIAL LINKS
        # ==========================================
        if paywall_blocked:
            st.markdown("""
                <div style="background-color:#1E1E24; padding:22px; border-radius:12px; border: 2px solid #00FF66; text-align:center; margin-top:15px; margin-bottom: 15px;">
                    <h2 style="color:#00FF66; margin-top:0;">👑 Unlock Unlimited Access</h2>
                    <p style="font-size:15px;">Daily free limit exhausted! To unlock unlimited balances and premium photo scanning, you need a voucher pin.</p>
                </div>
            """, unsafe_allow_html=True)
            
            st.markdown("### 🎟️ Don't have a code? Grab one here:")
            
            # Create two columns for your social link buttons
            btn_col1, btn_col2 = st.columns(2)
            
            with btn_col1:
                # 📢 REMINDER: Change '919876543210' to your real mobile number with country code!
                whatsapp_url = "https://wa.me/919876543210?text=Bro%20give%20me%20the%20premium%20balancer%20code"
                st.link_button("💬 Message on WhatsApp", whatsapp_url, use_container_width=True, type="secondary")
                st.caption("Text me directly to buy/request a personal code!")
                
            with btn_col2:
                # 📢 REMINDER: Change 'your_username' to your actual Insta handle!
                instagram_url = "https://instagram.com/your_username"
                st.link_button("📸 Follow on Instagram", instagram_url, use_container_width=True, type="secondary")
                st.caption("Check my stories/posts for daily code drops!")

            st.markdown("---")
            
            # The actual Code Input Box
            game_card_input = st.text_input("Enter 12-Digit One-Time Redeem Code:", placeholder="e.g., REDOX-7391-A").strip()
            
            if st.button("Redeem Premium Voucher Card", type="primary", use_container_width=True):
                if not game_card_input:
                    st.error("Please enter a code pin voucher first!")
                else:
                    df = read_google_sheet_direct()
                    if df is not None:
                        df.columns = [c.strip() for c in df.columns]
                        match = df[df['Code'].astype(str).str.strip() == game_card_input]
                        
                        if match.empty:
                            st.error("❌ Invalid Code Pin! This voucher code does not exist.")
                        else:
                            current_status = str(match.iloc[0]['Status']).strip().lower()
                            if current_status == "used":
                                st.error("⚠️ This code has already been redeemed!")
                            elif current_status == "unused":
                                st.session_state.is_premium = True
                                st.success("🎉 REDEEM SUCCESSFUL! Permanent Premium tier features activated.")
                                st.rerun()
            
        else:
            if st.button("Balance Equation", type="primary"):
                raw_input = user_input.strip()
                if not raw_input:
                    st.error("Please write an equation first!")
                else:
                    try:
                        reactants_side, products_side = raw_input.split("->")
                        reactants = set(formula.strip() for formula in reactants_side.split("+") if formula.strip())
                        products = set(formula.strip() for formula in products_side.split("+") if formula.strip())
                        
                        reac_coefficients, prod_coefficients = balance_stoichiometry(reactants, products)
                        reac_parts = [f"**{reac_coefficients[r]}** {r}" if reac_coefficients[r] > 1 else r for r in reactants]
                        prod_parts = [f"**{prod_coefficients[p]}** {p}" if prod_coefficients[p] > 1 else p for p in products]
                        balanced_result = " + ".join(reac_parts) + " &nbsp;&rarr;&nbsp; " + " + ".join(prod_parts)
                        
                        # Save historical items
                        history_entry = " + ".join([f"{reac_coefficients[r]} {r}" for r in reactants]) + "  →  " + " + ".join([f"{prod_coefficients[p]} {p}" for p in products])
                        st.session_state.history.insert(0, history_entry)

                        if not st.session_state.is_premium:
                            st.session_state.daily_balances += 1

                        st.success("### Balanced Successfully!")
                        st.markdown(f"<h3 style='color: #00FF66;'>{balanced_result}</h3>", unsafe_allow_html=True)
                    except Exception:
                        st.error("Could not balance equation. Check your formatting syntax.")

    with tab2:
        st.header("Previous Balances Log")
        if st.button("Clear History Log"):
            st.session_state.history = []
            st.rerun()
            
        if not st.session_state.history:
            st.info("No queries solved yet inside this active session.")
        else:
            for item in st.session_state.history:
                st.code(item, language="text")
# Create a clickable WhatsApp button with your number
whatsapp_number = "919123651311" # Added country code 91 for India
whatsapp_url = f"https://wa.me/{whatsapp_number}?text=Hi!%20I%20would%20like%20to%20get%20a%20premium%20balancer%20code."

st.link_button("💬 Contact Me on WhatsApp for premium access", whatsapp_url, use_container_width=True)