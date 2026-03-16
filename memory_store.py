<<<<<<< HEAD
conversation_memory={}

def save_context(user_id,intent):

    conversation_memory[user_id]=intent


def get_context(user_id):

    return conversation_memory.get(user_id)
=======
memory=[]

def save_context(q,a):

    memory.append({
    "question":q,
    "answer":a
    })

def get_context():

    return memory[-3:]  
>>>>>>> agent-v4
