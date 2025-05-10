from app.models import Client, User


def _join_clients(
    clients_clasification: str, client: Client, clasifier: str = ""
) -> str:
    if clasifier == "":
        clasifier = f"The order contains references to {client.name} company."
    return f"{clients_clasification}\n- {client.name}: {clasifier}"


def _get_clients_clasifier(user: User, clients: list[Client]) -> str:

    ##############################################################
    clients_clasification = ""
    for client in clients:

        ##############################################################
        if user.email == "asier.tena.zu@outlook.com":
            clients_clasification = _join_clients(clients_clasification, client)

            # ##########################################################
            # if client.name == "inola":
            #     clients_clasification = _join_clients(clients_clasification, client)

            # ##########################################################
            # if client.name == "matisa":
            #     clients_clasification = _join_clients(clients_clasification, client)

            # ##########################################################
            # ...

    return clients_clasification
