import streamlit as st
from PIL import Image

# Mock Data
owned_nfts = [
    {
        "id": 1,
        "name": "VIP Club Access",
        "image": "https://via.placeholder.com/400x300",
        "description": "Exclusive access to premium clubs and events worldwide",
        "type": "Membership",
        "expiry_date": "2025-12-31",
        "benefits": [
            {"name": "Club Entry", "total": 10, "used": 4},
            {"name": "VIP Table", "total": 5, "used": 1},
        ],
    },
    {
        "id": 2,
        "name": "Elite Yacht Party Pass",
        "image": "https://via.placeholder.com/400x300",
        "description": "Access to exclusive yacht parties in top cities",
        "type": "Event Access",
        "expiry_date": "2025-06-30",
        "benefits": [
            {"name": "Yacht Event Entry", "total": 6, "used": 2},
            {"name": "Champagne Service", "total": 6, "used": 1},
        ],
    },
    {
        "id": 3,
        "name": "Luxury Travel Package",
        "image": "https://via.placeholder.com/400x300",
        "description": "Hours of private jet and luxury car rides included",
        "type": "Travel",
        "expiry_date": "2025-09-15",
        "benefits": [
            {"name": "Private Jet Hours", "total": 15, "used": 5},
            {"name": "Rolls Royce Rides", "total": 10, "used": 3},
        ],
    },
]

def display_nft_details(nft):
    st.subheader(nft["name"])
    st.image(nft["image"], width=400)
    st.write(nft["description"])
    st.write(f"Type: {nft['type']}")
    st.write(f"Expiry Date: {nft['expiry_date']}")

    st.write("### Benefits")
    for benefit in nft["benefits"]:
        st.write(
            f"- {benefit['name']}: {benefit['used']} used out of {benefit['total']}"
        )

# Streamlit App
st.title("NFT Dashboard")

# Tabs for "Your NFTs" and "Marketplace"
tab = st.selectbox("Select a tab", ["Your NFTs", "Marketplace"])

if tab == "Your NFTs":
    st.header("Your NFTs")
    for nft in owned_nfts:
        with st.container():
            col1, col2 = st.columns([1, 3])
            with col1:
                st.image(nft["image"], width=100)
            with col2:
                st.write(f"**{nft['name']}**")
                st.write(nft["description"])
                if st.button(f"View Details ({nft['name']})"):
                    display_nft_details(nft)
                    st.markdown("---")
else:
    st.header("Marketplace")
    st.write("Marketplace functionality will be added soon.")
