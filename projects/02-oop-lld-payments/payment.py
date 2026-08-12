



def charge_payment(user_id: str, amount: int) -> None:
    """ 
        Here we are just using the user_id and the amount our system got and 
        printing the action to be performed
    """
    print(f"Charging user {user_id} amount {amount} using stripe")
