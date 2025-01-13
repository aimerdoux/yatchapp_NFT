# Required Dependencies
# Ensure you have the dependencies listed in requirements.txt installed.
# pip install streamlit
# pip install web3
# pip install passkit-generator

import streamlit as st
import json
from web3 import Web3
from passkit_generator import PassGenerator
import os

# Streamlit Interface
def main():
    st.title("Yacht Event NFT and Apple Wallet Pass Generator")

    # Input Metadata
    event_name = st.text_input("Event Name", "Luxury Yacht Party")
    event_date = st.date_input("Event Date")
    event_location = st.text_input("Event Location", "Miami Marina")
    qr_code_data = st.text_input("QR Code Data (URL)", "https://example.com/verify/nft")
    image_file = st.file_uploader("Upload Event Image", type=["jpg", "png", "webp"])

    # Ethereum/Polygon Settings
    wallet_address = st.text_input("Wallet Address", "0x...")
    rpc_provider = st.text_input("Polygon RPC URL", "https://polygon-mainnet.infura.io/v3/YOUR_PROJECT_ID")
    private_key = st.text_input("Private Key", type="password")
    contract_address = st.text_input("NFT Contract Address", "0x...")

    if st.button("Generate NFT and Wallet Pass"):
        if not all([event_name, event_date, event_location, qr_code_data, wallet_address, rpc_provider, private_key, contract_address]):
            st.error("Please fill in all required fields.")
        else:
            # Step 1: Generate NFT Metadata
            metadata = {
                "name": event_name,
                "description": f"Access to the exclusive {event_name}.",
                "image": "Uploaded image will be linked",
                "attributes": [
                    {"trait_type": "Event", "value": event_name},
                    {"trait_type": "Date", "value": str(event_date)},
                    {"trait_type": "Location", "value": event_location}
                ],
                "qrCodeData": qr_code_data
            }
            st.write("NFT Metadata:", metadata)

            # Step 2: Mint NFT
            try:
                web3 = Web3(Web3.HTTPProvider(rpc_provider))
                account = web3.eth.account.privateKeyToAccount(private_key)

                # Replace with your contract ABI
                contract_abi = ["function mint(address to, string memory tokenURI) public"]
                nft_contract = web3.eth.contract(address=Web3.toChecksumAddress(contract_address), abi=contract_abi)

                # Upload metadata (dummy link for now)
                token_uri = "https://example.com/metadata.json"
                tx = nft_contract.functions.mint(wallet_address, token_uri).buildTransaction({
                    'from': account.address,
                    'nonce': web3.eth.getTransactionCount(account.address),
                    'gas': 3000000,
                    'gasPrice': web3.toWei('20', 'gwei')
                })

                signed_tx = web3.eth.account.signTransaction(tx, private_key)
                tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
                st.success(f"NFT Minted Successfully! Transaction Hash: {web3.toHex(tx_hash)}")

            except Exception as e:
                st.error(f"Error minting NFT: {str(e)}")

            # Step 3: Generate Apple Wallet Pass
            try:
                pass_gen = PassGenerator(
                    pass_type_identifier="pass.com.yourdomain.yacht",
                    team_identifier="YOUR_TEAM_IDENTIFIER",
                    organization_name="Luxury Yacht Events",
                    description="Exclusive Yacht Event Ticket",
                    label_color="#FFD700",
                    foreground_color="#FFFFFF",
                    background_color="#003366"
                )

                pass_gen.add_field("event", "Event", event_name)
                pass_gen.add_field("location", "Location", event_location)
                pass_gen.add_field("date", "Date", str(event_date))
                pass_gen.add_qr_code(qr_code_data)

                if image_file:
                    pass_gen.add_image(image_file.getvalue(), "thumbnail")

                pass_file = pass_gen.create_pass(serial_number="12345")

                with open("LuxuryYachtEvent.pkpass", "wb") as f:
                    f.write(pass_file)

                st.success("Apple Wallet Pass Created Successfully! Download below:")
                st.download_button(
                    label="Download Pass", 
                    data=pass_file, 
                    file_name="LuxuryYachtEvent.pkpass", 
                    mime="application/vnd.apple.pkpass"
                )

            except Exception as e:
                st.error(f"Error generating wallet pass: {str(e)}")

if __name__ == "__main__":
    main()
