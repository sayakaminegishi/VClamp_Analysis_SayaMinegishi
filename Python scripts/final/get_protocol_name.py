#function to get the protol name. repeadely asks for user input if mistyped.

def get_protocol_name():
    valid_protocols = ["BradleyLong", "BradleyShort", "Henckels", "Okada"]
    while True:
        protocol_name = input("Enter the protocol name (BradleyLong, BradleyShort, Henckels, Okada): ")
        if protocol_name in valid_protocols:
            return protocol_name
        else:
            print("Invalid protocol name. Please try again.")
