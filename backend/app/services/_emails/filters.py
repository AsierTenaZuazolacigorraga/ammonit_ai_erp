def filters(msg, user, email):

    ##############################################################
    process = False
    # if msg.has_attachments:
    #     process=True

    ##############################################################
    if user.email == "asier.tena.zu@outlook.com":

        ##########################################################
        if email.email == "asier.tena.zu@outlook.com":
            if msg.has_attachments:
                process = True

    return process
