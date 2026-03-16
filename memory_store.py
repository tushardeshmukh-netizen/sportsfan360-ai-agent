<<<<<<< HEAD
conversation_memory={}

def save_context(user_id,intent):

    conversation_memory[user_id]=intent


def get_context(user_id):

=======
conversation_memory={}

def save_context(user_id,intent):

    conversation_memory[user_id]=intent


def get_context(user_id):

>>>>>>> 7a1f20c (UI update)
    return conversation_memory.get(user_id)